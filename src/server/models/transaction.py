from pydantic import BaseModel
from typing import Optional, List, Dict


class AmountDetails(BaseModel):
    transactionAmount: float
    transactionCurrency: str
    country: str


class DeviceData(BaseModel):
    batteryLevel: int
    deviceLatitude: float
    deviceLongitude: float
    ipAddress: str
    deviceIdentifier: str
    vpnUsed: bool
    operatingSystem: str
    deviceMaker: str
    deviceModel: str
    deviceYear: str
    appVersion: str


class Tag(BaseModel):
    key: str
    value: str


class RuleMeta(BaseModel):
    vars: Optional[List[Dict[str, str]]]
    labels: Optional[List[str]]
    nature: Optional[str]
    isShadow: Optional[bool]


class FalsePositiveDetails(BaseModel):
    isFalsePositive: bool
    confidenceScore: Optional[float]


class SanctionsDetails(BaseModel):
    name: str
    searchId: str
    iban: Optional[str]
    entityType: Optional[str]


class Rule(BaseModel):
    ruleInstanceId: str
    ruleName: str
    ruleDescription: str
    ruleAction: str
    ruleHit: bool
    ruleId: Optional[str]
    ruleHitMeta: Optional[RuleMeta]
    hitDirections: Optional[List[str]]
    falsePositiveDetails: Optional[FalsePositiveDetails]
    sanctionsDetails: Optional[List[SanctionsDetails]]
    isOngoingScreeningHit: Optional[bool]


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
    timestamp: int
    originUserId: str
    destinationUserId: str
    originAmountDetails: AmountDetails
    destinationAmountDetails: AmountDetails
    description: str
    promotionCodeUsed: Optional[bool] = None
    reference: Optional[str] = None
    originDeviceData: Optional[DeviceData] = None
    destinationDeviceData: Optional[DeviceData] = None
    tags: Optional[List[Tag]] = None
