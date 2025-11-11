from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Dict, Any
from app.models.wallet import Wallet, WalletTransaction, TransactionType, TransactionStatus
from app.models.booking import Booking
from app.models.user import User
from app.models.room import Room
from app.models.booking_addon import BookingAddon
from app.models.booking_reschedule_history import BookingRescheduleHistory

class WalletService:
    
    @staticmethod
    async def get_or_create_wallet(db: AsyncSession, user_id: int) -> Wallet:
        """
        Get user's wallet or create one if it doesn't exist
        """
        result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
        wallet = result.scalar_one_or_none()
        
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=0.0)
            db.add(wallet)
            await db.commit()
            await db.refresh(wallet)
        
        return wallet

    @staticmethod
    async def calculate_refund_amount(
        booking: Booking,
        cancellation_time: datetime = None
    ) -> Tuple[float, float, str]:
        """
        Calculate refund amount based on cancellation policy
        
        Refund Policy:
        - More than 48 hours before booking: 75% refund
        - 24-48 hours before booking: 50% refund  
        - Less than 24 hours before booking: 25% refund
        
        Returns:
            Tuple of (refund_amount, cancellation_fee, policy_description)
        """
        if cancellation_time is None:
            cancellation_time = datetime.now(timezone.utc)
        
        # Calculate hours until booking starts
        time_until_booking = booking.start_time - cancellation_time
        hours_until_booking = time_until_booking.total_seconds() / 3600
        
        original_amount = booking.total_cost
        
        if hours_until_booking > 48:
            # More than 2 days (48 hours)
            refund_percentage = 75
            refund_amount = original_amount * 0.75
            cancellation_fee = original_amount * 0.25
            policy_description = "Cancelled more than 48 hours before booking - 75% refund"
            
        elif hours_until_booking > 24:
            # 24-48 hours
            refund_percentage = 50
            refund_amount = original_amount * 0.50
            cancellation_fee = original_amount * 0.50
            policy_description = "Cancelled 24-48 hours before booking - 50% refund"
            
        else:
            # Less than 24 hours
            refund_percentage = 25
            refund_amount = original_amount * 0.25
            cancellation_fee = original_amount * 0.75
            policy_description = "Cancelled less than 24 hours before booking - 25% refund"
        
        return refund_amount, cancellation_fee, policy_description

    @staticmethod
    async def process_booking_refund(
        db: AsyncSession,
        booking: Booking,
        user_id: int,
        cancellation_reason: str = None
    ) -> Tuple[WalletTransaction, float, str]:
        """
        Process refund for a cancelled booking and add amount to user's wallet
        """
        # Calculate refund amount
        refund_amount, cancellation_fee, policy_description = await WalletService.calculate_refund_amount(booking)
        
        if refund_amount <= 0:
            raise ValueError("No refund available for this booking")
        
        # Get or create user's wallet
        wallet = await WalletService.get_or_create_wallet(db, user_id)
        
        # Create refund transaction
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            booking_id=booking.id,
            amount=refund_amount,
            transaction_type=TransactionType.REFUND,
            status=TransactionStatus.COMPLETED,
            description=f"Booking cancellation refund: {policy_description}. Reason: {cancellation_reason or 'Not specified'}"
        )
        
        # Update wallet balance
        wallet.balance += refund_amount
        wallet.updated_at = datetime.now(timezone.utc)
        
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        await db.refresh(wallet)
        
        return transaction, refund_amount, policy_description

    @staticmethod
    async def get_wallet_balance(db: AsyncSession, user_id: int) -> Wallet:
        """
        Get user's wallet with current balance
        """
        return await WalletService.get_or_create_wallet(db, user_id)

    @staticmethod
    async def get_wallet_transactions(
        db: AsyncSession, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[WalletTransaction]:
        """
        Get user's wallet transactions with pagination
        """
        wallet = await WalletService.get_or_create_wallet(db, user_id)
        
        result = await db.execute(
            select(WalletTransaction)
            .where(WalletTransaction.wallet_id == wallet.id)
            .order_by(WalletTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        return result.scalars().all()

    @staticmethod
    async def add_funds_to_wallet(
        db: AsyncSession,
        user_id: int,
        amount: float,
        description: str = None,
        reference_id: str = None
    ) -> WalletTransaction:
        """
        Add funds to user's wallet (for manual adjustments, etc.)
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        wallet = await WalletService.get_or_create_wallet(db, user_id)
        
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,
            transaction_type=TransactionType.ADJUSTMENT,
            status=TransactionStatus.COMPLETED,
            description=description or "Manual fund addition",
            reference_id=reference_id
        )
        
        wallet.balance += amount
        wallet.updated_at = datetime.now(timezone.utc)
        
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        
        return transaction
    
    @staticmethod
    async def process_reschedule_refund(
        db: AsyncSession,
        booking: Booking,
        user_id: int,
        original_total_cost: float,
        new_total_cost: float,
        description: str = "Reschedule price difference refund"
    ) -> Tuple[Optional[WalletTransaction], float, float]:
        """
        Process refund for reschedule when new booking cost is lower
        Returns: (transaction, refund_amount, price_difference)
        """
        price_difference = original_total_cost - new_total_cost
        refund_amount = price_difference if price_difference > 0 else 0
        
        if refund_amount <= 0:
            return None, 0, price_difference
        
        # Get or create user's wallet
        wallet = await WalletService.get_or_create_wallet(db, user_id)
        
        # Create refund transaction
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            booking_id=booking.id,
            amount=refund_amount,
            transaction_type=TransactionType.REFUND,
            status=TransactionStatus.COMPLETED,
            description=description
        )
        
        # Update wallet balance
        wallet.balance += refund_amount
        wallet.updated_at = datetime.now(timezone.utc)
        
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        await db.refresh(wallet)
        
        return transaction, refund_amount, price_difference


    @staticmethod
    async def process_reschedule_payment(
        db: AsyncSession,
        booking: Booking,
        user_id: int,
        original_total_cost: float,
        new_total_cost: float,
        description: str = "Reschedule additional payment"
    ) -> Tuple[Optional[WalletTransaction], float, float]:
        """
        Process payment for reschedule when new booking cost is higher
        Returns: (transaction, additional_amount, price_difference)
        """
        price_difference = new_total_cost - original_total_cost
        additional_amount = price_difference if price_difference > 0 else 0
        
        if additional_amount <= 0:
            return None, 0, price_difference
        
        # Get user's wallet
        wallet = await WalletService.get_or_create_wallet(db, user_id)
        
        # Calculate how much can be paid from wallet
        wallet_payment = min(wallet.balance, additional_amount)
        remaining_payment = additional_amount - wallet_payment
        
        transaction = None
        
        if wallet_payment > 0:
            # Create payment transaction from wallet
            transaction = WalletTransaction(
                wallet_id=wallet.id,
                booking_id=booking.id,
                amount=-wallet_payment,  # Negative for debit
                transaction_type=TransactionType.PAYMENT,
                status=TransactionStatus.COMPLETED,
                description=f"{description} (from wallet)"
            )
            
            # Update wallet balance
            wallet.balance -= wallet_payment
            wallet.updated_at = datetime.now(timezone.utc)
            
            db.add(transaction)
            await db.commit()
            await db.refresh(transaction)
            await db.refresh(wallet)
        
        return transaction, remaining_payment, price_difference

    @staticmethod
    async def validate_room_change(
        db: AsyncSession,
        original_room_id: int,
        new_room_id: int
    ) -> bool:
        """
        Validate that new room is in the same venue as original room
        """
        if original_room_id == new_room_id:
            return True
        
        # Get venue IDs for both rooms
        original_room_result = await db.execute(
            select(Room.venue_id).where(Room.id == original_room_id)
        )
        original_venue_id = original_room_result.scalar_one_or_none()
        
        new_room_result = await db.execute(
            select(Room.venue_id).where(Room.id == new_room_id)
        )
        new_venue_id = new_room_result.scalar_one_or_none()
        
        if not original_venue_id or not new_venue_id:
            return False
        
        return original_venue_id == new_venue_id

    @staticmethod
    async def get_reschedule_cost_breakdown(
        db: AsyncSession,
        booking: Booking,
        new_room_id: int,
        new_start_time: datetime,
        new_end_time: datetime
    ) -> Dict[str, Any]:
        """
        Calculate cost breakdown for reschedule including room change
        """
        from app.services.booking import calculate_total_cost
        
        # Get current booking addons
        addons_pairs = []
        addons_result = await db.execute(
            select(BookingAddon).where(BookingAddon.booking_id == booking.id)
        )
        addons = addons_result.scalars().all()
        if addons:
            addons_pairs = [(a.addon_id, a.quantity) for a in addons]
        
        # Calculate new total cost
        new_total_cost, recalculated_addons = await calculate_total_cost(
            db, 
            room_id=new_room_id, 
            start_time=new_start_time, 
            end_time=new_end_time, 
            addons=addons_pairs
        )
        
        price_difference = new_total_cost - booking.total_cost
        
        return {
            "original_cost": booking.total_cost,
            "new_cost": new_total_cost,
            "price_difference": price_difference,
            "is_refund": price_difference < 0,
            "refund_amount": abs(price_difference) if price_difference < 0 else 0,
            "additional_amount": price_difference if price_difference > 0 else 0,
            "recalculated_addons": recalculated_addons
        }
        
    @staticmethod
    async def create_reschedule_history(
        db: AsyncSession,
        booking: Booking,
        original_room_id: int,
        original_start_time: datetime,
        original_end_time: datetime,
        original_total_cost: float,
        new_room_id: int,
        new_start_time: datetime,
        new_end_time: datetime,
        new_total_cost: float,
        price_difference: float,
        refund_amount: float,
        additional_amount: float,
        reschedule_reason: str = None
    ) -> BookingRescheduleHistory:
        """
        Create a reschedule history record
        """
        history = BookingRescheduleHistory(
            booking_id=booking.id,
            original_room_id=original_room_id,
            original_start_time=original_start_time,
            original_end_time=original_end_time,
            original_total_cost=original_total_cost,
            new_room_id=new_room_id,
            new_start_time=new_start_time,
            new_end_time=new_end_time,
            new_total_cost=new_total_cost,
            price_difference=price_difference,
            refund_amount=refund_amount,
            additional_amount=additional_amount,
            reschedule_reason=reschedule_reason
        )
        
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history
    
    @staticmethod
    async def get_booking_reschedule_history(
        db: AsyncSession,
        booking_id: int
    ) -> list[BookingRescheduleHistory]:
        """
        Get reschedule history for a booking
        """
        result = await db.execute(
            select(BookingRescheduleHistory)
            .where(BookingRescheduleHistory.booking_id == booking_id)
            .order_by(BookingRescheduleHistory.created_at.desc())
        )
        return result.scalars().all()