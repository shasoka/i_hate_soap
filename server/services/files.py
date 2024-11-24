import datetime
from pathlib import Path

from spyne import rpc, String, ByteArray
from spyne.service import Service
from twisted.internet import defer, reactor
from twisted.internet.interfaces import IReactorTime
from twisted.internet.task import deferLater
from twisted.python import log

from core.config import UPLOADS_DIR
from core.db.models import File, User
from core.schemas.jwt import AuthHeader
from core.security import get_current_auth_user


# noinspection PyMethodParameters
class FileService(Service):
    __in_header__ = AuthHeader

    @rpc(
        String(),  # filename
        ByteArray(),  # content
        _returns=File.customize(
            nillable=False,
            min_occurs=1,
        ),
    )
    def upload_file(ctx: Service, filename: str, content: bytes):
        user: User = get_current_auth_user(
            ctx,
            ctx.in_header.Authorization if ctx.in_header else None,  # noqa
        )

        defer.execute(
            FileService._async_write_file, user.id, filename, content
        )

        return (
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
        n_chunks: int = 10
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
                    f"[Deferred] Upload progress: {uploaded}/{ttl_size} bytes."
                )

                yield deferLater(clock, 0)

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
            session.refresh()
            log.msg(f"[Deferred] File '{filename}' successfully saved.")
        except Exception as e:
            log.msg(f"[Deffered] Error while saving file: {e}")
        finally:
            session.close()
