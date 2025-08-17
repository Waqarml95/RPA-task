"""API data models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AccountType(str, Enum):
    """Account type enumeration."""

    CHECKING = "Checking"
    SAVINGS = "Savings"
    CORPORATE = "Corporate"
    CREDIT = "Credit"


class TransactionType(str, Enum):
    """Transaction type enumeration."""

    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"
    TRANSFER = "Transfer"
    PAYMENT = "Payment"
    FEE = "Fee"


class Account(BaseModel):
    """Account model."""

    account_id: str = Field(..., alias="id")
    account_number: str
    account_type: AccountType
    balance: float
    available_balance: Optional[float] = None
    status: str = "Active"
    currency: str = "USD"
    created_date: Optional[datetime] = None
    last_activity: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True
        use_enum_values = True


class Transaction(BaseModel):
    """Transaction model."""

    transaction_id: str = Field(..., alias="id")
    account_id: str
    date: datetime
    amount: float
    transaction_type: TransactionType
    description: str
    balance_after: Optional[float] = None
    reference: Optional[str] = None
    status: str = "Completed"

    class Config:
        """Pydantic config."""

        populate_by_name = True
        use_enum_values = True


class TransferRequest(BaseModel):
    """Transfer request model."""

    from_account: str
    to_account: str
    amount: float
    description: Optional[str] = ""
    scheduled_date: Optional[datetime] = None


class TransferConfirmation(BaseModel):
    """Transfer confirmation model."""

    confirmation_number: str
    from_account: str
    to_account: str
    amount: float
    description: str
    status: str
    timestamp: datetime
    fee: Optional[float] = 0.0


class ApiResponse(BaseModel):
    """Generic API response model."""

    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class CardProduct(BaseModel):
    """Card product model."""

    card_id: str
    name: str
    card_type: str
    features: list[str]
    terms: str
    apr: Optional[float] = None
    annual_fee: Optional[float] = None
    promotions: Optional[list[str]] = None