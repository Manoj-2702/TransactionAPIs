from fastapi import APIRouter, Depends, HTTPException, Form, Path, Query
from ..utils.auth import get_api_key
from ..database import insert_transaction, get_transaction_by_id, get_transactions, search_transactions_by_amount, search_transactions_by_date_range, search_transactions_by_type
from server.models.transaction import TransactionResponseDetails, Transaction, AmountDetails, Currency, Country, TransactionType, DeviceData, Tag
import random
from datetime import datetime

router = APIRouter()

@router.post("/create_transactions", dependencies=[Depends(get_api_key)], response_model=TransactionResponseDetails)
async def create_transaction(
    amount: float = Form(...),
    sender_id: str = Form(...),
    destination_id: str = Form(...),
    type: str = Form(...),
    currency: str = Form(...),
    country: str = Form(...)
):
    try:
        transaction_data = Transaction(
            type=TransactionType(type),
            transactionId=random.randint(100000, 999999),
            timestamp=datetime.now(),
            originUserId=sender_id,
            destinationUserId=destination_id,
            originAmountDetails=AmountDetails(
                transactionAmount=amount,
                transactionCurrency=Currency(currency),
                country=Country(country)
            ),
            destinationAmountDetails=AmountDetails(
                transactionAmount=amount,
                transactionCurrency=Currency(currency),
                country=Country(country)
            ),
            originDeviceData=DeviceData(),
            destinationDeviceData=DeviceData(),
            tags=[Tag()]
        )
        
        transaction_id = insert_transaction(transaction_data.dict(), transaction_data.transactionId)
        
        if not transaction_id:
            raise HTTPException(status_code=400, detail="Transaction could not be created")

        transaction_data = get_transaction_by_id(transaction_id)
        if not transaction_data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return TransactionResponseDetails(**transaction_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/get_transactions/{transaction_id}", dependencies=[Depends(get_api_key)])
async def retrieve_transaction(transaction_id: int = Path(..., description="The ID of the transaction to retrieve")):
    try:
        transaction_data = get_transactions(transaction_id)
        if not transaction_data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return format_transaction_details(transaction_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search_transaction_by_amount", dependencies=[Depends(get_api_key)])
async def transactions_by_amount(amount: float = Query(..., description="The amount to search for transactions")):
    try:
        transactions = search_transactions_by_amount(amount)
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found")
        
        return [format_search_result(transaction) for transaction in transactions]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search_transaction_by_date_range", dependencies=[Depends(get_api_key)])
async def transactions_by_date_range(
    start_date: datetime = Query(..., description="Start date for the date range"),
    end_date: datetime = Query(..., description="End date for the date range")
):
    try:
        transactions = search_transactions_by_date_range(start_date, end_date)
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found")
        
        return [format_search_result(transaction) for transaction in transactions]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions/search_by_type", dependencies=[Depends(get_api_key)])
async def transactions_by_type(type: str = Query(..., description="The type of transactions to search for")):
    try:
        transactions = search_transactions_by_type(type)
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found")
        
        return [format_search_result(transaction) for transaction in transactions]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def format_transaction_details(transaction_data):
    return {
        "id": transaction_data[0],
        "transaction_id": transaction_data[1],
        "type": transaction_data[2],
        "timestamp": transaction_data[3],
        "origin_user_id": transaction_data[4],
        "destination_user_id": transaction_data[5],
        "origin_amount": transaction_data[6],
        "origin_currency": transaction_data[7],
        "origin_country": transaction_data[8],
        "destination_amount": transaction_data[9],
        "destination_currency": transaction_data[10],
        "destination_country": transaction_data[11],
        "promotion_code_used": transaction_data[12],
        "reference": transaction_data[13],
        "origin_device_data": transaction_data[14],
        "destination_device_data": transaction_data[15],
        "tags": transaction_data[16]
    }
    
    
def format_search_result(transaction_data):
    return {
        "transaction_id": transaction_data[1],
        "type": transaction_data[2],
        "timestamp": transaction_data[3],
        "origin_user_id": transaction_data[4],
        "origin_amount": transaction_data[6],
        "origin_currency": transaction_data[7],
        "origin_country": transaction_data[8]
    }