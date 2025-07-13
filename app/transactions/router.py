from starlette.responses import JSONResponse

from app.schemas import TransactionPaginatedResponse, TransactionResponse
from app.utils import pagination, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import require_transaction
from .schemas import TransactionBroadcastArgs
from fastapi import APIRouter, Depends
from app.dependencies import get_page
from app.database import get_session
from app.models import Transaction
from . import service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/list/{token}", response_model=TransactionPaginatedResponse)
async def get_transactions(
    token: str = "MBC",
    page: int = Depends(get_page),
    session: AsyncSession = Depends(get_session),
):
    limit, offset = pagination(page)

    total = await service.count_transactions(session, token)
    transactions = await service.get_transactions(session, token, offset, limit)

    return paginated_response(
        transactions,
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/mempool",
    response_model=list[TransactionResponse],
    operation_id="get_mempool_transactions",
)
async def get_mempool(session: AsyncSession = Depends(get_session)):
    return await service.get_mempool_transactions(session)


@router.get("/{txid}", response_model=TransactionResponse)
async def get_transaction_info(
    transaction: Transaction = Depends(require_transaction),
):
    return transaction


@router.post("/broadcast")
async def broadcast_transaction(
    transaction: TransactionBroadcastArgs,
):
    node_response = await service.broadcast_transaction(transaction.raw)

    if node_response["error"] is not None:
        return JSONResponse(node_response["error"], status_code=400)

    return node_response["result"]
