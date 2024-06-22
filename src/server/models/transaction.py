from pydantic import BaseModel
from typing import Optional, Dict

class AmountDetails(BaseModel):
    amount: float
    currency: str

class PaymentDetails(BaseModel):
    type: str
    details: Dict[str, str]

class Transaction(BaseModel):
    type: str
    transactionId: Optional[str]
    timestamp: int
    transactionState: Optional[str] = "CREATED"
    originUserId: str
    destinationUserId: str
    originAmountDetails: AmountDetails
    destinationAmountDetails: AmountDetails
    originPaymentDetails: PaymentDetails
    destinationPaymentDetails: PaymentDetails
