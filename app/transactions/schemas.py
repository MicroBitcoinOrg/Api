from app.schemas import CustomModel


class TransactionBroadcastArgs(CustomModel):
    raw: str
