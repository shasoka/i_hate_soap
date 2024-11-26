import datetime

from spyne import ComplexModel, DateTime, Integer, Float

from core.config import MAIN_TNS


class PrettyUptime(ComplexModel):
    __namespace__ = MAIN_TNS

    first_up: datetime.datetime = DateTime(
        nullable=True,
        min_occurs=1,
    )
    last_up: datetime.datetime = DateTime(
        nullable=True,
        min_occurs=1,
    )
    last_death: datetime.datetime = DateTime(
        nullable=True,
        min_occurs=1,
    )
    total_ups: int = Integer(
        nullable=False,
        min_occurs=1,
    )
    uptime_percentage: float = Float(
        nullable=False,
        min_occurs=1,
    )
