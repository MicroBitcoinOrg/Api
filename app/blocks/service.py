from sqlalchemy import select, func, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Block, Transaction


async def get_latest_block(session: AsyncSession) -> Block:
    return await session.scalar(
        select(Block).order_by(Block.height.desc()).limit(1)
    )


async def count_blocks(session: AsyncSession) -> int:
    return await session.scalar(select(func.count(Block.id)))


async def get_blocks(
    session: AsyncSession, offset: int, limit: int
) -> ScalarResult[Block]:
    return await session.scalars(
        select(Block).order_by(Block.height.desc()).offset(offset).limit(limit),
    )


async def get_block_by_hash(session: AsyncSession, hash_: str) -> Block:
    return await session.scalar(select(Block).filter(Block.blockhash == hash_))


async def count_block_transactions(session: AsyncSession, hash_: str):
    return await session.scalar(
        select(func.count(Transaction.id)).filter(
            Transaction.blockhash == hash_
        )
    )


async def get_block_transactions(
    session: AsyncSession, hash_: str, offset: int, limit: int
) -> list[Transaction]:
    from app.transactions.service import load_tx_details

    latest_block = await get_latest_block(session)
    transactions = []
    for transaction in await session.scalars(
        select(Transaction)
        .filter(Transaction.blockhash == hash_)
        .offset(offset)
        .limit(limit),
    ):
        transactions.append(
            await load_tx_details(session, transaction, latest_block)
        )

    return transactions
