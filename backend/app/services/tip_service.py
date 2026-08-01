"""
Tip Service
Task 5.2: Tipping System

Handles tipping, withdrawals, and balance management
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid

from app.models.tip import Tip, TipWithdrawal, UserBalance, TipStatus, WithdrawalStatus, PaymentStatus
from app.models.user import User
from app.models.track import Track
from app.schemas.tip import TipSendRequest, WithdrawalRequest


class TipService:
    """Service for tipping system"""
    
    # Platform fee percentage (2.5%)
    PLATFORM_FEE_PERCENTAGE = 0.025
    
    # Minimum withdrawal amount
    MIN_WITHDRAWAL_AMOUNT = 10.0
    
    @staticmethod
    def send_tip(db: Session, from_user_id: str, request: TipSendRequest) -> Tip:
        """Send a tip to another user"""
        
        # Verify recipient exists
        to_user = db.query(User).filter(User.id == request.to_user_id).first()
        if not to_user:
            raise ValueError("Recipient user not found")
        
        # Can't tip yourself
        if from_user_id == request.to_user_id:
            raise ValueError("Cannot tip yourself")
        
        # Verify track exists if provided
        if request.track_id:
            track = db.query(Track).filter(
                Track.id == request.track_id,
                Track.user_id == request.to_user_id
            ).first()
            if not track:
                raise ValueError("Track not found or doesn't belong to recipient")
        
        # Calculate platform fee and net amount
        platform_fee = request.amount * TipService.PLATFORM_FEE_PERCENTAGE
        net_amount = request.amount - platform_fee
        
        # Create tip
        tip = Tip(
            id=str(uuid.uuid4()),
            from_user_id=from_user_id,
            to_user_id=request.to_user_id,
            amount=request.amount,
            currency=request.currency,
            track_id=request.track_id,
            campaign_id=request.campaign_id,
            message=request.message,
            is_anonymous=request.is_anonymous,
            payment_method=request.payment_method,
            payment_status=PaymentStatus.SUCCEEDED,  # Simulated for now
            payment_provider="simulated",  # Will be Stripe/Paystack in Task 5.1
            platform_fee=platform_fee,
            net_amount=net_amount,
            status=TipStatus.COMPLETED,
            paid_at=datetime.utcnow(),
        )
        
        db.add(tip)
        
        # Update recipient balance
        balance = TipService.get_or_create_balance(db, request.to_user_id)
        balance.available_balance += net_amount
        balance.total_earned += net_amount
        balance.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(tip)
        
        return tip
    
    @staticmethod
    def get_or_create_balance(db: Session, user_id: str) -> UserBalance:
        """Get or create user balance"""
        balance = db.query(UserBalance).filter(UserBalance.user_id == user_id).first()
        
        if not balance:
            balance = UserBalance(
                id=str(uuid.uuid4()),
                user_id=user_id,
                available_balance=0.0,
                pending_balance=0.0,
                total_earned=0.0,
                total_withdrawn=0.0,
            )
            db.add(balance)
            db.commit()
            db.refresh(balance)
        
        return balance
    
    @staticmethod
    def get_user_balance(db: Session, user_id: str) -> Dict[str, Any]:
        """Get user balance with calculated fields"""
        balance = TipService.get_or_create_balance(db, user_id)
        
        # Calculate withdrawable amount (available - pending)
        withdrawable = max(0, balance.available_balance - balance.pending_balance)
        
        return {
            "user_id": balance.user_id,
            "available_balance": balance.available_balance,
            "pending_balance": balance.pending_balance,
            "total_earned": balance.total_earned,
            "total_withdrawn": balance.total_withdrawn,
            "currency": balance.currency,
            "withdrawable_amount": withdrawable,
        }
    
    @staticmethod
    def get_tips_received(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Tip], int, float]:
        """Get tips received by user"""
        query = db.query(Tip).filter(
            Tip.to_user_id == user_id,
            Tip.status == TipStatus.COMPLETED
        )
        
        total = query.count()
        total_amount = db.query(func.sum(Tip.amount)).filter(
            Tip.to_user_id == user_id,
            Tip.status == TipStatus.COMPLETED
        ).scalar() or 0.0
        
        tips = query.order_by(desc(Tip.created_at)).offset(skip).limit(limit).all()
        
        return tips, total, total_amount
    
    @staticmethod
    def get_tips_sent(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Tip], int, float]:
        """Get tips sent by user"""
        query = db.query(Tip).filter(
            Tip.from_user_id == user_id,
            Tip.status == TipStatus.COMPLETED
        )
        
        total = query.count()
        total_amount = db.query(func.sum(Tip.amount)).filter(
            Tip.from_user_id == user_id,
            Tip.status == TipStatus.COMPLETED
        ).scalar() or 0.0
        
        tips = query.order_by(desc(Tip.created_at)).offset(skip).limit(limit).all()
        
        return tips, total, total_amount
    
    @staticmethod
    def get_tip_stats(db: Session, user_id: str) -> Dict[str, Any]:
        """Get tip statistics for user"""
        
        # Tips received
        tips_received = db.query(
            func.count(Tip.id),
            func.sum(Tip.amount)
        ).filter(
            Tip.to_user_id == user_id,
            Tip.status == TipStatus.COMPLETED
        ).first()
        
        tips_received_count = tips_received[0] or 0
        total_received = tips_received[1] or 0.0
        
        # Tips sent
        tips_sent = db.query(
            func.count(Tip.id),
            func.sum(Tip.amount)
        ).filter(
            Tip.from_user_id == user_id,
            Tip.status == TipStatus.COMPLETED
        ).first()
        
        tips_sent_count = tips_sent[0] or 0
        total_sent = tips_sent[1] or 0.0
        
        # Top supporters (people who tipped this user)
        top_supporters_query = db.query(
            Tip.from_user_id,
            User.username,
            User.full_name,
            func.sum(Tip.amount).label('total'),
            func.count(Tip.id).label('count')
        ).join(
            User, Tip.from_user_id == User.id
        ).filter(
            Tip.to_user_id == user_id,
            Tip.status == TipStatus.COMPLETED,
            Tip.is_anonymous == False
        ).group_by(
            Tip.from_user_id, User.username, User.full_name
        ).order_by(
            desc('total')
        ).limit(5).all()
        
        top_supporters = [
            {
                "user_id": supporter.from_user_id,
                "username": supporter.username,
                "full_name": supporter.full_name,
                "total_tipped": float(supporter.total),
                "tip_count": supporter.count,
            }
            for supporter in top_supporters_query
        ]
        
        # Recent tips
        recent_tips = db.query(Tip).filter(
            Tip.to_user_id == user_id,
            Tip.status == TipStatus.COMPLETED
        ).order_by(desc(Tip.created_at)).limit(5).all()
        
        return {
            "total_received": float(total_received),
            "total_sent": float(total_sent),
            "tips_received_count": tips_received_count,
            "tips_sent_count": tips_sent_count,
            "top_supporters": top_supporters,
            "recent_tips": recent_tips,
        }
    
    @staticmethod
    def get_leaderboard(
        db: Session,
        creator_id: str,
        period: str = "all_time",
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get tip leaderboard for a creator"""
        
        # Get creator info
        creator = db.query(User).filter(User.id == creator_id).first()
        if not creator:
            raise ValueError("Creator not found")
        
        # Date filter based on period
        date_filter = None
        if period == "this_month":
            date_filter = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        elif period == "this_week":
            date_filter = datetime.utcnow() - timedelta(days=7)
        
        query = db.query(
            Tip.from_user_id,
            User.username,
            Tip.is_anonymous,
            func.sum(Tip.amount).label('total'),
            func.count(Tip.id).label('count')
        ).outerjoin(
            User, Tip.from_user_id == User.id
        ).filter(
            Tip.to_user_id == creator_id,
            Tip.status == TipStatus.COMPLETED
        )
        
        if date_filter:
            query = query.filter(Tip.created_at >= date_filter)
        
        query = query.group_by(
            Tip.from_user_id, User.username, Tip.is_anonymous
        ).order_by(desc('total')).limit(limit)
        
        supporters = query.all()
        
        # Format leaderboard
        leaderboard = []
        for rank, supporter in enumerate(supporters, 1):
            leaderboard.append({
                "rank": rank,
                "user_id": supporter.from_user_id if not supporter.is_anonymous else "anonymous",
                "username": supporter.username if not supporter.is_anonymous else "Anonymous Supporter",
                "total_tipped": float(supporter.total),
                "tip_count": supporter.count,
                "is_anonymous": supporter.is_anonymous,
            })
        
        # Total stats
        total_query = db.query(
            func.sum(Tip.amount),
            func.count(func.distinct(Tip.from_user_id))
        ).filter(
            Tip.to_user_id == creator_id,
            Tip.status == TipStatus.COMPLETED
        )
        
        if date_filter:
            total_query = total_query.filter(Tip.created_at >= date_filter)
        
        totals = total_query.first()
        
        return {
            "creator_id": creator_id,
            "creator_name": creator.username or creator.full_name,
            "period": period,
            "top_supporters": leaderboard,
            "total_tips": float(totals[0] or 0),
            "total_supporters": totals[1] or 0,
        }
    
    @staticmethod
    def request_withdrawal(
        db: Session,
        user_id: str,
        request: WithdrawalRequest
    ) -> TipWithdrawal:
        """Request withdrawal of tips"""
        
        # Check balance
        balance = TipService.get_or_create_balance(db, user_id)
        withdrawable = balance.available_balance - balance.pending_balance
        
        if request.amount > withdrawable:
            raise ValueError(f"Insufficient balance. Available: ${withdrawable:.2f}")
        
        if request.amount < TipService.MIN_WITHDRAWAL_AMOUNT:
            raise ValueError(f"Minimum withdrawal amount is ${TipService.MIN_WITHDRAWAL_AMOUNT}")
        
        # Create withdrawal request
        withdrawal = TipWithdrawal(
            id=str(uuid.uuid4()),
            user_id=user_id,
            amount=request.amount,
            currency=balance.currency,
            withdrawal_method=request.withdrawal_method,
            account_details=request.account_details,  # Should be encrypted in production
            notes=request.notes,
            status=WithdrawalStatus.PENDING,
        )
        
        db.add(withdrawal)
        
        # Update pending balance
        balance.pending_balance += request.amount
        balance.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(withdrawal)
        
        return withdrawal
    
    @staticmethod
    def get_user_withdrawals(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[TipWithdrawal], int]:
        """Get user's withdrawal requests"""
        query = db.query(TipWithdrawal).filter(TipWithdrawal.user_id == user_id)
        
        total = query.count()
        withdrawals = query.order_by(desc(TipWithdrawal.created_at)).offset(skip).limit(limit).all()
        
        return withdrawals, total
