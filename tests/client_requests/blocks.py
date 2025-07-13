from async_asgi_testclient import TestClient


async def get_latest_block(client: TestClient):
    return await client.get("/blocks/latest")


async def list_blocks(client: TestClient, page: int = 1):
    return await client.get(
        "/blocks/",
        query_string={"page": page},
    )


async def get_block(client: TestClient, blockhash: str):
    return await client.get(f"/blocks/{blockhash}")


async def list_block_transactions(
    client: TestClient, blockhash: str, page: int = 1
):
    return await client.get(
        f"/blocks/{blockhash}/transactions",
        query_string={"page": page},
    )
