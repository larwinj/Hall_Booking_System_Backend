from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.wallet_service import WalletService
from app.schemas.wallet import WalletOut, WalletTransactionOut, WalletWithTransactions

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