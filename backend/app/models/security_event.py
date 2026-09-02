"""
Security Event Model
Logs security-related events for auditing and fraud detection
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base


class SecurityEvent(Base):
    """Security event logging for audit trail"""
    __tablename__ = "security_events"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Event details
    event_type = Column(String(50), nullable=False, index=True)  # login, register, transaction, etc.
    user_id = Column(String(36), nullable=True, index=True)  # User involved (if known)
    
    # Security data
    ip_address = Column(String(45), nullable=True)
    device_id = Column(String(255), nullable=True)
    user_agent = Column(String(500), nullable=True)
    country = Column(String(2), nullable=True)  # ISO country code
    
    # Fraud detection
    risk_score = Column(Float, nullable=True)  # 0-100
    flags = Column(Text, nullable=True)  # JSON array of flags
    decision = Column(String(20), nullable=True)  # allow, review, block
    
    # Additional context
    event_metadata = Column(Text, nullable=True)  # JSON object with extra data (renamed from metadata to avoid SQLAlchemy conflict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SecurityEvent {self.event_type} - User {self.user_id}>"
