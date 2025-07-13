from async_asgi_testclient import TestClient


async def get_transaction_info(client: TestClient, txid: str):
    return await client.get(f"/transactions/{txid}")


async def list_transactions(client: TestClient, token: str):
    return await client.get(
        f"/transactions/list/{token}",
    )


async def broadcast_transaction(client: TestClient, raw: str):
    return await client.post(
        "/transactions/broadcast",
        query_string={"raw": raw},
    )
