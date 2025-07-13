import time

from app import sessionmanager, parser, get_settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import MemPool
from sqlalchemy import select


async def sync_mempool():
    start = time.time()
    settings = get_settings()

    async with sessionmanager.session() as session:
        session: AsyncSession

        mempool = await session.scalar(select(MemPool).limit(1))

        if mempool is None:
            mempool = MemPool(raw={})
            session.add(mempool)

        response = await parser.make_request(
            settings.blockchain.endpoint,
            {"id": "mempool", "method": "getrawmempool", "params": []},
        )
        if response["error"]:
            return

        data = await parser.parse_transactions(response["result"])

        raw_mempool = {"transactions": [], "outputs": {}}

        for transaction in data["transactions"]:
            txid = transaction["txid"]
            outputs = transaction.setdefault("outputs", [])
            inputs = transaction.setdefault("inputs", [])

            for output in data["outputs"].copy():
                if output["txid"] != txid:
                    continue

                output["amount"] = float(output["amount"])

                outputs.append(output)
                raw_mempool["outputs"][output["shortcut"]] = output

                # Reduce amount of next iterations
                data["outputs"].remove(output)

            for input_ in data["inputs"].copy():
                if input_["txid"] != txid:
                    continue

                inputs.append(input_)

                # Reduce amount of next iterations
                data["inputs"].remove(input_)

            raw_mempool["transactions"].append(transaction)

        mempool.raw = raw_mempool

        await session.commit()

        print(
            f"Synced mempool in {(time.time() - start) * 1000:.3f} miliseconds"
        )
