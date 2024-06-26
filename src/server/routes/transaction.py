import logging
import random
from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, logger
from typing import Optional
import asyncio
import json
from datetime import datetime
from ..database import create_tables

router = APIRouter()
create_tables()

@router.post("/create_transactions", dependencies=[Depends(get_api_key)],response_model=TransactionResponseDetails)
async def create_transaction(transaction: Transaction):
    try:
        response = await verify_transaction(transaction.dict())
        return TransactionResponseDetails(
            executedRules=response.get("executedRules"),
            hitRules=response.get("hitRules"),
            status=response.get("status"),
            transactionId=response.get("transactionId"),
            message=response.get("message"),
            riskScoreDetails=response.get("riskScoreDetails")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
