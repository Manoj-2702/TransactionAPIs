from datetime import datetime
from pydantic import BaseModel


class TransactionBaseSchema(BaseModel):
    concept: str
    amount: float
    destination_user_id: int
    created_at: datetime


class TransactionSchema(TransactionBaseSchema):
    class Config:
        orm_mode = True