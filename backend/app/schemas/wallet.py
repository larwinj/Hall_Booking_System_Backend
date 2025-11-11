from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.wallet import TransactionType, TransactionStatus

class WalletBase(BaseModel):
    balance: float = Field(..., ge=0, description="Current wallet balance")

class WalletOut(WalletBase):
    id: int = Field(..., ge=1, description="Unique ID of the wallet")
    user_id: int = Field(..., ge=1, description="ID of the user who owns this wallet")
    created_at: datetime = Field(..., description="When the wallet was created")
    updated_at: datetime = Field(..., description="When the wallet was last updated")

    class Config:
        from_attributes = True

class WalletTransactionBase(BaseModel):
    amount: float = Field(..., description="Transaction amount (positive for credit, negative for debit)")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    description: Optional[str] = Field(None, description="Description of the transaction")
    # reference_id: Optional[str] = Field(None, description="External reference ID")

class WalletTransactionCreate(WalletTransactionBase):
    wallet_id: int = Field(..., ge=1, description="ID of the wallet")
    booking_id: Optional[int] = Field(None, ge=1, description="ID of the related booking")

class WalletTransactionOut(WalletTransactionBase):
    id: int = Field(..., ge=1, description="Unique ID of the transaction")
    wallet_id: int = Field(..., ge=1, description="ID of the wallet")
    booking_id: Optional[int] = Field(None, ge=1, description="ID of the related booking")
    status: TransactionStatus = Field(..., description="Status of the transaction")
    created_at: datetime = Field(..., description="When the transaction was created")

    class Config:
        from_attributes = True

class WalletWithTransactions(WalletOut):
    transactions: list[WalletTransactionOut] = Field(default_factory=list, description="List of wallet transactions")

class RefundCalculation(BaseModel):
    original_amount: float = Field(..., ge=0, description="Original booking amount")
    refund_percentage: float = Field(..., ge=0, le=100, description="Refund percentage applied")
    refund_amount: float = Field(..., ge=0, description="Calculated refund amount")
    cancellation_fee: float = Field(..., ge=0, description="Cancellation fee deducted")
    hours_until_booking: float = Field(..., description="Hours remaining until booking start")
    refund_policy_applied: str = Field(..., description="Description of refund policy applied")