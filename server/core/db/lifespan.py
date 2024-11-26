import datetime

from sqlalchemy import desc

from .models import SessionLocal, ServerUptime


def on_startup():
    with SessionLocal() as session:
        session.add(
            ServerUptime(
                start_time=datetime.datetime.utcnow(),
            ),
        )
        session.commit()


def on_shutdown():
    with SessionLocal() as session:
        server_uptime = (
            session.query(ServerUptime)
            .order_by(
                desc(
                    ServerUptime.id,
                )
            )
            .first()
        )

        if server_uptime:
            server_uptime.death_time = datetime.datetime.utcnow()
            session.commit()
