from tests.client_requests import transactions
from app.utils import to_satoshi


async def test_normal(client, transaction, block):
    response = await transactions.get_transaction_info(client, transaction.txid)
    print(response.json())
    assert response.status_code == 200

    assert response.json()["blockhash"] == transaction.blockhash
    assert response.json()["timestamp"] == transaction.timestamp
    assert response.json()["height"] == transaction.height
    assert response.json()["amount"] == {
        token: to_satoshi(amount)
        for token, amount in transaction.amount.items()
    }
    assert response.json()["txid"] == transaction.txid


async def test_not_found(client, block):
    response = await transactions.get_transaction_info(
        client, "aabbccdd112233445566778899"
    )
    assert response.status_code == 404

    assert response.json()["code"] == "transactions:not_found"
