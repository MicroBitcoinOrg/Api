from decimal import Decimal
from typing import Any

from app.models import Transaction, Output, Input, Block, MemPool
from sqlalchemy.ext.asyncio import AsyncSession
from app.blocks.service import get_latest_block
from sqlalchemy import select, Select, func
from app.settings import get_settings
from app.parser import make_request


async def get_token_units(_: AsyncSession, currency: str) -> int:
    if currency == "MBC":
        return 8

    return 8


async def load_tx_details(
    session: AsyncSession,
    transaction: Transaction | None,
    latest_block: Block | None = None,
) -> Transaction | None:

    if transaction is None:
        return transaction

    if latest_block is None:
        latest_block = await get_latest_block(session)

    transaction.confirmations = latest_block.height - transaction.height  # type: ignore

    transaction.fee = 0  # type: ignore

    output_shortcuts: dict[str, Output] = {}

    transaction.outputs = []  # type: ignore
    for output in await session.scalars(
        select(Output).filter(Output.txid == transaction.txid).order_by(Output.index)
    ):
        output: Output
        output.units = await get_token_units(session, output.currency)  # type: ignore

        output_shortcuts[output.shortcut] = output
        transaction.outputs.append(output)  # type: ignore

        if output.currency == "MBC":
            transaction.fee -= output.amount  # type: ignore

    transaction.inputs = []  # type: ignore
    for input_ in await session.scalars(
        select(Input).filter(Input.txid == transaction.txid)
    ):
        input_: Input

        output = await session.scalar(  # type: ignore
            select(Output).filter(Output.shortcut == input_.shortcut)
        )

        input_.amount = output.amount  # type: ignore
        input_.units = await get_token_units(session, output.currency)  # type: ignore
        input_.currency = output.currency  # type: ignore
        input_.address = output.address  # type: ignore

        transaction.inputs.append(input_)  # type: ignore

        if output.currency == "MBC":
            transaction.fee += output.amount  # type: ignore

    return transaction


async def get_transaction_by_txid(
    session: AsyncSession, txid: str
) -> Transaction | None:
    return await load_tx_details(
        session,
        await session.scalar(select(Transaction).filter(Transaction.txid == txid)),
    )


def transactions_filter(query: Select[Any], currency: str) -> Select[Any]:
    return query.filter(Transaction.currencies.contains([currency.upper()]))


async def count_transactions(session: AsyncSession, currency: str) -> int:
    return (
        await session.scalar(
            transactions_filter(select(func.count(Transaction.id)), currency)
        )
        or 0
    )


async def get_transactions(
    session: AsyncSession, currency: str, offset: int, limit: int
) -> list[Transaction]:
    latest_block = await get_latest_block(session)

    transactions: list[Transaction] = []
    for tx in await session.scalars(
        transactions_filter(
            select(Transaction)
            .order_by(Transaction.height.desc())
            .offset(offset)
            .limit(limit),
            currency,
        )
    ):
        transaction = await load_tx_details(session, tx, latest_block=latest_block)
        if transaction is None:
            continue

        transactions.append(transaction)

    return transactions


async def broadcast_transaction(raw: str):
    settings: Any = get_settings()

    return await make_request(
        settings.blockchain.endpoint,
        {"id": "broadcast", "method": "sendrawtransaction", "params": [raw]},
    )


async def load_mempool_tx_details(
    session: AsyncSession,
    transaction: dict[str, Any],
    mempool_outputs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    transaction["height"] = None
    transaction["confirmations"] = 0
    transaction["amount"] = {}
    transaction["fee"] = Decimal(0)

    for output in transaction["outputs"]:
        output["units"] = await get_token_units(session, output["currency"])

        transaction["amount"].setdefault(output["currency"], Decimal(0))  # type: ignore
        transaction["amount"][output["currency"]] += Decimal(output["amount"])

        if output["currency"] == "MBC":
            transaction["fee"] -= Decimal(output["amount"])

    for input_ in transaction["inputs"]:
        if input_["shortcut"] in mempool_outputs:
            output = mempool_outputs[input_["shortcut"]]

            input_["amount"] = Decimal(str(output["amount"]))
            input_["units"] = await get_token_units(session, output["currency"])
            input_["currency"] = output["currency"]
            input_["address"] = output["address"]

        else:
            output_: Output = await session.scalar(  # type: ignore
                select(Output).filter(Output.shortcut == input_["shortcut"])
            )

            input_["amount"] = output_.amount  # type: ignore
            input_["units"] = await get_token_units(session, output_.currency)
            input_["currency"] = output_.currency
            input_["address"] = output_.address

        if input_["currency"] == "MBC":
            transaction["fee"] += input_["amount"]

    return transaction


async def get_mempool_transactions(session: AsyncSession) -> list[dict[str, Any]]:
    mempool = await session.scalar(select(MemPool).limit(1))

    if mempool is None:
        return []

    return [
        await load_mempool_tx_details(session, transaction, mempool.raw["outputs"])
        for transaction in mempool.raw["transactions"]
    ]
