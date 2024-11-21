import logging
from wsgiref.simple_server import make_server

from spyne import Application, ResourceNotFoundError, Fault, InternalError
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from sqlalchemy.exc import NoResultFound

from core.config import USERS_TNS
from core.db.defctx import on_method_call, on_method_return_object
from core.db.models import TableModel
from services.users import UserService

logging.basicConfig(level=logging.CRITICAL)


class MyApplication(Application):
    def __init__(
        self,
        services,
        tns,
        name=None,
        in_protocol=None,
        out_protocol=None,
    ):
        super(MyApplication, self).__init__(
            services,
            tns,
            name,
            in_protocol,
            out_protocol,
        )

    def call_wrapper(self, ctx):
        try:
            return ctx.service_class.call_wrapper(ctx)

        except NoResultFound:
            raise ResourceNotFoundError(ctx.in_object)

        except Fault:
            # logging.error(e)
            raise

        except Exception as e:
            # logging.exception(e)
            raise InternalError(e)


if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    UserService.event_manager.add_listener(
        "method_call",
        on_method_call,
    )
    # noinspection PyUnresolvedReferences
    UserService.event_manager.add_listener(
        "method_return_object",
        on_method_return_object,
    )

    application = MyApplication(
        [UserService],
        tns=USERS_TNS,
        in_protocol=Soap11(validator="lxml"),
        out_protocol=Soap11(),
    )

    wsgi_app = WsgiApplication(application)
    server = make_server("127.0.0.1", 8000, wsgi_app)

    TableModel.Attributes.sqla_metadata.create_all()

    logging.info("🧼 Listening to http://127.0.0.1:8000")
    logging.info("📝 WSDL is at http://127.0.0.1:8000/?wsdl")

    server.serve_forever()
