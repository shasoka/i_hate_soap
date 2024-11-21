from spyne import rpc, Unicode, ResourceAlreadyExistsError
from spyne.service import Service

from core.db.models import User
from core.security import hash_password


# noinspection PyMethodParameters
class UserService(Service):
    @rpc(
        Unicode,  # username
        Unicode,  # password
        _returns=User,
    )
    def register(
        ctx: Service,
        username: str,
        password: str,
    ) -> str:
        if (
            ctx.udc.session.query(User)
            .filter(User.username == username)
            .first()
        ):
            raise ResourceAlreadyExistsError(username)

        ctx.udc.session.add(
            user := User(
                username=username,
                password_hash=hash_password(password),
            )
        )

        ctx.udc.session.flush()
        return user
