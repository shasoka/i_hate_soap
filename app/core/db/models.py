import datetime

from spyne import (
    TTableModel,
    Integer as SpInteger,
    String as SpString,
    ByteArray as SpByteArray,
)
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    TIMESTAMP,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..config import DATABASE_URL, USERS_TNS

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


class User(TableModel):
    __tablename__ = "users"
    __namespace__ = USERS_TNS

    # id: int = Column(Integer, primary_key=True)
    # username: str = Column(String(50), unique=True, nullable=False)
    # password_hash: bytes = Column(LargeBinary, nullable=False)
    id: int = SpInteger(pk=True, nullable=False)
    username: str = SpString(50, unique=True, nullable=False)
    password_hash: bytes = SpByteArray(nullable=False)


# noinspection PyDeprecation
class File(DeclarativeBase):
    __tablename__ = "files"

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id"))
    filename: str = Column(String(255), nullable=False)
    upload_time: datetime = Column(
        TIMESTAMP,
        server_default=func.now(),
        default=datetime.datetime.utcnow,
    )


# noinspection PyDeprecation
class ServerUptime(DeclarativeBase):
    __tablename__ = "server_uptime"

    id: int = Column(Integer, primary_key=True)
    start_time: datetime = Column(
        TIMESTAMP,
        server_default=func.now(),
        default=datetime.datetime.utcnow,
    )
