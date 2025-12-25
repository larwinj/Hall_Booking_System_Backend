from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timezone
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.wallet import TransactionType, TransactionStatus
from app.services.wallet_service import WalletService
from app.schemas.wallet import WalletOut, WalletTransactionOut, WalletWithTransactions, WalletPaymentRequest, WalletPaymentResponse

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.get("/balance", response_model=WalletOut, description="Access by authenticated users - Get current wallet balance")
async def get_wallet_balance(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current wallet balance for the authenticated user
    """
    wallet = await WalletService.get_wallet_balance(db, user.id)
    return wallet

@router.get("/transactions", response_model=List[WalletTransactionOut], description="Access by authenticated users - Get wallet transactions")
async def get_wallet_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get wallet transactions for the authenticated user
    """
    transactions = await WalletService.get_wallet_transactions(db, user.id, skip, limit)
    return transactions

@router.get("/details", response_model=WalletWithTransactions, description="Access by authenticated users - Get wallet details with recent transactions")
async def get_wallet_details(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete wallet details including balance and recent transactions
    """
    wallet = await WalletService.get_wallet_balance(db, user.id)
    transactions = await WalletService.get_wallet_transactions(db, user.id, limit=10)
    
    return WalletWithTransactions(
        **wallet.__dict__,
        transactions=transactions
    )

@router.post("/pay", response_model=WalletPaymentResponse, description="Access by authenticated users - Process payment from wallet")
async def process_wallet_payment(
    payment: WalletPaymentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process payment from wallet for booking.
    If wallet balance is sufficient, deducts full amount.
    If wallet balance is insufficient, deducts available balance and returns remaining amount.
    """
    wallet = await WalletService.get_or_create_wallet(db, user.id)
    
    if wallet.balance <= 0:
        return WalletPaymentResponse(
            success=False,
            transaction=None,
            wallet_balance=wallet.balance,
            amount_paid=0,
            remaining_amount=payment.amount,
            message="No wallet balance available"
        )
    
    # Calculate how much can be paid from wallet
    amount_to_pay = min(wallet.balance, payment.amount)
    remaining_amount = payment.amount - amount_to_pay
    
    # Create payment transaction (negative amount for debit)
    from app.models.wallet import WalletTransaction
    transaction = WalletTransaction(
        wallet_id=wallet.id,
        amount=-amount_to_pay,  # Negative for debit
        transaction_type=TransactionType.PAYMENT,
        status=TransactionStatus.COMPLETED,
        description=payment.description
    )
    
    # Deduct from wallet
    wallet.balance -= amount_to_pay
    wallet.updated_at = datetime.now(timezone.utc)
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    await db.refresh(wallet)
    
    # Convert transaction to output schema
    transaction_out = WalletTransactionOut(
        id=transaction.id,
        wallet_id=transaction.wallet_id,
        booking_id=transaction.booking_id,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        status=transaction.status,
        description=transaction.description,
        created_at=transaction.created_at
    )
    
    if remaining_amount > 0:
        return WalletPaymentResponse(
            success=True,
            transaction=transaction_out,
            wallet_balance=wallet.balance,
            amount_paid=amount_to_pay,
            remaining_amount=remaining_amount,
            message=f"Partial payment of ₹{amount_to_pay:.2f} from wallet. Remaining ₹{remaining_amount:.2f} to pay via other method."
        )
    
    return WalletPaymentResponse(
        success=True,
        transaction=transaction_out,
        wallet_balance=wallet.balance,
        amount_paid=amount_to_pay,
        remaining_amount=0,
        message=f"Full payment of ₹{amount_to_pay:.2f} processed from wallet."
    )