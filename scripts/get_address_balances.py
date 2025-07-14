import asyncio
import typing

from sqlalchemy.orm import selectinload
from sqlalchemy import func, select

from app.database import sessionmanager
from app.models import AddressBalance
from app.settings import get_settings

settings: typing.Any = get_settings()


async def main():
    sessionmanager.init(settings.database.endpoint)

    file = open("balances.csv", "w")
    print("Address,Balances,Currency", file=file)

    async with sessionmanager.session() as session:
        total = await session.scalar(select(func.count(AddressBalance.id))) or 0
        balances = await session.stream_scalars(
            select(AddressBalance).options(selectinload(AddressBalance.address))
        )

        current = 0
        async for balance in balances:
            print(
                f"{balance.address.address},{float(balance.balance)},{balance.currency}",
                file=file,
            )

            if current % 100 == 0:
                print(
                    f"Progress: {current}/{total} ({(current / total) * 100 :.2f}%))",
                    end="\r",
                )
            current += 1

    print("\nComplete. Total rows:", total)

    file.close()


if __name__ == "__main__":
    asyncio.run(main())
