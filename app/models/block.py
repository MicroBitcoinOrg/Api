from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from datetime import datetime
from typing import Any
from .base import Base


class Block(Base):
    __tablename__ = "service_blocks"

    blockhash: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    transactions: Mapped[list[str]] = mapped_column(ARRAY(String))
    height: Mapped[int] = mapped_column(index=True)
    movements: Mapped[dict[str, Any]] = mapped_column(JSONB)
    created: Mapped[datetime]
    timestamp: Mapped[int]
    prev_blockhash: Mapped[str] = mapped_column(String(64), index=True, nullable=True)

    @property
    def tx(self) -> int:
        return len(self.transactions)
