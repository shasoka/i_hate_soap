import logging
import sys

from spyne import Application, Fault, InternalError, ResourceNotFoundError
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from sqlalchemy.exc import NoResultFound
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from core.config import (
    MAIN_TNS,
    MAX_ENVELOPE_SIZE,
    SOAP_SVC_HOST,
    SOAP_SVC_PORT,
    LOG_LEVEL,
)
from core.db.defctx import on_method_call
from services.files import FileService
from services.users import UserService


# Класс приложения, который расширяет Spyne Application
class MyApplication(Application):
    def __init__(
        self, services, tns, name=None, in_protocol=None, out_protocol=None
    ):
        super().__init__(services, tns, name, in_protocol, out_protocol)

    def call_wrapper(self, ctx):
        # SOAP поддерживает только 2** и 5** коды ошибок
        try:
            return ctx.service_class.call_wrapper(ctx)

        except NoResultFound as e:
            log.msg(e)
            raise ResourceNotFoundError(ctx.in_object)

        except Fault as e:
            log.msg(e)
            raise

        except Exception as e:
            log.msg(e)
            raise InternalError(e)


# Основная асинхронная часть
if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    logging.getLogger("spyne.protocol.xml").setLevel(LOG_LEVEL)
    observer = log.PythonLoggingObserver("twisted")
    log.startLogging(sys.stdout)

    application = MyApplication(
        [UserService, FileService],
        tns=MAIN_TNS,
        in_protocol=Soap11(validator="lxml"),
        out_protocol=Soap11(),
    )

    application.event_manager.add_listener("method_call", on_method_call)

    wsgi_app = WsgiApplication(
        application,
        max_content_length=MAX_ENVELOPE_SIZE,
    )
    resource = WSGIResource(reactor, reactor, wsgi_app)
    site = Site(resource)
    reactor.listenTCP(SOAP_SVC_PORT, site, interface=SOAP_SVC_HOST)  # noqa

    log.msg("🧼 Listening to http://127.0.0.1:8000")
    log.msg("📝 WSDL is at http://127.0.0.1:8000/?wsdl")

    sys.exit(reactor.run())  # noqa
