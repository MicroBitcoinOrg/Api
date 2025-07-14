import asyncio
import typing

from sqlalchemy import func, select, update

from app.database import sessionmanager
from app.settings import get_settings
from app.parser import make_request
from app.models import Transaction

settings: typing.Any = get_settings()


async def main():
    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:

        total = (
            await session.scalar(
                select(func.count(Transaction.id)).filter(Transaction.addresses == ())
            )
            or 0
        )
        limit = 100

        offset = 0
        query = (
            select(Transaction.id, Transaction.txid)
            .limit(limit)
            .filter(Transaction.addresses == ())
            .limit(limit)
        )

        total /= limit

        while txs := (await session.execute(query.offset(offset))).all():
            offset += limit

            transactions_result = await make_request(
                settings.blockchain.endpoint,
                [
                    {
                        "id": str(dbid),
                        "method": "getrawtransaction",
                        "params": [txid, True],
                    }
                    for dbid, txid in txs
                ],
            )

            addresses: dict[str, list[str]] = {
                tx["id"]: (
                    list(
                        set(
                            vout["scriptPubKey"]["address"]
                            for vout in tx["result"]["vout"]
                            if vout["scriptPubKey"]["type"] != "nulldata"
                        )
                    )
                )
                for tx in transactions_result
            }

            await session.execute(
                update(Transaction),
                [
                    {"id": dbid, "addresses": addresses}
                    for dbid, addresses in addresses.items()
                ],
                execution_options={"synchronize_session": False},
            )
            await session.commit()
            print(
                f"Progress: {offset // limit}/{total} ({(offset // limit/total)*100:.2f})",
                end="\r",
                flush=True,
            )
            break

        print("\nDone")


if __name__ == "__main__":
    asyncio.run(main())
