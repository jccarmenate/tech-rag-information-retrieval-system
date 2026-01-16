import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    title: Mapped[str] = mapped_column(String(512))
    text: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    published_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    fetched_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
