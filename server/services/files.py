import datetime
import json
import uuid
from pathlib import Path

from spyne import rpc, String, ByteArray
from spyne.error import RequestTooLongError, ArgumentError
from spyne.service import Service
from twisted.internet import defer, reactor
from twisted.internet.interfaces import IReactorTime
from twisted.internet.task import deferLater
from twisted.python import log

from core.config import (
    UPLOADS_DIR,
    MAX_FILE_SIZE,
    MAX_USER_DIR_SIZE,
    DEFER_DELAY,
)
from core.db.models import User
from core.schemas.jwt import AuthHeader
from core.security import get_current_auth_user


# noinspection PyMethodParameters
class FileService(Service):
    __in_header__ = AuthHeader

    @rpc(
        String(),  # filename
        ByteArray(),  # cid (=> content: bytes from MTOM)
        _returns=String(min_occurs=1),
        # Here should be _mtom=True but sometimes it corrupts outcoming
        # envelope so in the last closing tag it looks like '</soap1' :/
        # Anyway Spyne converts MTOM attachments by their CID and MIMES to
        # base64 before proceeding the request.
    )
    def upload_file(ctx: Service, filename: str, content: tuple[bytes]):
        try:
            user: User = get_current_auth_user(
                ctx,
                ctx.in_header.Authorization if ctx.in_header else None,  # noqa
            )
        except Exception:
            raise

        # Файл нулевой длины
        if content is None:
            log.msg("[FILECHECK.LEN] File length is 0.")
            raise ArgumentError("File size should be more than zero bytes.")
        # Файл превышает 3 Мб
        elif len(file_content := content[0]) > MAX_FILE_SIZE:
            log.msg(
                f"[FILECHECK.LEN] File length exceeds {MAX_FILE_SIZE:_} bytes."
            )
            raise RequestTooLongError(
                f"File size should be less than {MAX_FILE_SIZE} bytes."
            )
        # Имя файла содержит букву 'ж'
        elif "ж" in filename.lower():
            log.msg("[FILECHECK.NAME] File name contains 'ж'.")
            raise ArgumentError("Filename can't contain 'ж' in any case.")

        # В файле только валидный JSON
        json_inside: bool = True
        try:
            json.loads(file_content.decode("utf-8"))
        except Exception as e:
            log.msg(f"[FILECHECK.JSON] {e}")
            json_inside = False
        finally:
            if json_inside:
                log.msg("[FILECHECK.JSON] Json inside -> skipping.")
                raise ArgumentError("File consists of json data")

        # Проверка свободного места
        user_dir: Path = UPLOADS_DIR / str(user.id)
        user_dir.mkdir(parents=True, exist_ok=True)
        current_size = sum(  # Рекурсивное вычисление размера папки
            f.stat().st_size for f in user_dir.glob("**/*") if f.is_file()
        )
        ttl_f_size = len(file_content)
        if current_size + ttl_f_size > MAX_USER_DIR_SIZE:
            log.msg(
                f"[USERDIR:{user.id}] Directory size limit exceeded. "
                f"Max size: {MAX_USER_DIR_SIZE:_} bytes, Current size: "
                f"{current_size:_} bytes, File size: {ttl_f_size:_} bytes."
            )
            raise ArgumentError(
                f"Adding this file will exceed the directory size limit of "
                f"{MAX_USER_DIR_SIZE:_} bytes."
            )

        uid: str = uuid.uuid4().hex
        defer.execute(
            FileService._async_write_file,
            user.id,  # user_id
            filename,  # filename
            file_content,  # content
            uid,  # uid
            user_dir,  # user_dir
            ttl_f_size,  # ttl_size
        )

        return str(
            f"File '{filename}' currently uploading. You can check "
            f"upload status at /upload/{uid}."
        )

    @staticmethod
    @defer.inlineCallbacks
    def _async_write_file(
        user_id: int,
        filename: str,
        content: bytes,
        uid: str,
        user_dir: Path,
        ttl_size: int,
    ) -> None:
        # TODO: Корнер кейс с тайм-аутом

        clock: IReactorTime = IReactorTime(reactor)

        # Проверка конфликта имени файла
        filepath: Path = user_dir / filename
        base_name, ext = filepath.stem, filepath.suffix
        counter: int = 1
        while filepath.exists():
            filepath = user_dir / f"{base_name} ({counter}){ext}"
            counter += 1

        # Создание временного файла для резервирования места
        temp_file: Path = user_dir / f"{uid}.tmp"
        with open(temp_file, "wb") as temp:
            temp.truncate(ttl_size)
        log.msg(
            f"[DEFERRED:{uid}] Temporary file '{temp_file.name}' created to "
            f"reserve {ttl_size:_} bytes."
        )

        # Асинхронная запись файла
        n_chunks: int = 10 if ttl_size >= 10 else ttl_size
        chunk_size: int = ttl_size // n_chunks
        uploaded: int = 0

        try:
            # Запись файла чанками с задержкой
            with open(filepath, "wb") as f:
                for i in range(n_chunks):
                    start = i * chunk_size
                    end = start + chunk_size if i < n_chunks - 1 else ttl_size
                    chunk = content[start:end]

                    f.write(chunk)
                    uploaded += len(chunk)

                    # Уменьшение размера временного файла
                    with open(temp_file, "r+b") as temp:
                        temp.truncate(ttl_size - uploaded)

                    log.msg(
                        f"[DEFERRED:{uid}] Upload progress: {uploaded:_} / "
                        f"{ttl_size:_} bytes. Reserved size adjusted to "
                        f"{ttl_size - uploaded:_} bytes."
                    )

                    yield deferLater(clock, DEFER_DELAY)

            log.msg(
                f"[DEFERRED:{uid}] File '{filepath.name}' written "
                f"successfully."
            )

        except Exception as e:
            log.msg(f"[DEFERRED:{uid}] Error during file upload: {e}")
            raise
        finally:
            # Удаление временного файла
            if temp_file.exists():
                temp_file.unlink()
                log.msg(
                    f"[DEFERRED:{uid}] Temporary file '{temp_file.name}' "
                    f"removed."
                )

        # Запись в БД
        from core.db.models import SessionLocal, File

        session = SessionLocal()
        try:
            session.add(
                File(
                    user_id=user_id,
                    filename=filepath.name,  # Сохраняем итоговое имя файла
                    upload_time=datetime.datetime.utcnow(),  # noqa
                )
            )
            session.commit()
            log.msg(
                f"[DEFERRED:{uid}] File '{filepath.name}' successfully saved "
                f"to DB."
            )
        except Exception as e:
            log.msg(f"[DEFERRED:{uid}] Error while saving file to DB: {e}")
        finally:
            session.close()
