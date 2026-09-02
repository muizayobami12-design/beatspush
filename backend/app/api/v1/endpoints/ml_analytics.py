"""
ML Analytics API Endpoints
Advanced predictions, trend forecasting, anomaly detection
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.services.ml_analytics_service import MLAnalyticsService

router = APIRouter(prefix="/analytics/ml", tags=["ML Analytics"])

ml_service = MLAnalyticsService()


@router.get("/revenue-prediction")
async def get_revenue_prediction(
    days_ahead: int = 30,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Predict future revenue for current user
    - days_ahead: Number of days to forecast (default: 30)
    - Returns: Predicted revenue, trend, confidence, daily predictions
    """
    result = await ml_service.predict_revenue(current_user.id, db, days_ahead)
    return result


@router.get("/audience-prediction")
async def get_audience_prediction(
    days_ahead: int = 30,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Predict audience growth for current user
    - days_ahead: Number of days to forecast (default: 30)
    - Returns: Predicted followers, growth rate, confidence
    """
    result = await ml_service.predict_audience_growth(current_user.id, db, days_ahead)
    return result


@router.get("/trend-forecast/{beat_id}")
async def get_trend_forecast(
    beat_id: str,
    days_ahead: int = 14,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Forecast if a beat will trend up/down/stable
    - beat_id: Beat to forecast
    - days_ahead: Number of days ahead (default: 14)
    - Returns: Trend direction, score, confidence, recommendation
    """
    result = await ml_service.forecast_trend(beat_id, db, days_ahead)
    return result


@router.get("/anomalies")
async def detect_anomalies(
    metric: str = "revenue",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Detect unusual patterns in user metrics
    - metric: "revenue" or "plays"
    - Returns: List of detected anomalies with severity
    """
    if metric not in ["revenue", "plays"]:
        raise HTTPException(status_code=400, detail="Invalid metric")

    result = await ml_service.detect_anomalies(current_user.id, db, metric)
    return result


@router.get("/insights-report")
async def get_insights_report(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate comprehensive AI insights report
    - Returns: Revenue predictions, audience predictions, anomalies, beat trends, overall health
    """
    result = await ml_service.generate_user_insights_report(current_user.id, db)
    return result


@router.get("/health-score")
async def get_health_score(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get overall user health score (0-100)
    - Returns: Overall score, revenue health, audience health, stability, rating
    """
    report = await ml_service.generate_user_insights_report(current_user.id, db)
    return report.get("overall_health", {})
