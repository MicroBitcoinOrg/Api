from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.errors import Abort
from . import service
from ..models import Block


async def require_latest_block(
    session: AsyncSession = Depends(get_session),
) -> Block:
    block = await service.get_latest_block(session)

    if block is None:
        raise Abort("blocks", "not-found")

    return block


async def require_block(
    hash_: str, session: AsyncSession = Depends(get_session)
) -> Block:
    block = await service.get_block_by_hash(session, hash_)

    if block is None:
        raise Abort("blocks", "not-found")

    return block
