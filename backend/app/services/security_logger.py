"""
Security Event Logger
Logs security events for auditing and fraud detection
"""

import uuid
import json
from typing import Optional, Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.security_event import SecurityEvent
import logging

logger = logging.getLogger(__name__)


class SecurityLogger:
    """Service for logging security events"""
    
    @staticmethod
    def log_event(
        db: Session,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        country: Optional[str] = None,
        risk_score: Optional[float] = None,
        flags: Optional[List[str]] = None,
        decision: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> SecurityEvent:
        """
        Log a security event
        
        Args:
            db: Database session
            event_type: Type of event (login, register, transaction, etc.)
            user_id: User ID (if known)
            ip_address: IP address
            device_id: Device fingerprint
            user_agent: User agent string
            country: Country code
            risk_score: Fraud risk score (0-100)
            flags: List of security flags
            decision: Decision made (allow, review, block)
            metadata: Additional context
            
        Returns:
            Created SecurityEvent
        """
        event = SecurityEvent(
            id=str(uuid.uuid4()),
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            device_id=device_id,
            user_agent=user_agent,
            country=country,
            risk_score=risk_score,
            flags=json.dumps(flags) if flags else None,
            decision=decision,
            metadata=json.dumps(metadata) if metadata else None,
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        logger.info(
            f"Security event logged: {event_type} - "
            f"User: {user_id}, Risk: {risk_score}, Decision: {decision}"
        )
        
        return event
    
    @staticmethod
    def log_registration(
        db: Session,
        user_id: str,
        email: str,
        ip_address: str,
        device_id: Optional[str],
        risk_score: float,
        flags: List[str],
        decision: str
    ):
        """Log a registration attempt"""
        return SecurityLogger.log_event(
            db=db,
            event_type="registration",
            user_id=user_id,
            ip_address=ip_address,
            device_id=device_id,
            risk_score=risk_score,
            flags=flags,
            decision=decision,
            metadata={"email": email}
        )
    
    @staticmethod
    def log_login_attempt(
        db: Session,
        user_id: Optional[str],
        email: str,
        ip_address: str,
        device_id: Optional[str],
        success: bool,
        risk_score: Optional[float] = None,
        flags: Optional[List[str]] = None
    ):
        """Log a login attempt"""
        return SecurityLogger.log_event(
            db=db,
            event_type="login_attempt",
            user_id=user_id,
            ip_address=ip_address,
            device_id=device_id,
            risk_score=risk_score,
            flags=flags,
            decision="allow" if success else "block",
            metadata={
                "email": email,
                "success": success
            }
        )
    
    @staticmethod
    def log_suspicious_activity(
        db: Session,
        user_id: str,
        activity_type: str,
        ip_address: str,
        device_id: Optional[str],
        risk_score: float,
        flags: List[str],
        details: Dict
    ):
        """Log suspicious activity"""
        return SecurityLogger.log_event(
            db=db,
            event_type="suspicious_activity",
            user_id=user_id,
            ip_address=ip_address,
            device_id=device_id,
            risk_score=risk_score,
            flags=flags,
            decision="review",
            metadata={
                "activity_type": activity_type,
                **details
            }
        )
    
    @staticmethod
    def log_fraud_prevention(
        db: Session,
        user_id: str,
        transaction_type: str,
        amount: Optional[float],
        risk_score: float,
        flags: List[str],
        decision: str
    ):
        """Log fraud prevention action"""
        return SecurityLogger.log_event(
            db=db,
            event_type="fraud_prevention",
            user_id=user_id,
            risk_score=risk_score,
            flags=flags,
            decision=decision,
            metadata={
                "transaction_type": transaction_type,
                "amount": amount
            }
        )


# Singleton instance
security_logger = SecurityLogger()
