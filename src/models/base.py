from sqlalchemy.orm import DeclarativeMeta, Mapped, mapped_column, declarative_base, DeclarativeBase
from datetime import datetime, timezone
import sqlalchemy as sa
from typing import Optional

class Base(DeclarativeBase):

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        default=datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )

    @classmethod
    def on_conflict_constraint(cls) -> tuple | None:
        return None



