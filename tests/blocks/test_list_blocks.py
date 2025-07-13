from tests.client_requests import blocks
from app.utils import to_timestamp


async def test_normal(client, block):
    response = await blocks.list_blocks(client)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 1, "pages": 1, "page": 1}

    block_data = response.json()["list"][0]

    assert block_data["created"] == to_timestamp(block.created)
    assert block_data["blockhash"] == block.blockhash
    assert block_data["height"] == block.height
    assert block_data["tx"] == block.tx


async def test_none(client):
    response = await blocks.list_blocks(client)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 0, "pages": 0, "page": 1}

    assert response.json()["list"] == []
