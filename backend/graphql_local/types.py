import strawberry
from typing import Optional

@strawberry.type
class FinancialData:
    country_code: str
    region: str
    amount: float
    transaction_type: str
    payment_successful: bool
    gateway_fee: float
    fraud_score: float
    date_time: str
    currency: Optional[str] = None  # Add this if it's part of the table
