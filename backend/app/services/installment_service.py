"""
Installment Payment Service
3-month payment plans for beats and products
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class InstallmentPlan(str, Enum):
    """Available installment plans"""
    MONTHLY_3 = "3_months"  # 3 monthly payments
    MONTHLY_6 = "6_months"  # 6 monthly payments
    WEEKLY_4 = "4_weeks"    # 4 weekly payments


class InstallmentService:
    """Manage installment payments for products"""
    
    # Installment configurations
    PLANS = {
        InstallmentPlan.MONTHLY_3: {
            "duration_days": 90,
            "interval_days": 30,
            "payments": 3,
            "interest_rate": 0.0,  # No interest for first 3 months
            "description": "Pay in 3 monthly installments"
        },
        InstallmentPlan.MONTHLY_6: {
            "duration_days": 180,
            "interval_days": 30,
            "payments": 6,
            "interest_rate": 0.05,  # 5% interest
            "description": "Pay in 6 monthly installments"
        },
        InstallmentPlan.WEEKLY_4: {
            "duration_days": 28,
            "interval_days": 7,
            "payments": 4,
            "interest_rate": 0.02,  # 2% interest
            "description": "Pay in 4 weekly installments"
        }
    }
    
    @staticmethod
    def calculate_payment_schedule(
        product_price: Decimal,
        plan: InstallmentPlan,
        start_date: datetime = None
    ) -> Dict[str, Any]:
        """Calculate payment schedule for installment plan"""
        
        if start_date is None:
            start_date = datetime.now()
        
        plan_config = InstallmentService.PLANS[plan]
        
        # Add interest if applicable
        interest_amount = product_price * Decimal(str(plan_config["interest_rate"]))
        total_amount = product_price + interest_amount
        
        # Calculate payment amount
        payment_amount = total_amount / plan_config["payments"]
        
        # Generate payment schedule
        schedule = []
        for i in range(plan_config["payments"]):
            payment_date = start_date + timedelta(
                days=plan_config["interval_days"] * i
            )
            
            # Last payment gets rounding adjustments
            if i == plan_config["payments"] - 1:
                amount = total_amount - (payment_amount * (plan_config["payments"] - 1))
            else:
                amount = payment_amount
            
            schedule.append({
                "payment_number": i + 1,
                "due_date": payment_date.isoformat(),
                "amount": float(amount),
                "status": "pending",
                "paid_date": None
            })
        
        return {
            "plan": plan,
            "product_price": float(product_price),
            "total_amount": float(total_amount),
            "interest_amount": float(interest_amount),
            "interest_rate": plan_config["interest_rate"],
            "payment_amount": float(payment_amount),
            "total_payments": plan_config["payments"],
            "duration_days": plan_config["duration_days"],
            "start_date": start_date.isoformat(),
            "end_date": (start_date + timedelta(days=plan_config["duration_days"])).isoformat(),
            "description": plan_config["description"],
            "schedule": schedule
        }
    
    @staticmethod
    def get_available_plans() -> Dict[str, Dict[str, Any]]:
        """Get all available installment plans with details"""
        plans = {}
        for plan_name, config in InstallmentService.PLANS.items():
            plans[plan_name] = config
        return plans
    
    @staticmethod
    def validate_installment_plan(
        product_price: Decimal,
        plan: InstallmentPlan
    ) -> bool:
        """Validate if product is eligible for installment"""
        
        # Minimum price check (e.g., ₦500 minimum)
        min_price = Decimal("500")
        if product_price < min_price:
            logger.warning(f"Product price {product_price} below minimum for installment")
            return False
        
        # Maximum price check (optional)
        max_price = Decimal("500000")
        if product_price > max_price:
            logger.warning(f"Product price {product_price} exceeds maximum for installment")
            return False
        
        # Plan validation
        if plan not in InstallmentService.PLANS:
            logger.warning(f"Invalid installment plan: {plan}")
            return False
        
        return True
    
    @staticmethod
    def process_payment(
        installment_id: str,
        payment_number: int,
        amount: Decimal,
        payment_reference: str
    ) -> Dict[str, Any]:
        """Process installment payment"""
        
        try:
            result = {
                "success": True,
                "installment_id": installment_id,
                "payment_number": payment_number,
                "amount": float(amount),
                "reference": payment_reference,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            
            logger.info(f"Installment payment processed: {result}")
            return result
        except Exception as e:
            logger.error(f"Installment payment error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_payment_status(installment_id: str) -> Dict[str, Any]:
        """Get payment status for installment"""
        
        # In production, fetch from database
        return {
            "installment_id": installment_id,
            "status": "active",
            "total_payments": 3,
            "payments_completed": 1,
            "next_payment_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "next_payment_amount": 1000.0,
            "remaining_balance": 2000.0
        }
    
    @staticmethod
    def handle_missed_payment(installment_id: str) -> Dict[str, Any]:
        """Handle missed payment"""
        
        logger.warning(f"Missed payment for installment: {installment_id}")
        
        return {
            "status": "overdue",
            "action": "send_reminder",
            "penalty": 50.0,  # Late fee
            "grace_period_days": 5
        }
    
    @staticmethod
    def calculate_early_payoff(
        remaining_payments: List[Dict[str, Any]]
    ) -> float:
        """Calculate early payoff amount with interest reduction"""
        
        total = sum(float(payment["amount"]) for payment in remaining_payments)
        # Reduce interest for early payoff
        discount = total * 0.05  # 5% discount for early payoff
        return float(total - discount)
    
    @staticmethod
    def cancel_installment(installment_id: str, reason: str) -> bool:
        """Cancel installment plan"""
        
        try:
            logger.info(f"Cancelling installment {installment_id}: {reason}")
            # In production, update database status
            return True
        except Exception as e:
            logger.error(f"Cancel installment error: {str(e)}")
            return False
    
    @staticmethod
    def send_payment_reminder(
        installment_id: str,
        customer_email: str,
        payment_number: int,
        amount: float,
        due_date: str
    ) -> bool:
        """Send payment reminder to customer"""
        
        try:
            # In production, integrate with email service
            logger.info(
                f"Payment reminder sent to {customer_email} for installment {installment_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Send reminder error: {str(e)}")
            return False
