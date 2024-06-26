from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, date
from enum import Enum

class TransactionType(str, Enum):
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"
    TRANSFER = "TRANSFER"
    EXTERNAL_PAYMENT = "EXTERNAL_PAYMENT"
    REFUND = "REFUND"
    OTHER = "OTHER"


class Currency(str, Enum):
    EUR = "EUR"
    USD = "USD"
    INR = "INR"


class Country(str, Enum):
    DE = "DE"  
    IN = "IN"  
    US = "US"  

class AmountDetails(BaseModel):
    transactionAmount: float
    transactionCurrency: Currency
    country: Country


class DeviceData(BaseModel):
    batteryLevel: float=95.0
    deviceLatitude: float=13.0033
    deviceLongitude: float=76.1004
    ipAddress: str="10.23.191.2"
    deviceIdentifier: str="3c49f915d04485e34caba"
    vpnUsed: bool=False
    operatingSystem: str="Android 11.2"
    deviceMaker: str="ASUS"
    deviceModel: str="Zenphone M2 Pro Max"
    deviceYear: str="2018"
    appVersion: str="1.1.0"


class Tag(BaseModel):
    key: str="customKey"
    value: str="customValue"

class FalsePositiveDetails(BaseModel):
    isFalsePositive: bool
    confidenceScore: Optional[float]

class RuleMeta(BaseModel):
    vars: Optional[List[Dict[str, str]]]
    labels: Optional[List[str]]
    nature: Optional[str]
    isShadow: Optional[bool]

class SanctionsDetails(BaseModel):
    name: str
    searchId: str
    iban: Optional[str]
    entityType: Optional[str]

class Actions(BaseModel):
    ALLOW="ALLOW"
    FLAG="FLAG"
    BLOCK="BLOCK"
    SUSPEND="SUSPEND"

class Rule(BaseModel):
    ruleInstanceId: str="ruleInstanceId"
    ruleName: str="Proof of funds for high value transactions"
    ruleDescription: str="If a user makes a remittance transaction >= 1800 in EUR - ask for proof of funds"
    ruleAction: Actions
    ruleHit: bool=True
    ruleId: Optional[str]="R-1a"
    hitDirections: Optional[List[str]]
    falsePositiveDetails: Optional[FalsePositiveDetails]
    sanctionsDetails: Optional[List[SanctionsDetails]]
    isOngoingScreeningHit: Optional[bool]
    labels: Optional[List[str]]
    nature: Optional[str]
    isShadow: Optional[bool]


class RiskScoreDetails(BaseModel):
    trsScore: float
    trsRiskLevel: str


class TransactionResponseDetails(BaseModel):
    executedRules: List[Rule]
    hitRules: List[Rule]
    status: str
    transactionId: str
    message: Optional[str]
    riskScoreDetails: Optional[RiskScoreDetails]


class Transaction(BaseModel):
    type: str
    transactionId: Optional[str] = None
    timestamp: Optional[datetime] = None
    originUserId: Optional[str] = None
    destinationUserId: Optional[str] = None
    originAmountDetails: AmountDetails
    destinationAmountDetails: AmountDetails
    description: str
    promotionCodeUsed: Optional[bool] = False
    reference: Optional[str] = None
    originDeviceData: Optional[DeviceData] = None
    destinationDeviceData: Optional[DeviceData] = None
    tags: Optional[List[Tag]] = None
