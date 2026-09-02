"""
Fraud Detection Service
Real-time fraud scoring for transactions and logins
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
from app.db.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class FraudDetector:
    """Service for detecting fraudulent activity"""
    
    async def score_registration(
        self,
        email: str,
        ip_address: str,
        device_id: Optional[str],
        country: Optional[str] = None,
        db: Session = None
    ) -> Dict:
        """
        Score a new registration for fraud risk
        
        Returns:
            {
                "risk_score": float (0-100),
                "decision": str ("allow", "review", "block"),
                "flags": List[str],
                "reasons": List[str]
            }
        """
        risk_score = 0
        flags = []
        reasons = []
        
        # Check 1: Email domain analysis
        domain = email.split('@')[1].lower() if '@' in email else ''
        
        # Suspicious domains
        if any(keyword in domain for keyword in ['temp', 'disposable', 'fake', 'trash']):
            risk_score += 40
            flags.append("suspicious_email_domain")
            reasons.append("Email domain appears temporary")
        
        # Check 2: Multiple accounts from same IP (if db available)
        if db and ip_address:
            from app.models.user import User
            same_ip_users = db.query(User).filter(
                User.last_login_ip == ip_address
            ).count()
            
            if same_ip_users > 5:
                risk_score += 30
                flags.append("ip_reuse")
                reasons.append(f"Multiple accounts from same IP ({same_ip_users})")
            elif same_ip_users > 2:
                risk_score += 15
                flags.append("ip_reuse_minor")
        
        # Check 3: Device fingerprint analysis
        if not device_id:
            risk_score += 10
            flags.append("no_device_id")
            reasons.append("Device fingerprint unavailable")
        elif db and device_id:
            from app.models.user import User
            same_device_users = db.query(User).filter(
                User.device_id == device_id
            ).count()
            
            if same_device_users > 3:
                risk_score += 25
                flags.append("device_reuse")
                reasons.append(f"Multiple accounts from same device ({same_device_users})")
        
        # Check 4: Geographic risk (optional)
        if country:
            # High-risk countries for fraud (customize based on your data)
            high_risk_countries = []  # Add countries with high fraud rates
            if country in high_risk_countries:
                risk_score += 15
                flags.append("high_risk_country")
                reasons.append(f"Registration from high-risk location")
        
        # Determine decision
        if risk_score < 30:
            decision = "allow"
        elif risk_score < 70:
            decision = "review"  # Manual review queue
        else:
            decision = "block"
        
        logger.info(f"Registration fraud score: {risk_score} ({decision}) - {email}")
        
        return {
            "risk_score": risk_score,
            "decision": decision,
            "flags": flags,
            "reasons": reasons,
        }
    
    async def score_login(
        self,
        user_id: int,
        ip_address: str,
        device_id: Optional[str],
        user_data: Dict,
        db: Session = None
    ) -> Dict:
        """
        Score a login attempt for suspicious activity
        
        Args:
            user_id: User attempting login
            ip_address: Current IP address
            device_id: Current device fingerprint
            user_data: User's stored data (last_login_ip, last_login_at, etc.)
            
        Returns:
            {
                "risk_score": float (0-100),
                "action": str ("allow", "mfa_required", "block"),
                "flags": List[str],
                "reasons": List[str]
            }
        """
        risk_score = 0
        flags = []
        reasons = []
        
        # Check 1: Impossible travel
        last_login_at = user_data.get("last_login_at")
        last_login_ip = user_data.get("last_login_ip")
        
        if last_login_at and last_login_ip and last_login_ip != ip_address:
            time_diff = (datetime.utcnow() - last_login_at).total_seconds()
            
            # If login within 5 minutes from different IP = suspicious
            if time_diff < 300:  # 5 minutes
                risk_score += 50
                flags.append("impossible_travel")
                reasons.append("Login from different location within 5 minutes")
        
        # Check 2: New device
        last_device_id = user_data.get("device_id")
        if last_device_id and device_id != last_device_id:
            risk_score += 20
            flags.append("new_device")
            reasons.append("Login from new device")
        
        # Check 3: Failed login attempts
        failed_attempts = user_data.get("failed_login_attempts", 0)
        if failed_attempts > 3:
            risk_score += 25
            flags.append("prior_failures")
            reasons.append(f"Multiple failed login attempts ({failed_attempts})")
        
        # Check 4: Unusual timing
        hour = datetime.utcnow().hour
        if hour < 6 or hour > 23:
            risk_score += 10
            flags.append("unusual_time")
            reasons.append("Login at unusual hour")
        
        # Check 5: VPN/Proxy detection (would require IP intelligence API)
        # Placeholder for now
        # if is_vpn(ip_address):
        #     risk_score += 15
        #     flags.append("vpn_detected")
        
        # Determine action
        if risk_score < 30:
            action = "allow"
        elif risk_score < 60:
            action = "mfa_required"  # Require 2FA
        else:
            action = "block"  # Block and alert user
        
        logger.info(f"Login fraud score: {risk_score} ({action}) - User {user_id}")
        
        return {
            "risk_score": risk_score,
            "action": action,
            "flags": flags,
            "reasons": reasons,
        }
    
    async def score_transaction(
        self,
        user_id: int,
        amount: float,
        payment_method: str,
        user_data: Dict,
        db: Session = None
    ) -> Dict:
        """
        Score a transaction for fraud risk
        
        Returns:
            {
                "risk_score": float (0-100),
                "decision": str ("approve", "review", "reject"),
                "flags": List[str],
                "reasons": List[str]
            }
        """
        risk_score = 0
        flags = []
        reasons = []
        
        # Check 1: New user with high-value purchase
        account_age_days = user_data.get("account_age_days", 0)
        
        if account_age_days < 7 and amount > 10000:  # ₦10,000
            risk_score += 30
            flags.append("new_user_high_value")
            reasons.append("New account with large transaction")
        
        # Check 2: Velocity check - multiple purchases in short time
        # Would require checking recent transaction history
        if db:
            from app.models.user import User
            # Placeholder: get recent transactions
            # recent_purchases = get_recent_purchases(user_id, hours=1, db=db)
            # if len(recent_purchases) > 3:
            #     risk_score += 25
            #     flags.append("high_velocity")
            pass
        
        # Check 3: Amount anomaly
        avg_transaction = user_data.get("avg_transaction_amount", 0)
        if avg_transaction > 0 and amount > avg_transaction * 3:
            risk_score += 20
            flags.append("amount_anomaly")
            reasons.append("Transaction amount significantly higher than usual")
        
        # Check 4: Payment method risk
        if payment_method == "unknown":
            risk_score += 15
            flags.append("unknown_payment_method")
        
        # Determine decision
        if risk_score < 30:
            decision = "approve"
        elif risk_score < 70:
            decision = "review"  # Manual review
        else:
            decision = "reject"
        
        logger.info(f"Transaction fraud score: {risk_score} ({decision}) - User {user_id}, Amount: ₦{amount}")
        
        return {
            "risk_score": risk_score,
            "decision": decision,
            "flags": flags,
            "reasons": reasons,
        }


# Singleton instance
fraud_detector = FraudDetector()
