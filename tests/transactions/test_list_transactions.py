from tests.client_requests import transactions
from app.utils import to_satoshi


async def test_mbc_none(client):
    response = await transactions.list_transactions(client, "mbc")
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 0, "pages": 0, "page": 1}
    assert response.json()["list"] == []


async def test_mbc(client, transaction, block, session):
    response = await transactions.list_transactions(client, "mbc")
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 1, "pages": 1, "page": 1}
    transaction_data = response.json()["list"][0]

    assert transaction_data["blockhash"] == transaction.blockhash
    assert transaction_data["amount"] == {
        token: to_satoshi(amount) for token, amount in transaction.amount.items()
    }
    assert transaction_data["height"] == transaction.height
    assert transaction_data["txid"] == transaction.txid
