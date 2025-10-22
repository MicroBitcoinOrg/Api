import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Transaction, Block, Address, Output
from app.utils import utcnow, to_timestamp


async def create_transaction(
    session: AsyncSession,
    currencies: list[str] | None = None,
    size: int = 1024,
    height: int = 1,
    locktime: int = 0,
    version: int = 1,
    amount: dict[str, float] | None = None,
    blockhash: str | None = None,
    addresses: list[str] | None = None,
    coinbase: bool = False,
) -> Transaction:
    if currencies is None:
        currencies = ["MBC"]

    if amount is None:
        amount = {"MBC": 10.0}

    now = utcnow()

    transaction = Transaction(
        currencies=currencies,
        txid=secrets.token_hex(32),
        blockhash=blockhash or secrets.token_hex(32),
        created=now,
        timestamp=to_timestamp(now),
        size=size,
        height=height,
        locktime=locktime,
        version=version,
        amount=amount,
        coinbase=coinbase,
        addresses=addresses or [secrets.token_hex(32), secrets.token_hex(32)],
    )

    session.add(transaction)

    await session.commit()

    return transaction


async def create_block(
    session: AsyncSession,
    blockhash: str = None,
    height: int = 1,
    movements: dict = None,
    transactions: list[str] = None,
    prev_blockhash: str = None,
) -> Block:
    if movements is None:
        movements = {}

    if transactions is None:
        transactions = []

    now = utcnow()

    block = Block(
        blockhash=blockhash or secrets.token_hex(32),
        transactions=transactions,
        height=height,
        movements=movements,
        created=now,
        timestamp=to_timestamp(now),
        prev_blockhash=prev_blockhash,
    )

    session.add(block)

    await session.commit()

    return block


async def create_address(session: AsyncSession) -> Address:
    address = Address(
        address=secrets.token_hex(32),
    )

    session.add(address)

    await session.commit()

    return address


async def create_output(
    session: AsyncSession,
    currency: str = "MBC",
    shortcut: str = "aabbccddeeff0011223344",
    blockhash: str = None,
    address: str = None,
    txid: str = None,
    amount: float = 10.0,
    timelock: int = 0,
    type: str = "new_token",
    spent: bool = False,
    index: int = 1,
):
    output = Output(
        currency=currency,
        shortcut=shortcut,
        blockhash=blockhash or secrets.token_hex(32),
        address=address or secrets.token_hex(32),
        txid=txid or secrets.token_hex(32),
        amount=amount,  # type: ignore
        timelock=timelock,
        type=type,
        meta={},
        spent=spent,
        script="",
        asm="",
        index=index,
    )

    session.add(output)

    await session.commit()

    return output
