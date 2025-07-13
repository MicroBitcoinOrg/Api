from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import get_session
from app.errors import Abort
from . import service


async def require_transaction(
    txid: str, session: AsyncSession = Depends(get_session)
):
    transaction = await service.get_transaction_by_txid(session, txid)

    if not transaction:
        raise Abort("transactions", "not-found")

    return transaction
