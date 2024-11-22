from jwt import InvalidTokenError
from spyne import (
    ResourceAlreadyExistsError,
    String,
    Boolean,
    rpc,
    InvalidCredentialsError,
    Fault,
)
from spyne.service import Service

from core.db.models import User
from core.schemas.jwt import JWTResponse
from core.security import (
    hash_password,
    validate_password,
    encode_jwt,
    decode_jwt,
)


# noinspection PyMethodParameters
class UserService(Service):
    @rpc(
        String(
            min_len=5,
            max_len=50,
            min_occurs=1,
            nillable=False,
        ),  # username
        String(
            min_len=5,
            max_len=50,
            min_occurs=1,
            nillable=False,
        ),  # password
        _returns=User.customize(
            nillable=False,
            min_occurs=1,
        ),
    )
    def register(
        ctx: Service,
        username: str,
        password: str,
    ):
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

    @rpc(
        String(
            min_occurs=1,
            nillable=False,
        ),  # username
        _returns=Boolean(
            nillable=False,
            min_occurs=1,
        ),
    )
    def check_token(
        ctx: Service,
        token: str,
    ):
        try:
            payload: dict = decode_jwt(token)
        except InvalidTokenError:
            return False

        if (
            ctx.udc.session.query(User)
            .filter(User.id == int(payload["sub"]))
            .first()
        ):
            return True

        return False

    @rpc(
        String(
            min_occurs=1,
            nillable=False,
        ),  # username
        String(
            min_occurs=1,
            nillable=False,
        ),  # password
        _returns=JWTResponse.customize(
            nillable=False,
            min_occurs=1,
        ),
    )
    def login(
        ctx: Service,
        username: str,
        password: str,
    ):
        auth_fault: Fault = InvalidCredentialsError(
            "Login or password is invalid"
        )

        # Идентификация
        user = (
            ctx.udc.session.query(User)
            .filter(User.username == username)
            .first()
        )

        if not user:
            raise auth_fault

        if not validate_password(password, user.password_hash):
            raise auth_fault

        return JWTResponse(
            access_token=encode_jwt(
                payload={
                    "sub": str(user.id),
                    "username": user.username,
                }
            ),
            token_type="Bearer",
        )
