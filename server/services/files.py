import csv
import datetime
import io
import json
import uuid
from pathlib import Path

import requests
from spyne import rpc, String, ByteArray
from spyne.error import (
    RequestTooLongError,
    ArgumentError,
    ResourceNotFoundError,
)
from spyne.model.binary import _FileValue
from spyne.service import Service
from sqlalchemy import desc
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
from core.db.models import User, File, SessionLocal
from core.schemas.jwt import AuthHeader
from core.security import authenticate_user


# noinspection PyMethodParameters
class FileService(Service):
    __in_header__ = AuthHeader

    # --------------- File Uploading --------------- #

    @rpc(
        String(
            min_occurs=1,
            nillable=False,
        ),  # filename
        ByteArray(
            min_occurs=1,
            nillable=False,
        ),  # cid (=> content: bytes
        # from MTOM)
        _returns=String(
            min_occurs=1,
            nillable=False,
        ),  # Here should be _mtom=True but sometimes it corrupts outcoming
        # envelope so in the last closing tag it looks like '</soap1' :/
        # Anyway Spyne converts MTOM attachments by their CID and MIMES to
        # base64 before proceeding the request even without _mtom=True.
    )
    def upload_file(ctx: Service, filename: str, content: tuple[bytes]):
        user: User = authenticate_user(ctx)

        # Проверки входного файла
        file_content = FileService._validate_file(filename, content)

        # Проверка свободного места в пользовательской директории
        user_dir = UPLOADS_DIR / str(user.id)
        FileService._check_directory_space(user_dir, file_content)

        # Генерация уникального идентификатора
        uid = uuid.uuid4().hex

        # Асинхронная запись файла
        defer.execute(
            FileService._async_write_file,
            user.id,
            filename,
            file_content,
            uid,
            user_dir,
        )

        return (
            f"File '{filename}' currently uploading. You can check upload "
            f"status at /upload/{uid}."
        )

    @staticmethod
    def _validate_file(filename: str, content: tuple[bytes]) -> bytes:
        if not content:
            log.msg("[FILECHECK.LEN] File length is 0.")
            raise ArgumentError("File size should be more than zero bytes.")

        file_content = content[0]

        if len(file_content) > MAX_FILE_SIZE:
            log.msg(
                f"[FILECHECK.LEN] File length exceeds {MAX_FILE_SIZE:_} bytes."
            )
            raise RequestTooLongError(
                f"File size should be less than {MAX_FILE_SIZE:_} bytes."
            )

        if "ж" in filename.lower():
            log.msg("[FILECHECK.NAME] File name contains 'ж'.")
            raise ArgumentError("Filename can't contain 'ж' in any case.")

        if FileService._is_json_content(file_content):
            log.msg("[FILECHECK.JSON] File contains valid JSON.")
            raise ArgumentError("File consists of json data.")

        return file_content

    @staticmethod
    def _is_json_content(content: bytes) -> bool:
        try:
            json.loads(content.decode("utf-8"))
            return True
        except Exception:
            return False

    @staticmethod
    def _check_directory_space(user_dir: Path, file_content: bytes) -> None:
        user_dir.mkdir(parents=True, exist_ok=True)
        current_size = sum(
            f.stat().st_size for f in user_dir.glob("**/*") if f.is_file()
        )
        total_size = current_size + len(file_content)

        if total_size > MAX_USER_DIR_SIZE:
            log.msg(
                f"[USERDIR] Directory size limit exceeded. Max: "
                f"{MAX_USER_DIR_SIZE:_} bytes, Current: {current_size:_} "
                f"bytes, File: {len(file_content):_} bytes."
            )
            raise ArgumentError(
                f"Adding this file will exceed the directory size limit of "
                f"{MAX_USER_DIR_SIZE:_} bytes."
            )

    @staticmethod
    @defer.inlineCallbacks
    def _async_write_file(
        user_id: int, filename: str, content: bytes, uid: str, user_dir: Path
    ) -> None:
        clock: IReactorTime = IReactorTime(reactor)

        filepath = FileService._resolve_file_conflict(user_dir, filename)
        temp_file = FileService._create_temp_file(user_dir, uid, len(content))

        try:
            yield FileService._write_file_in_chunks(
                filepath, content, temp_file, uid, clock
            )
            FileService._save_file_to_db(user_id, filepath, uid)
        except Exception as e:
            log.msg(f"[DEFERRED:{uid}] Error during file upload: {e}")
            raise
        finally:
            FileService._cleanup_temp_file(temp_file, uid)

    @staticmethod
    def _resolve_file_conflict(user_dir: Path, filename: str) -> Path:
        filepath = user_dir / filename
        base_name, ext = filepath.stem, filepath.suffix
        counter = 1

        suffixed: bool = False
        while filepath.exists():
            filepath = user_dir / f"{base_name} ({counter}){ext}"
            suffixed = True
            counter += 1

        if suffixed:
            log.msg(
                f"[DEFERRED] File with name '{filename}' already exists. "
                f"Renaming to '{filepath.name}'."
            )

        return filepath

    @staticmethod
    def _notify_upload_progress(
        uid: str,
        filename: str,
        uploaded: int,
        total: int,
    ) -> None:
        progress = {
            "uid": uid,
            "filename": filename,
            "uploaded": uploaded,
            "total": total,
        }
        try:
            requests.post(
                f"http://localhost:7999/upload/{uid}",
                json=progress,
            )
        except Exception as e:
            log.msg(f"[NOTIFY] Failed to notify client: {e}")

    @staticmethod
    def _create_temp_file(user_dir: Path, uid: str, size: int) -> Path:
        temp_file = user_dir / f"{uid}.tmp"
        with open(temp_file, "wb") as temp:
            temp.truncate(size)

        log.msg(
            f"[DEFERRED:{uid}] Temporary file '{temp_file.name}' created to "
            f"reserve {size:_} bytes."
        )
        return temp_file

    @staticmethod
    @defer.inlineCallbacks
    def _write_file_in_chunks(
        filepath: Path,
        content: bytes,
        temp_file: Path,
        uid: str,
        clock: IReactorTime,
    ) -> None:
        total_size = len(content)
        n_chunks = min(5, total_size)  # 5 чанков, если всего >= 5 байт
        chunk_size = total_size // n_chunks
        uploaded = 0

        with open(filepath, "wb") as f:
            for i in range(n_chunks):
                start = i * chunk_size
                end = start + chunk_size if i < n_chunks - 1 else total_size
                chunk = content[start:end]

                f.write(chunk)
                uploaded += len(chunk)

                if (fname := filepath.stem) != "nevernotify" and (
                    fext := filepath.suffix
                ) != ".me":
                    FileService._notify_upload_progress(
                        uid=uid,
                        filename=f"{fname}{fext}",
                        uploaded=uploaded,
                        total=total_size,
                    )

                with open(temp_file, "r+b") as temp:
                    temp.truncate(total_size - uploaded)

                log.msg(
                    f"[DEFERRED:{uid}] Upload progress: {uploaded:_} / "
                    f"{total_size:_} bytes. Reserved size adjusted to "
                    f"{total_size - uploaded:_} bytes."
                )

                yield deferLater(clock, DEFER_DELAY)

        log.msg(
            f"[DEFERRED:{uid}] File '{filepath.name}' written successfully."
        )

    @staticmethod
    def _cleanup_temp_file(temp_file: Path, uid: str) -> None:
        if temp_file.exists():
            temp_file.unlink()
            log.msg(
                f"[DEFERRED:{uid}] Temporary file '{temp_file.name}' removed."
            )

    @staticmethod
    def _save_file_to_db(user_id: int, filepath: Path, uid: str) -> None:
        session = SessionLocal()

        try:
            session.add(
                File(
                    user_id=user_id,
                    filename=filepath.name,
                    upload_time=datetime.datetime.utcnow(),
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

    # ---------------------------------------------- #

    @rpc(_returns=_FileValue.customize(min_occurs=1))
    def get_last_uploaded_file(ctx: Service):
        user: User = authenticate_user(ctx)

        if last_file := (
            ctx.udc.session.query(File)
            .filter(File.user_id == user.id)
            .order_by(desc(File.upload_time))
            .first()
        ):
            return last_file

        raise ResourceNotFoundError(
            fault_object=user.username,
            fault_string="No files found for user %r.",
        )

    @rpc(_returns=_FileValue)
    def get_all_files_csv(ctx: Service):
        authenticate_user(ctx)

        files: list[File] = ctx.udc.session.query(File).all()

        if not files:
            raise ResourceNotFoundError(
                fault_object=[],
                fault_string="No files found. Files: %r",
            )

        # Создание CSV в памяти
        output = io.StringIO()
        writer = csv.writer(output, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            (
                "Id",
                "UserId",
                "Filename",
                "UploadTime",
            )
        )

        for file in files:
            writer.writerow(
                (
                    file.id,
                    file.user_id,
                    file.filename,
                    file.upload_time,
                )
            )

        csv_data = output.getvalue()
        csv_bytes = csv_data.encode("utf-8")

        return _FileValue(
            name="uploads.csv",
            type="text/csv",
            data=csv_bytes,
        )
