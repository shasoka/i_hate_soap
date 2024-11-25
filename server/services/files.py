import datetime
import json
from pathlib import Path

from spyne import rpc, String, ByteArray
from spyne.error import RequestTooLongError, ArgumentError
from spyne.service import Service
from twisted.internet import defer, reactor
from twisted.internet.interfaces import IReactorTime
from twisted.internet.task import deferLater
from twisted.python import log

from core.config import UPLOADS_DIR, MAX_FILE_SIZE
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

        # Проверки по заданию
        if content is None:
            log.msg("[FILECHECK.LEN] File length is 0.")
            raise ArgumentError("File size should be more than zero bytes.")
        elif len(file_content := content[0]) > MAX_FILE_SIZE:
            log.msg(
                f"[FILECHECK.LEN] File length exceeds {MAX_FILE_SIZE} bytes."
            )
            raise RequestTooLongError(
                f"File size should be less than {MAX_FILE_SIZE} bytes."
            )
        elif "ж" in filename.lower():
            log.msg("[FILECHECK.NAME] File name contains 'ж'.")
            raise ArgumentError("Filename can't contain 'ж' in any case.")

        json_inside: bool = True
        try:
            json.loads(file_content.decode("utf-8"))
        except Exception as e:
            log.msg(f"[FILECHECK.JSON] {e}")
            json_inside = False
        finally:
            if json_inside:
                raise ArgumentError("File consists of json data")

        defer.execute(
            FileService._async_write_file, user.id, filename, content
        )

        return str(
            f"File '{filename}' currently uploading. You can check "
            f"upload status at /upload."
        )

    @staticmethod
    @defer.inlineCallbacks
    def _async_write_file(
        user_id: int,
        filename: str,
        content: tuple[bytes],
    ) -> None:
        clock: IReactorTime = IReactorTime(reactor)

        content: bytes = content[0]
        filepath: Path = UPLOADS_DIR / filename
        ttl_size: int = len(content)
        n_chunks: int = 10 if ttl_size >= 10 else ttl_size
        chunk_size: int = ttl_size // n_chunks
        uploaded: int = 0

        # Запись файла чанками с задержкой
        with open(filepath, "wb") as f:
            for i in range(n_chunks):
                start = i * chunk_size
                end = start + chunk_size if i < n_chunks - 1 else ttl_size
                chunk = content[start:end]

                f.write(chunk)
                uploaded += len(chunk)

                log.msg(
                    f"[DEFERRED] Upload progress: {uploaded}/{ttl_size} bytes."
                )

                yield deferLater(clock, 1.5)

        # Запись в БД
        from core.db.models import SessionLocal, File

        session = SessionLocal()
        try:
            session.add(
                File(
                    user_id=user_id,
                    filename=filename,
                    upload_time=datetime.datetime.utcnow(),  # noqa
                )
            )
            session.commit()
            log.msg(f"[DEFERRED] File '{filename}' successfully saved.")
        except Exception as e:
            log.msg(f"[DEFERRED] Error while saving file: {e}")
        finally:
            session.close()
