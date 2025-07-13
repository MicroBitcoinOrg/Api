from tests.client_requests import blocks
from app.utils import to_timestamp


async def test_normal(client, block):
    response = await blocks.get_latest_block(client)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["created"] == to_timestamp(block.created)
    assert response.json()["blockhash"] == block.blockhash
    assert response.json()["height"] == block.height
    assert response.json()["tx"] == block.tx


async def test_not_found(client):
    response = await blocks.get_latest_block(client)
    print(response.json())
    assert response.status_code == 404

    assert response.json()["code"] == "blocks:not_found"
