from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from typing import Any
from .base import Base


class MemPool(Base):
    __tablename__ = "service_mempool"
    raw: Mapped[dict[str, Any]] = mapped_column(JSONB)
