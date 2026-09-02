"""
ML Analytics Models
Predictions, trends, anomalies, health scores
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime as dt
import uuid

Base = declarative_base()


class RevenuePrediction(Base):
    """Revenue prediction for a user"""
    __tablename__ = "revenue_predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False, index=True)
    
    # Prediction data
    current_revenue = Column(Float, default=0.0)
    predicted_revenue = Column(Float, default=0.0)
    trend_percentage = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)  # 0-1
    days_ahead = Column(Integer, default=30)
    
    # Predictions detail
    predictions = Column(JSON, nullable=True)  # List of daily predictions
    
    # Metadata
    generated_at = Column(DateTime, default=dt.utcnow, index=True)
    created_at = Column(DateTime, default=dt.utcnow)


class AudiencePrediction(Base):
    """Audience growth prediction for a user"""
    __tablename__ = "audience_predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False, index=True)
    
    # Prediction data
    current_followers = Column(Integer, default=0)
    predicted_followers = Column(Integer, default=0)
    projected_growth = Column(Integer, default=0)
    growth_rate_per_day = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    days_ahead = Column(Integer, default=30)
    
    # Predictions detail
    predictions = Column(JSON, nullable=True)  # List of daily predictions
    
    # Metadata
    generated_at = Column(DateTime, default=dt.utcnow, index=True)
    created_at = Column(DateTime, default=dt.utcnow)


class TrendForecast(Base):
    """Trend forecast for a beat"""
    __tablename__ = "trend_forecasts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    beat_id = Column(String(36), ForeignKey("beat.id"), nullable=False, index=True)
    
    # Trend data
    trend = Column(String(50))  # "rising", "falling", "stable"
    trend_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    days_ahead = Column(Integer, default=14)
    
    # Metrics
    play_trend = Column(Float, default=0.0)
    engagement_trend = Column(Float, default=0.0)
    current_plays_daily = Column(Float, default=0.0)
    current_saves_daily = Column(Float, default=0.0)
    
    # Recommendation
    recommendation = Column(Text, nullable=True)
    
    # Metadata
    generated_at = Column(DateTime, default=dt.utcnow, index=True)
    created_at = Column(DateTime, default=dt.utcnow)


class AnomalyDetection(Base):
    """Detected anomalies in user metrics"""
    __tablename__ = "anomaly_detections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False, index=True)
    
    # Anomaly data
    metric = Column(String(50), nullable=False)  # "revenue", "plays", "followers"
    anomaly_date = Column(DateTime, nullable=True)
    anomaly_value = Column(Float, nullable=True)
    anomaly_score = Column(Float, default=0.0)  # 0-1, higher = more anomalous
    severity = Column(String(50))  # "low", "medium", "high"
    
    # Context
    expected_value = Column(Float, nullable=True)
    deviation = Column(Float, nullable=True)  # Deviation from expected
    
    # Metadata
    detected_at = Column(DateTime, default=dt.utcnow, index=True)
    created_at = Column(DateTime, default=dt.utcnow)


class HealthScore(Base):
    """Overall user health score"""
    __tablename__ = "health_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False, index=True, unique=True)
    
    # Overall score
    overall_score = Column(Integer, default=0)  # 0-100
    rating = Column(String(50))  # "Excellent", "Good", "Needs Work"
    
    # Component scores
    revenue_health = Column(Integer, default=0)  # 0-100
    audience_health = Column(Integer, default=0)  # 0-100
    stability = Column(Integer, default=0)  # 0-100
    
    # Trends
    previous_score = Column(Integer, default=0)
    score_change = Column(Integer, default=0)  # +/- change from previous
    
    # Metadata
    calculated_at = Column(DateTime, default=dt.utcnow, index=True)
    created_at = Column(DateTime, default=dt.utcnow)
    updated_at = Column(DateTime, default=dt.utcnow, onupdate=dt.utcnow)


class InsightsReport(Base):
    """Comprehensive AI insights report"""
    __tablename__ = "insights_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False, index=True)
    
    # Report data
    report_data = Column(JSON, nullable=True)  # Complete report JSON
    
    # Key metrics
    revenue_prediction_id = Column(String(36), ForeignKey("revenue_predictions.id"), nullable=True)
    audience_prediction_id = Column(String(36), ForeignKey("audience_predictions.id"), nullable=True)
    health_score_id = Column(String(36), ForeignKey("health_scores.id"), nullable=True)
    
    # Anomalies
    anomalies_count = Column(Integer, default=0)
    
    # Metadata
    generated_at = Column(DateTime, default=dt.utcnow, index=True)
    created_at = Column(DateTime, default=dt.utcnow)
