"""For database tasks."""

import contextlib
import datetime
from typing import Any

import sqlalchemy
import sqlalchemy.event
import sqlalchemy.orm

from . import paths

__all__ = ["RyujinxSave", "client", "CLIENT_CONFIGS"]
CLIENT_CONFIGS: dict[str, Any] = {"url": f"sqlite:///{paths.DATABASE_FILE}"}


class Base(sqlalchemy.orm.DeclarativeBase): ...


class RyujinxSave(Base):
    __tablename__ = "ryujinx_saves"
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        primary_key=True
    )
    label: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column()
    created: sqlalchemy.orm.Mapped[datetime.datetime] = (
        sqlalchemy.orm.mapped_column(
            type_=sqlalchemy.TIMESTAMP,
            server_default=sqlalchemy.func.current_timestamp(),
        )
    )
    updated: sqlalchemy.orm.Mapped[datetime.datetime] = (
        sqlalchemy.orm.mapped_column(
            type_=sqlalchemy.TIMESTAMP,
            server_default=sqlalchemy.func.current_timestamp(),
        )
    )
    last_used: sqlalchemy.orm.Mapped[datetime.datetime] = (
        sqlalchemy.orm.mapped_column(type_=sqlalchemy.TIMESTAMP, nullable=True)
    )
    size: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        server_default="0"
    )


@sqlalchemy.event.listens_for(RyujinxSave, "before_update")
def _(mapper: object, connection: object, target: RyujinxSave):
    target.updated = datetime.datetime.now(datetime.timezone.utc)


@contextlib.contextmanager
def client():
    """Create a session with the database."""

    engine = sqlalchemy.create_engine(**CLIENT_CONFIGS)
    Base.metadata.create_all(engine)
    with sqlalchemy.orm.Session(engine) as session:
        yield session
        session.commit()
