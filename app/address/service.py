from app.models import Output, Transaction, AddressBalance, Address, MemPool
from sqlalchemy import Select, select, func, ScalarResult
from app.transactions.service import (
    load_tx_details,
    get_token_units,
    load_mempool_tx_details,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.blocks.service import get_latest_block


def unspent_outputs_filters(query: Select, address: str, currency) -> Select:
    query = query.filter(
        Output.address == address,
        func.lower(Output.currency) == currency.lower(),  # type: ignore
        ~Output.spent,
    )

    return query


async def count_unspent_outputs(
    session: AsyncSession, address: str, currency: str
) -> int:
    return await session.scalar(
        unspent_outputs_filters(select(func.count(Output.id)), address, currency)
    )


async def list_unspent_outputs(
    session: AsyncSession,
    address: str,
    currency: str,
    limit: int,
    offset: int,
) -> ScalarResult[Output]:
    return await session.scalars(
        unspent_outputs_filters(
            select(Output).order_by(Output.amount.desc()).limit(limit).offset(offset),
            address,
            currency,
        )
    )


def utxo_cte(address: str, currency: str):
    return (
        select(
            Output,
            func.sum(Output.amount)  # type: ignore
            .over(order_by=Output.blockhash)
            .label("cumulative_amount"),
        )
        .filter(Output.address == address, Output.currency == currency, ~Output.spent)
        .cte("cumulative_outputs")
    )


async def count_utxo(
    session: AsyncSession, address: str, currency: str, amount: float
) -> int:
    cte = utxo_cte(address, currency)
    query = (
        select(func.count(1)).select_from(cte).where(cte.c.cumulative_amount < amount)
    )
    return await session.scalar(query) or 0


async def list_utxo(
    session: AsyncSession,
    address: str,
    currency: str,
    amount: float,
    limit: int,
    offset: int,
):
    cte = utxo_cte(address, currency)
    query = (
        select(cte)
        .select_from(cte)
        .where(cte.c.cumulative_amount < amount)
        .limit(limit)
        .offset(offset)
    )
    return await session.execute(query)


def transactions_filters(query: Select, address: str) -> Select:
    query = query.filter(Transaction.addresses.contains([address]))

    return query


async def count_transactions(session: AsyncSession, address: str):
    return await session.scalar(
        transactions_filters(select(func.count(Transaction.id)), address)
    )


async def list_transactions(
    session: AsyncSession, address: str, limit: int, offset: int
) -> list[Transaction]:
    latest_block = await get_latest_block(session)
    transactions = []
    for transaction in await session.scalars(
        transactions_filters(
            select(Transaction)
            .order_by(Transaction.created.desc())
            .limit(limit)
            .offset(offset),
            address,
        )
    ):
        transactions.append(await load_tx_details(session, transaction, latest_block))

    return transactions


async def list_balances(session: AsyncSession, address: str) -> list[AddressBalance]:
    balances = []
    for balance in await session.scalars(
        select(AddressBalance).filter(
            AddressBalance.address_id == Address.id, Address.address == address
        )
    ):
        balance.units = await get_token_units(session, balance.currency)

        balances.append(balance)

    return balances


async def list_address_mempool_transactions(session: AsyncSession, address: str):
    mempool = await session.scalar(select(MemPool).limit(1))

    if mempool is None:
        return []

    return [
        await load_mempool_tx_details(session, transaction, mempool.raw["outputs"])
        for transaction in mempool.raw["transactions"]
        if address in transaction["addresses"]
    ]
