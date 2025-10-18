import asyncio
import json
import pathlib
import typing
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent))

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
                select(func.count(Transaction.id)).filter(
                    (Transaction.coinbase == None) | (Transaction.block_index == None)
                )
            )
            or 0
        )
        limit = 100

        query = (
            select(Transaction.id, Transaction.txid)
            .filter((Transaction.coinbase == None) | (Transaction.block_index == None))
            .limit(limit)
        )

        processed = 0

        while txs := (await session.execute(query)).all():
            updates: list[dict[str, typing.Any]] = []

            for dbid, txid in txs:
                transaction_result = await make_request(
                    settings.blockchain.endpoint,
                    [
                        {
                            "id": str(dbid),
                            "method": "getrawtransaction",
                            "params": [txid, True],
                        }
                    ],
                )
                tx = transaction_result[0]["result"]

                block_response = await make_request(
                    settings.blockchain.endpoint,
                    [
                        {
                            "id": tx["blockhash"],
                            "method": "getblock",
                            "params": [tx["blockhash"]],
                        }
                    ],
                )
                block = block_response[0]["result"]

                block_index = block["tx"].index(txid)
                updates.append(
                    {
                        "id": dbid,
                        "block_index": block_index,
                        "coinbase": block_index == 0,
                    }
                )

            await session.execute(
                update(Transaction),
                updates,
                execution_options={"synchronize_session": False},
            )
            await session.commit()
            processed += limit
            print(
                f"Progress: {processed}/{total} ({(processed/total)*100:.2f})",
                end="\r",
                flush=True,
            )

        print("\nDone")


if __name__ == "__main__":
    asyncio.run(main())
