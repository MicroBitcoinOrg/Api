from typing import Annotated, TypeVar, Generic
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta
from pydantic import PlainSerializer
from app import utils


# Custom Pydantic serializers
datetime_pd = Annotated[
    datetime,
    PlainSerializer(
        lambda x: utils.to_timestamp(x),
        return_type=int,
    ),
]

timedelta_pd = Annotated[
    timedelta,
    PlainSerializer(
        lambda x: int(x.total_seconds()),
        return_type=int,
    ),
]

Satoshi = Annotated[
    float,
    PlainSerializer(
        utils.to_satoshi,
        return_type=int,
    ),
]


class CustomModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        from_attributes=True,
    )


class PaginationDataResponse(CustomModel):
    total: int
    pages: int
    page: int


T = TypeVar("T", bound=CustomModel)


class PaginatedResponse(CustomModel, Generic[T]):
    pagination: PaginationDataResponse
    list: list[T]


class OutputResponse(CustomModel):
    address: str
    txid: str
    currency: str
    amount: Satoshi
    timelock: int
    type: str
    spent: bool
    script: str
    asm: str
    index: int


OutputPaginatedResponse = PaginatedResponse[OutputResponse]


class OutputFullResponse(OutputResponse):
    units: int


class InputFullResponse(CustomModel):
    amount: Satoshi
    units: int
    currency: str
    address: str


class TransactionResponse(CustomModel):
    height: int | None
    blockhash: str | None
    timestamp: int | None
    txid: str
    amount: dict[str, Satoshi]
    outputs: list[OutputFullResponse]
    inputs: list[InputFullResponse]
    confirmations: int
    fee: Satoshi


TransactionPaginatedResponse = PaginatedResponse[TransactionResponse]


class BalanceResponse(CustomModel):
    currency: str
    units: int
    balance: Satoshi
