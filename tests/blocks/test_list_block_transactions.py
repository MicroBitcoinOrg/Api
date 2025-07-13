from tests.client_requests import blocks
from app.utils import to_satoshi


async def test_normal(client, block_transaction):
    response = await blocks.list_block_transactions(
        client, block_transaction.blockhash
    )
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 1, "pages": 1, "page": 1}

    transaction_data = response.json()["list"][0]

    assert transaction_data["blockhash"] == block_transaction.blockhash
    assert transaction_data["amount"] == {
        token: to_satoshi(amount)
        for token, amount in block_transaction.amount.items()
    }
    assert transaction_data["height"] == block_transaction.height
    assert transaction_data["txid"] == block_transaction.txid


async def test_none(client, block):
    response = await blocks.list_block_transactions(client, block.blockhash)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 0, "pages": 0, "page": 1}
    assert response.json()["list"] == []
