from datetime import datetime

from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String

from .base import Base


class Transaction(Base):
    __tablename__ = "service_transactions"

    currencies: Mapped[list[str]] = mapped_column(ARRAY(String(64)), index=True)
    txid: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    blockhash: Mapped[str] = mapped_column(String(64), index=True)
    addresses: Mapped[list[str]] = mapped_column(ARRAY(String), index=True)
    created: Mapped[datetime]
    timestamp: Mapped[int]
    size: Mapped[int]
    height: Mapped[int]
    locktime: Mapped[int]
    version: Mapped[int]

    amount: Mapped[dict[str, float]] = mapped_column(JSONB, default={})
