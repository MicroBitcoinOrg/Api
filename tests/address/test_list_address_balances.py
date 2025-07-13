from tests.client_requests import addresses


async def test_list_no_address(client):
    response = await addresses.get_address_balances(client, "asdasdsadasdasd")
    print(response.json())
    assert response.status_code == 200

    assert response.json() == []
