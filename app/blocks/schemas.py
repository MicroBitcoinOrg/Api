from app.schemas import CustomModel, datetime_pd, PaginatedResponse


class BlockResponse(CustomModel):
    created: datetime_pd
    blockhash: str
    height: int
    tx: int


BlockPaginatedResponse = PaginatedResponse[BlockResponse]
