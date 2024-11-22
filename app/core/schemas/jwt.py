from spyne import ComplexModel, String

from core.config import MAIN_TNS


class JWTResponse(ComplexModel):
    __namespace__ = MAIN_TNS

    access_token: str = String(nullable=False, min_occurs=1)
    token_type: str = String(nullable=False, min_occurs=1)
