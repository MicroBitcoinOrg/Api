from datetime import datetime

from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Index, String

from .base import Base


class Transaction(Base):
    __tablename__ = "service_transactions"
    __table_args__ = (
        Index(
            "ix_service_transactions_addresses",
            "addresses",
            postgresql_using="gin",
        ),
    )

    currencies: Mapped[list[str]] = mapped_column(ARRAY(String(64)), index=True)
    txid: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    blockhash: Mapped[str] = mapped_column(String(64), index=True)
    addresses: Mapped[list[str]] = mapped_column(ARRAY(String))
    created: Mapped[datetime]
    timestamp: Mapped[int]
    size: Mapped[int]
    height: Mapped[int]
    locktime: Mapped[int]
    version: Mapped[int]

    amount: Mapped[dict[str, float]] = mapped_column(JSONB, default={})

    coinbase: Mapped[bool]
