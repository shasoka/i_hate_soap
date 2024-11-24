from spyne import rpc
from spyne.service import Service

from core.schemas.jwt import AuthHeader


# noinspection PyMethodParameters
class FileService(Service):
    __in_header__ = AuthHeader

    @rpc()
    def upload_file(ctx: Service):
        print(ctx.in_header.Authorization)
