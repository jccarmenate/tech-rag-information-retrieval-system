import os
from collections.abc import Generator

from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.models import Base

settings = get_settings()

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

os.makedirs("data", exist_ok=True)
engine = create_engine(settings.database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    add_missing_columns(engine)


def add_missing_columns(bind: Engine) -> None:
    """`create_all` never alters existing tables, so a database created by an
    older version would lack newly added columns. This handles the only kind
    of schema change the project makes — new nullable columns — without
    pulling in a migration framework.
    """
    inspector = inspect(bind)
    with bind.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                continue
            existing = {col["name"] for col in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing or not column.nullable:
                    continue
                col_type = column.type.compile(dialect=bind.dialect)
                conn.execute(
                    text(f'ALTER TABLE {table.name} ADD COLUMN "{column.name}" {col_type}')
                )


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
