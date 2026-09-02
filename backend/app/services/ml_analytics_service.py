"""
ML Analytics Service
Advanced predictions, trend forecasting, audience growth projections, anomaly detection
Uses scikit-learn + pandas for data science capabilities
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import json
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.cache import get_cache, set_cache
from app.models import Beat, User, Analytics, Transaction


class MLAnalyticsService:
    """Machine learning analytics engine for BeatPush"""

    def __init__(self):
        self.cache_ttl = 3600  # 1 hour
        self.scaler = StandardScaler()

    # ============ REVENUE PREDICTIONS ============

    async def predict_revenue(
        self,
        user_id: str,
        db: Session,
        days_ahead: int = 30,
    ) -> Dict:
        """
        Predict future revenue using linear regression
        Features: historical revenue, trend, seasonality
        """
        cache_key = f"revenue_pred:{user_id}:{days_ahead}"
        cached = await get_cache(cache_key)
        if cached:
            return json.loads(cached)

        # Get historical revenue data (last 90 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)

        revenue_data = db.query(
            func.date(Transaction.created_at).label("date"),
            func.sum(Transaction.amount).label("revenue")
        ).filter(
            Transaction.recipient_id == user_id,
            Transaction.created_at >= start_date,
            Transaction.status == "completed"
        ).group_by(
            func.date(Transaction.created_at)
        ).all()

        if len(revenue_data) < 10:
            return {
                "status": "insufficient_data",
                "message": "Need at least 10 days of data for prediction",
                "current_revenue": 0,
                "predicted_revenue": 0,
            }

        # Prepare data for model
        dates = [(end_date - timedelta(days=90-i)).timestamp() for i in range(len(revenue_data))]
        revenues = [r.revenue or 0 for r in revenue_data]

        # Train linear regression model
        X = np.array(dates).reshape(-1, 1)
        y = np.array(revenues)

        model = LinearRegression()
        model.fit(X, y)

        # Generate predictions for next N days
        future_dates = [
            (end_date + timedelta(days=i)).timestamp()
            for i in range(1, days_ahead + 1)
        ]
        future_X = np.array(future_dates).reshape(-1, 1)
        predictions = model.predict(future_X)

        # Calculate trend
        current_revenue = sum(revenues[-7:])  # Last 7 days
        predicted_revenue = sum(predictions)
        trend_pct = ((predicted_revenue - current_revenue) / current_revenue * 100) if current_revenue > 0 else 0

        result = {
            "status": "success",
            "current_revenue": float(current_revenue),
            "predicted_revenue": float(max(0, predicted_revenue)),
            "trend_percentage": float(trend_pct),
            "confidence": float(self._calculate_r_squared(model, X, y)),
            "days_ahead": days_ahead,
            "predictions": [
                {
                    "date": (end_date + timedelta(days=i)).isoformat(),
                    "predicted_revenue": float(max(0, pred))
                }
                for i, pred in enumerate(predictions, 1)
            ]
        }

        await set_cache(cache_key, json.dumps(result), self.cache_ttl)
        return result

    # ============ AUDIENCE GROWTH PREDICTIONS ============

    async def predict_audience_growth(
        self,
        user_id: str,
        db: Session,
        days_ahead: int = 30,
    ) -> Dict:
        """
        Predict audience growth using exponential/linear regression
        Factors: follower growth rate, engagement, content frequency
        """
        cache_key = f"audience_pred:{user_id}:{days_ahead}"
        cached = await get_cache(cache_key)
        if cached:
            return json.loads(cached)

        # Get user follower history (last 90 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)

        follower_data = db.query(
            func.date(Analytics.created_at).label("date"),
            func.sum(Analytics.follower_gain).label("followers_gained")
        ).filter(
            Analytics.user_id == user_id,
            Analytics.created_at >= start_date,
        ).group_by(
            func.date(Analytics.created_at)
        ).all()

        if len(follower_data) < 10:
            return {
                "status": "insufficient_data",
                "predicted_followers": 0,
            }

        # Calculate cumulative followers
        follower_counts = np.cumsum([f.followers_gained or 0 for f in follower_data])

        dates = np.array([(end_date - timedelta(days=90-i)).timestamp() for i in range(len(follower_counts))])
        X = (dates - dates[0]).reshape(-1, 1) / 86400  # Convert to days

        model = LinearRegression()
        model.fit(X, follower_counts)

        # Generate predictions
        future_X = np.array([i for i in range(1, days_ahead + 1)]).reshape(-1, 1)
        predictions = model.predict(future_X)

        current_followers = db.query(User).filter(User.id == user_id).first()
        current_count = current_followers.follower_count if current_followers else 0
        predicted_growth = sum(max(0, p) for p in predictions)

        result = {
            "status": "success",
            "current_followers": current_count,
            "predicted_followers": int(current_count + predicted_growth),
            "projected_growth": int(predicted_growth),
            "growth_rate_per_day": float(np.mean(predictions[:7])),
            "confidence": float(self._calculate_r_squared(model, X, follower_counts)),
            "predictions": [
                {
                    "date": (end_date + timedelta(days=i)).isoformat(),
                    "predicted_followers": int(current_count + sum(max(0, p) for p in predictions[:i]))
                }
                for i in range(1, days_ahead + 1)
            ]
        }

        await set_cache(cache_key, json.dumps(result), self.cache_ttl)
        return result

    # ============ TREND FORECASTING ============

    async def forecast_trend(
        self,
        beat_id: str,
        db: Session,
        days_ahead: int = 14,
    ) -> Dict:
        """
        Forecast beat trend (will it gain popularity or decline?)
        Analyzes: play velocity, save rate, playlist adds, sentiment
        """
        cache_key = f"trend_pred:{beat_id}:{days_ahead}"
        cached = await get_cache(cache_key)
        if cached:
            return json.loads(cached)

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=60)

        # Get beat performance metrics
        beat_analytics = db.query(
            func.date(Analytics.created_at).label("date"),
            func.sum(Analytics.plays).label("plays"),
            func.sum(Analytics.saves).label("saves"),
            func.sum(Analytics.downloads).label("downloads"),
        ).filter(
            Analytics.beat_id == beat_id,
            Analytics.created_at >= start_date,
        ).group_by(
            func.date(Analytics.created_at)
        ).order_by("date").all()

        if len(beat_analytics) < 7:
            return {
                "status": "insufficient_data",
                "trend": "unknown",
                "confidence": 0.0,
            }

        # Calculate velocity metrics
        plays = np.array([a.plays or 0 for a in beat_analytics])
        saves = np.array([a.saves or 0 for a in beat_analytics])
        engagement_rate = saves / (plays + 1)

        # Detect trend direction
        recent_plays = np.mean(plays[-7:])
        previous_plays = np.mean(plays[-14:-7])
        play_trend = (recent_plays - previous_plays) / (previous_plays + 1)

        recent_engagement = np.mean(engagement_rate[-7:])
        previous_engagement = np.mean(engagement_rate[-14:-7])
        engagement_trend = (recent_engagement - previous_engagement) / (previous_engagement + 0.01)

        # Combined trend score
        trend_score = (play_trend * 0.6) + (engagement_trend * 0.4)

        if trend_score > 0.15:
            trend = "rising"
            trend_label = "📈 Rising"
        elif trend_score < -0.15:
            trend = "falling"
            trend_label = "📉 Falling"
        else:
            trend = "stable"
            trend_label = "→ Stable"

        result = {
            "status": "success",
            "beat_id": beat_id,
            "trend": trend,
            "trend_label": trend_label,
            "trend_score": float(trend_score),
            "confidence": float(min(0.95, 0.5 + abs(trend_score))),
            "metrics": {
                "play_trend": float(play_trend),
                "engagement_trend": float(engagement_trend),
                "current_plays_daily": float(recent_plays),
                "current_saves_daily": float(np.mean(saves[-7:])),
            },
            "recommendation": self._get_trend_recommendation(trend, trend_score),
        }

        await set_cache(cache_key, json.dumps(result), self.cache_ttl)
        return result

    # ============ ANOMALY DETECTION ============

    async def detect_anomalies(
        self,
        user_id: str,
        db: Session,
        metric: str = "revenue",
    ) -> Dict:
        """
        Detect unusual patterns in user metrics
        Uses Isolation Forest for unsupervised anomaly detection
        """
        cache_key = f"anomalies:{user_id}:{metric}"
        cached = await get_cache(cache_key)
        if cached:
            return json.loads(cached)

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)

        # Get historical data
        if metric == "revenue":
            data = db.query(
                func.date(Transaction.created_at).label("date"),
                func.sum(Transaction.amount).label("value")
            ).filter(
                Transaction.recipient_id == user_id,
                Transaction.created_at >= start_date,
                Transaction.status == "completed"
            ).group_by(func.date(Transaction.created_at)).all()
        elif metric == "plays":
            data = db.query(
                func.date(Analytics.created_at).label("date"),
                func.sum(Analytics.plays).label("value")
            ).filter(
                Analytics.user_id == user_id,
                Analytics.created_at >= start_date,
            ).group_by(func.date(Analytics.created_at)).all()
        else:
            return {"status": "invalid_metric", "anomalies": []}

        if len(data) < 10:
            return {"status": "insufficient_data", "anomalies": []}

        values = np.array([d.value or 0 for d in data]).reshape(-1, 1)

        # Detect anomalies
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        predictions = iso_forest.fit_predict(values)
        scores = iso_forest.score_samples(values)

        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly detected
                anomalies.append({
                    "date": data[i].date.isoformat(),
                    "value": float(values[i][0]),
                    "anomaly_score": float(abs(score)),
                    "severity": "high" if abs(score) > 0.5 else "medium",
                })

        result = {
            "status": "success",
            "metric": metric,
            "total_data_points": len(data),
            "anomalies_detected": len(anomalies),
            "anomalies": sorted(anomalies, key=lambda x: x["anomaly_score"], reverse=True)[:5],
        }

        await set_cache(cache_key, json.dumps(result), self.cache_ttl)
        return result

    # ============ UTILITY METHODS ============

    def _calculate_r_squared(self, model, X, y) -> float:
        """Calculate R-squared coefficient"""
        y_pred = model.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / (ss_tot + 1e-10))
        return max(0.0, min(1.0, r_squared))

    def _get_trend_recommendation(self, trend: str, score: float) -> str:
        """Get recommendation based on trend"""
        if trend == "rising":
            if score > 0.3:
                return "🚀 Your beat is trending! Consider promoting it"
            return "✨ Momentum is building, keep up the engagement"
        elif trend == "falling":
            return "⚠️  Engagement declining. Try remixing or new promo"
        else:
            return "→ Beat performing steadily. Consider fresh content"

    # ============ BATCH ANALYTICS ============

    async def generate_user_insights_report(
        self,
        user_id: str,
        db: Session,
    ) -> Dict:
        """Generate comprehensive AI insights for user"""

        # Gather all predictions and analytics
        revenue_pred = await self.predict_revenue(user_id, db)
        audience_pred = await self.predict_audience_growth(user_id, db)
        anomalies = await self.detect_anomalies(user_id, db, metric="revenue")

        # Get top beats
        top_beats = db.query(
            Beat,
            func.count(Analytics.id).label("analytics_count")
        ).outerjoin(Analytics, Beat.id == Analytics.beat_id).filter(
            Beat.user_id == user_id
        ).group_by(Beat.id).order_by(
            func.count(Analytics.id).desc()
        ).limit(3).all()

        # Get trend for each top beat
        trends = []
        for beat, _ in top_beats:
            trend = await self.forecast_trend(beat.id, db)
            trends.append({
                "beat_id": beat.id,
                "title": beat.title,
                "trend": trend.get("trend"),
                "confidence": trend.get("confidence"),
            })

        return {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "revenue_prediction": revenue_pred,
            "audience_prediction": audience_pred,
            "anomalies": anomalies,
            "beat_trends": trends,
            "overall_health": self._calculate_health_score(revenue_pred, audience_pred, anomalies),
        }

    def _calculate_health_score(self, revenue: Dict, audience: Dict, anomalies: Dict) -> Dict:
        """Calculate overall user health score (0-100)"""
        revenue_score = revenue.get("confidence", 0) * 100 if revenue.get("status") == "success" else 0
        audience_score = audience.get("confidence", 0) * 100 if audience.get("status") == "success" else 0
        anomaly_penalty = min(50, len(anomalies.get("anomalies", [])) * 10)

        total_score = (revenue_score * 0.4) + (audience_score * 0.4) + ((100 - anomaly_penalty) * 0.2)

        return {
            "overall_score": int(total_score),
            "revenue_health": int(revenue_score),
            "audience_health": int(audience_score),
            "stability": 100 - int(anomaly_penalty),
            "rating": "Excellent" if total_score >= 80 else "Good" if total_score >= 60 else "Needs Work",
        }
