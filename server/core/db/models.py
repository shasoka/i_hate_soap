import datetime

from spyne import (
    TTableModel,
    Integer as SpInteger,
    String as SpString,
    ByteArray as SpByteArray,
    DateTime as SpDateTime,
)
from sqlalchemy import (
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..config import DATABASE_URL, MAIN_TNS

# [SQLAlchemy] движок и метаданные
_engine = create_engine(DATABASE_URL)
DeclarativeBase = declarative_base()
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_engine,
)
DeclarativeBase.metadata.create_all(bind=_engine)

# [Spyne] бинд метаданных
TableModel = TTableModel()
TableModel.Attributes.sqla_metadata.bind = _engine


class File(TableModel):
    __tablename__ = "files"
    __namespace__ = MAIN_TNS

    id: int = SpInteger(
        pk=True,
        nullable=False,
        min_occurs=1,
    )
    filename: str = SpString(
        255,
        unique=True,
        nullable=False,
        min_occurs=1,
        default="anonymous_file",
    )
    upload_time: datetime = SpDateTime(
        min_occurs=1,
        nullable=False,
    )

    user_id: int = SpInteger(
        nullable=False,
        min_occurs=1,
    )


class User(TableModel):
    __tablename__ = "users"
    __namespace__ = MAIN_TNS

    id: int = SpInteger(
        pk=True,
        nullable=False,
        min_occurs=1,
    )
    username: str = SpString(
        50,
        unique=True,
        nullable=False,
        min_occurs=1,
        min_len=5,
    )
    password_hash: bytes = SpByteArray(
        nullable=False,
        min_occurs=1,
    )


# noinspection PyDeprecation
class ServerUptime(TableModel):
    __tablename__ = "server_uptime"
    __namespace__ = MAIN_TNS

    id: int = SpInteger(
        pk=True,
        nullable=False,
        min_occurs=1,
    )
    start_time: datetime = SpDateTime(
        min_occurs=1,
        nullable=False,
    )
    death_time: datetime = SpDateTime(
        min_occurs=1,
        nullable=False,
    )
