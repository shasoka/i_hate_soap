from spyne.service import Service

from .models import SessionLocal


class DefinedContext(object):
    def __init__(self):
        self.session = SessionLocal()

    def __del__(self):
        self.session.close()


def on_method_call(ctx: Service):
    ctx.udc = DefinedContext()


def on_method_return_object(ctx):
    ctx.udc.session.commit()
