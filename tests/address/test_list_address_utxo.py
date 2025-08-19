from sqlalchemy.ext.asyncio import AsyncSession
from async_asgi_testclient import TestClient
from tests.client_requests import addresses
from app.models.output import Output
from app.utils import to_satoshi
from tests import helpers
import secrets


async def test_default(client: TestClient, address_utxo: Output, session: AsyncSession):
    extra_amount = 100

    utxo1 = await helpers.create_output(
        session,
        address_utxo.currency,
        address=address_utxo.address,
        spent=False,
        shortcut=secrets.token_hex(16),
        amount=123,
    )

    required_amount = address_utxo.amount + utxo1.amount + extra_amount

    response = await addresses.get_address_utxo(
        client, address_utxo.address, float(required_amount), "MBC"
    )
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 2, "pages": 1, "page": 1}

    for txo in response.json()["list"]:
        assert txo["timelock"] in (address_utxo.timelock, utxo1.timelock)
        assert txo["amount"] in (
            to_satoshi(float(address_utxo.amount)),
            to_satoshi(float(utxo1.amount)),
        )
        assert txo["currency"] in (address_utxo.currency, utxo1.currency)
        assert txo["index"] in (address_utxo.index, utxo1.index)
        assert txo["type"] in (address_utxo.type, utxo1.type)
        assert txo["txid"] in (address_utxo.txid, utxo1.txid)
        assert txo["spent"] is False


async def test_none(client, address):
    response = await addresses.get_address_utxo(client, address.address, 1, "MBC")
    print(response.json())
    assert response.status_code == 200

    assert response.json()["pagination"] == {"total": 0, "pages": 0, "page": 1}
    assert response.json()["list"] == []
