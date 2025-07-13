from tests.client_requests import addresses
from app.utils import to_satoshi


async def test_normal(client, address_utxo):
    response = await addresses.get_unspent_address_outputs(
        client, address_utxo.address, "MBC"
    )
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 1, "pages": 1, "page": 1}

    utxo = response.json()["list"][0]

    assert utxo["txid"] == address_utxo.txid
    assert utxo["currency"] == address_utxo.currency
    assert utxo["amount"] == to_satoshi(address_utxo.amount)  # type: ignore
    assert utxo["timelock"] == address_utxo.timelock
    assert utxo["type"] == address_utxo.type
    assert utxo["spent"] == address_utxo.spent
    assert utxo["index"] == address_utxo.index


async def test_none(client, address):
    response = await addresses.get_unspent_address_outputs(
        client, address.address, "MBC"
    )
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 0, "pages": 0, "page": 1}
    assert response.json()["list"] == []
