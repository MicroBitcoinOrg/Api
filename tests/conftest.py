# Based on https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
# https://github.com/gpkc/fastapi-sqlalchemy-pytest

from contextlib import ExitStack
import asyncio

from pytest_postgresql.janitor import DatabaseJanitor
from async_asgi_testclient import TestClient
from pytest_postgresql import factories
from sqlalchemy import make_url, delete
import pytest

from app.models import Base, Transaction, Block, Address, Output
from app.database import sessionmanager, get_session
from app.settings import get_settings
from app import create_app
from tests import helpers

# This is needed to obtain PostgreSQL version
test_db = factories.postgresql_proc()


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield create_app(init_db=False)


@pytest.fixture
async def client(app):
    async with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def connection_test(test_db, event_loop):
    # Switch to testing config using env variable
    settings = get_settings()
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")

    db_url = make_url(settings.database.endpoint)

    pg_password = db_url.password
    pg_user = db_url.username
    pg_db = db_url.database
    pg_host = db_url.host
    pg_port = db_url.port

    with DatabaseJanitor(
        pg_user, pg_host, pg_port, pg_db, test_db.version, pg_password
    ):
        sessionmanager.init(settings.database.endpoint)
        yield
        await sessionmanager.close()


@pytest.fixture(scope="session", autouse=True)
async def create_tables(connection_test):
    async with sessionmanager.connect() as connection:
        await connection.run_sync(Base.metadata.create_all)


# noinspection PyTestUnpassedFixture
@pytest.fixture(scope="function", autouse=True)
async def clean_tables(connection_test):
    yield
    async with sessionmanager.session() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(delete(table))

        await session.commit()


@pytest.fixture(scope="function", autouse=True)
async def session_override(app, connection_test):
    async def get_session_override():
        async with sessionmanager.session() as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override  # noqa


@pytest.fixture
async def session():
    async with sessionmanager.session() as session:
        yield session


@pytest.fixture
async def transaction(session) -> Transaction:
    return await helpers.create_transaction(session)


@pytest.fixture
async def block(session) -> Block:
    return await helpers.create_block(session)


@pytest.fixture
async def block_transaction(session, block) -> Transaction:
    transaction = await helpers.create_transaction(session, blockhash=block.blockhash)

    block.transactions = [transaction.txid]

    await session.commit()

    return transaction


@pytest.fixture
async def address(session) -> Address:
    return await helpers.create_address(session)


@pytest.fixture
async def address_utxo(session, address) -> Output:
    return await helpers.create_output(session, address=address.address, spent=False)


@pytest.fixture
async def address_transaction(session, address) -> Transaction:
    return await helpers.create_transaction(session, addresses=[address.address])
