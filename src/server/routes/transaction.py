from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.server.models.transaction import Transaction
from src.server.utils.flagright_api import verify_transaction

router = APIRouter()

class TransactionResponse(BaseModel):
    transactionId: str
    status: str

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(transaction: Transaction):
    try:
        response = await verify_transaction(transaction.dict())
        return TransactionResponse(
            transactionId=response.get("transactionId"),
            status=response.get("status")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
