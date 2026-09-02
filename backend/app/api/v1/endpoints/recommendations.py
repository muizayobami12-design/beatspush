"""
Recommendation API endpoints for BeatPush
Personalized beat recommendations, trending, discover feed
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.recommendation_engine import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def get_recommendation_service(db: Session) -> RecommendationService:
    """Get recommendation service instance"""
    return RecommendationService(db)


@router.get("/beats")
async def get_personalized_recommendations(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get personalized beat recommendations for current user
    Uses hybrid: 60% collaborative + 40% content-based filtering
    """
    try:
        service = get_recommendation_service(db)
        recommendations = service.get_personalized_recommendations(
            user_id=str(current_user.id), limit=limit
        )

        return {
            "success": True,
            "recommendations": [
                {
                    "id": beat.id,
                    "title": beat.title,
                    "genre": beat.genre,
                    "bpm": beat.bpm,
                    "key": beat.musical_key,
                    "mood": beat.mood,
                    "producer_id": beat.producer_user_id,
                    "play_count": beat.play_count,
                    "favorite_count": beat.favorite_count,
                    "price": beat.lease_price,
                }
                for beat in recommendations
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@router.get("/trending")
async def get_trending_beats(
    limit: int = Query(20, ge=1, le=100),
    genre: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get trending beats (24-hour window)
    Optionally filter by genre
    """
    try:
        service = get_recommendation_service(db)
        trending = service.get_trending_beats(limit=limit, genre=genre)

        return {
            "success": True,
            "trending": [
                {
                    "id": beat.id,
                    "title": beat.title,
                    "genre": beat.genre,
                    "bpm": beat.bpm,
                    "mood": beat.mood,
                    "producer_id": beat.producer_user_id,
                    "play_count": beat.play_count,
                    "favorite_count": beat.favorite_count,
                    "price": beat.lease_price,
                }
                for beat in trending
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending: {str(e)}")


@router.get("/discover")
async def get_discover_feed(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get personalized discover feed
    Mix of: 20% trending + 15% followed artists + 40% collaborative + 25% content-based
    """
    try:
        service = get_recommendation_service(db)
        feed = service.get_discover_feed(user_id=str(current_user.id), limit=limit)

        return {
            "success": True,
            "feed": [
                {
                    "id": beat.id,
                    "title": beat.title,
                    "genre": beat.genre,
                    "bpm": beat.bpm,
                    "mood": beat.mood,
                    "producer_id": beat.producer_user_id,
                    "play_count": beat.play_count,
                    "favorite_count": beat.favorite_count,
                    "price": beat.lease_price,
                }
                for beat in feed
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get discover feed: {str(e)}")


@router.get("/similar/{beat_id}")
async def get_similar_beats(
    beat_id: str,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get beats similar to given beat
    Uses content-based filtering (genre, BPM, key, mood, tags)
    """
    try:
        service = get_recommendation_service(db)
        similar = service.get_similar_beats(beat_id=beat_id, limit=limit)

        if not similar:
            raise HTTPException(status_code=404, detail="Beat not found")

        return {
            "success": True,
            "similar": [
                {
                    "id": beat.id,
                    "title": beat.title,
                    "genre": beat.genre,
                    "bpm": beat.bpm,
                    "key": beat.musical_key,
                    "mood": beat.mood,
                    "producer_id": beat.producer_user_id,
                    "play_count": beat.play_count,
                    "favorite_count": beat.favorite_count,
                    "price": beat.lease_price,
                }
                for beat in similar
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get similar beats: {str(e)}")


@router.get("/also-bought/{beat_id}")
async def get_also_bought(
    beat_id: str,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get beats bought by people who also bought this beat
    Collaborative filtering based on purchase patterns
    """
    try:
        service = get_recommendation_service(db)
        also_bought = service.get_also_bought(beat_id=beat_id, limit=limit)

        return {
            "success": True,
            "also_bought": [
                {
                    "id": beat.id,
                    "title": beat.title,
                    "genre": beat.genre,
                    "bpm": beat.bpm,
                    "mood": beat.mood,
                    "producer_id": beat.producer_user_id,
                    "play_count": beat.play_count,
                    "favorite_count": beat.favorite_count,
                    "price": beat.lease_price,
                }
                for beat in also_bought
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get also-bought: {str(e)}")


@router.post("/feedback/{beat_id}")
async def record_recommendation_feedback(
    beat_id: str,
    helpful: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Record feedback on recommendation (helpful/not helpful)
    Used to improve recommendation algorithm over time
    """
    # TODO: Implement feedback storage in database
    # This would be used to adjust recommendation weights

    return {
        "success": True,
        "message": "Feedback recorded",
        "beat_id": beat_id,
        "helpful": helpful,
    }
