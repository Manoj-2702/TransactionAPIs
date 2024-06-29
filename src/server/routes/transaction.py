from fastapi import APIRouter, Depends, HTTPException, Form, Path, Query
from pydantic import BaseModel, Field, validator
from fastapi.encoders import jsonable_encoder
from ..utils.auth import get_api_key
from ..database import insert_transaction, get_transaction_by_id, get_transactions, search_transactions_by_amount, search_transactions_by_date_range, search_transactions_by_type, get_total_transaction_amount, get_transaction_summary
from server.models.transaction import TransactionResponseDetails, Transaction, AmountDetails, Currency, Country, TransactionType, DeviceData, Tag
import random
from datetime import datetime
import threading
import time

router = APIRouter()


class TransactionRequest(BaseModel):
    amount: float = Field(..., gt=0, description="The amount for the transaction")
    sender_id: str = Field(..., description="The ID of the sender")
    destination_id: str = Field(..., description="The ID of the receiver")
    type: TransactionType
    currency: Currency
    country: Country


class ReportRequest(BaseModel):
    start_date: datetime
    end_date: datetime

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, end_date, values):
        if 'start_date' in values and end_date <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return end_date

class CronStatus(BaseModel):
    status: str


cron_running = False
cron_thread = None

def generate_transaction():
    while cron_running:
        try:
            transaction_data = Transaction(
                type=TransactionType(random.choice(["WITHDRAW", "DEPOSIT", "TRANSFER", "EXTERNAL_PAYMENT", "REFUND", "OTHER"])),
                transactionId=random.randint(100000, 999999),
                timestamp=datetime.now(),
                originUserId=str(random.randint(1, 100)),
                destinationUserId=str(random.randint(1, 100)),
                originAmountDetails=AmountDetails(
                    transactionAmount=random.uniform(1, 1000),
                    transactionCurrency=Currency("USD"),
                    country=Country("US")
                ),
                destinationAmountDetails=AmountDetails(
                    transactionAmount=random.uniform(1, 1000),
                    transactionCurrency=Currency("USD"),
                    country=Country("US")
                ),
                originDeviceData=DeviceData(),
                destinationDeviceData=DeviceData(),
                tags=[Tag()]
            )
            insert_transaction(transaction_data.dict(), transaction_data.transactionId)
            time.sleep(1)
        except Exception as e:
            print(f"An error occurred while generating transaction: {e}")
            
            
            
@router.post("/cron/start", response_model=CronStatus, dependencies=[Depends(get_api_key)])
async def start_cron():
    global cron_running, cron_thread
    if not cron_running:
        cron_running = True
        cron_thread = threading.Thread(target=generate_transaction)
        cron_thread.start()
    return {"status": "CRON job started"}

@router.post("/cron/stop", response_model=CronStatus, dependencies=[Depends(get_api_key)])
async def stop_cron():
    global cron_running
    cron_running = False
    if cron_thread:
        cron_thread.join()
    return {"status": "CRON job stopped"}


@router.post("/create_transactions", dependencies=[Depends(get_api_key)])
async def create_transaction(transaction_request: TransactionRequest):
    try:
        transaction_data = Transaction(
            type=transaction_request.type,
            transactionId=random.randint(100000, 999999),
            timestamp=datetime.now(),
            originUserId=transaction_request.sender_id,
            destinationUserId=transaction_request.destination_id,
            originAmountDetails=AmountDetails(
                transactionAmount=transaction_request.amount,
                transactionCurrency=transaction_request.currency,
                country=transaction_request.country
            ),
            destinationAmountDetails=AmountDetails(
                transactionAmount=transaction_request.amount,
                transactionCurrency=transaction_request.currency,
                country=transaction_request.country
            ),
            originDeviceData=DeviceData(),
            destinationDeviceData=DeviceData(),
            tags=[Tag()]
        )
        
        transaction_id = insert_transaction(transaction_data.dict(), transaction_data.transactionId)
        
        if not transaction_id:
            raise HTTPException(status_code=400, detail="Transaction could not be created")

        transaction_data = get_transactions(transaction_id)
        if not transaction_data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return jsonable_encoder(transaction_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_transactions/{transaction_id}", dependencies=[Depends(get_api_key)])
async def retrieve_transaction(transaction_id: int):
    try:
        transaction_data = get_transactions(transaction_id)
        if not transaction_data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return jsonable_encoder(transaction_data)
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

@router.get("/search_transaction_by_type", dependencies=[Depends(get_api_key)])
async def transactions_by_type(type: str = Query(..., description="The type of transactions to search for")):
    try:
        transactions = search_transactions_by_type(type)
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found")
        
        return [format_search_result(transaction) for transaction in transactions]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions/summary", dependencies=[Depends(get_api_key)])
async def transaction_summary(report_request: ReportRequest = Depends()):
    try:
        summary = get_transaction_summary(report_request.start_date, report_request.end_date)
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions/total_amount", dependencies=[Depends(get_api_key)])
async def total_transaction_amount(report_request: ReportRequest = Depends()):
    try:
        total_amount = get_total_transaction_amount(report_request.start_date, report_request.end_date)
        return {"total_amount": total_amount}
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