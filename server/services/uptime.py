import datetime

from spyne import rpc
from spyne.service import Service
from sqlalchemy import func, asc, desc

from core.db.models import ServerUptime
from core.schemas.jwt import AuthHeader
from core.schemas.pretty_uptime import PrettyUptime
from core.security import authenticate_user


# noinspection PyMethodParameters
class UptimeService(Service):
    __in_header__ = AuthHeader

    @rpc(
        _returns=PrettyUptime.customize(
            min_occurs=1,
            nillable=False,
        )
    )
    def check_uptime(ctx):
        authenticate_user(ctx)

        # Получаем первый и последний запуск сервера
        first_uptime: ServerUptime = (
            ctx.udc.session.query(ServerUptime.start_time)
            .order_by(asc(ServerUptime.start_time))
            .first()
        )

        last_uptime: ServerUptime = (
            ctx.udc.session.query(ServerUptime.start_time)
            .order_by(desc(ServerUptime.start_time))
            .first()
        )

        # Получаем последнюю смерть, если есть
        last_death: ServerUptime | None = (
            ctx.udc.session.query(ServerUptime.death_time)
            .filter(ServerUptime.death_time != None)  # noqa
            .order_by(desc(ServerUptime.death_time))
            .first()
        )
        last_death_time = last_death.death_time if last_death else None

        # Получаем общее количество запусков
        total_uptimes: int = ctx.udc.session.query(
            func.count(ServerUptime.id)
        ).scalar()

        if first_uptime and last_uptime:
            first_uptime_time = first_uptime.start_time
            last_uptime_time = last_uptime.start_time
            now = datetime.datetime.utcnow()

            # Суммируем время жизни для всех запусков (с death_time)
            total_lifetime = 0
            uptimes: list[ServerUptime] = (
                ctx.udc.session.query(ServerUptime)
                .order_by(asc(ServerUptime.start_time))
                .all()
            )

            for i in range(len(uptimes)):
                uptime = uptimes[i]
                if uptime.death_time:
                    total_lifetime += (
                        uptime.death_time - uptime.start_time
                    ).total_seconds()
                elif (
                    i == len(uptimes) - 1
                ):  # для последнего запуска, если death_time нет
                    total_lifetime += (now - uptime.start_time).total_seconds()

            # Считаем общее время с первого запуска до текущего времени
            total_time_span = (now - first_uptime_time).total_seconds()

            uptime_percentage = (
                (total_lifetime / total_time_span) * 100
                if total_time_span > 0
                else 0
            )
        else:
            uptime_percentage = 0
            first_uptime_time = None
            last_uptime_time = None
            last_death_time = None

        return PrettyUptime(
            first_up=first_uptime_time,
            last_up=last_uptime_time,
            last_death=last_death_time,
            total_ups=total_uptimes,
            uptime_percentage=uptime_percentage,
        )
