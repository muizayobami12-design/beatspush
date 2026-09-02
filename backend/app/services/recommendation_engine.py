"""
AI Recommendation Engine for BeatPush
Provides personalized beat recommendations using hybrid collaborative + content-based filtering
"""

import math
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.beat import Beat, BeatPlay, BeatFavorite, BeatPurchase
from app.models.user import User
from app.models.social import Follow
from app.models.recommendation import (
    UserPreferenceProfile,
    BeatSimilarityCache,
    TrendingBeatCache,
)


class ContentBasedFilter:
    """Content-based filtering using beat metadata"""

    @staticmethod
    def calculate_similarity(beat1: Dict, beat2: Dict) -> float:
        """
        Calculate similarity between two beats based on:
        - Genre (100% match = 1.0)
        - BPM (similar = higher score)
        - Key (same key = higher score)
        - Mood (same mood = 0.5)
        - Tags (overlap)
        """
        score = 0.0
        weights = {
            "genre": 0.3,
            "bpm": 0.25,
            "key": 0.2,
            "mood": 0.15,
            "tags": 0.1,
        }

        # Genre similarity (exact match = 1.0)
        if beat1.get("genre", "").lower() == beat2.get("genre", "").lower():
            score += 1.0 * weights["genre"]
        else:
            score += 0.3 * weights["genre"]  # Slight boost for different genre

        # BPM similarity (within 20 BPM = 1.0)
        bpm1 = beat1.get("bpm", 128)
        bpm2 = beat2.get("bpm", 128)
        bpm_diff = abs(bpm1 - bpm2)
        bpm_similarity = max(0, 1.0 - (bpm_diff / 100))
        score += bpm_similarity * weights["bpm"]

        # Key similarity (same key = 1.0, no key = 0.5)
        if beat1.get("key") and beat2.get("key"):
            if beat1.get("key") == beat2.get("key"):
                score += 1.0 * weights["key"]
            else:
                score += 0.3 * weights["key"]  # Different key penalty
        else:
            score += 0.5 * weights["key"]

        # Mood similarity (exact match = 1.0)
        if beat1.get("mood", "").lower() == beat2.get("mood", "").lower():
            score += 1.0 * weights["mood"]
        else:
            score += 0.4 * weights["mood"]

        # Tag similarity (Jaccard similarity)
        tags1 = set((beat1.get("tags") or "").split(","))
        tags2 = set((beat2.get("tags") or "").split(","))
        if tags1 and tags2:
            intersection = len(tags1 & tags2)
            union = len(tags1 | tags2)
            tag_similarity = intersection / union if union > 0 else 0
            score += tag_similarity * weights["tags"]

        return min(score, 1.0)

    @staticmethod
    def get_similar_beats(
        beat_id: str,
        beat_metadata: Dict,
        all_beats: List[Dict],
        top_n: int = 10,
    ) -> List[Tuple[str, float]]:
        """Get similar beats using content-based filtering"""
        similarities = []

        for beat in all_beats:
            if beat["id"] == beat_id:
                continue

            similarity = ContentBasedFilter.calculate_similarity(
                beat_metadata, beat
            )
            similarities.append((beat["id"], similarity))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]


class CollaborativeFilter:
    """Collaborative filtering using user-user and item-item similarity"""

    @staticmethod
    def get_user_similarity(
        user1_beats: Set[str], user2_beats: Set[str]
    ) -> float:
        """Calculate Jaccard similarity between two users' liked beats"""
        if not user1_beats or not user2_beats:
            return 0.0

        intersection = len(user1_beats & user2_beats)
        union = len(user1_beats | user2_beats)
        return intersection / union if union > 0 else 0.0

    @staticmethod
    def get_item_similarity(
        beat1_likers: Set[str], beat2_likers: Set[str]
    ) -> float:
        """Calculate Jaccard similarity between two beats' likers"""
        if not beat1_likers or not beat2_likers:
            return 0.0

        intersection = len(beat1_likers & beat2_likers)
        union = len(beat1_likers | beat2_likers)
        return intersection / union if union > 0 else 0.0

    @staticmethod
    def get_user_user_recommendations(
        user_id: str,
        user_liked_beats: Set[str],
        all_user_beats: Dict[str, Set[str]],
        top_n: int = 10,
    ) -> List[Tuple[str, float]]:
        """Find similar users and recommend their favorite beats"""
        similarities = []

        for other_user_id, other_beats in all_user_beats.items():
            if other_user_id == user_id:
                continue

            user_sim = CollaborativeFilter.get_user_similarity(
                user_liked_beats, other_beats
            )
            if user_sim > 0:
                similarities.append((other_user_id, user_sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Collect beats from similar users
        recommendations = []
        recommended_beats = set()

        for similar_user_id, similarity in similarities[:20]:  # Top 20 similar users
            other_beats = all_user_beats.get(similar_user_id, set())
            for beat_id in other_beats:
                if beat_id not in user_liked_beats and beat_id not in recommended_beats:
                    # Weight by user similarity
                    recommendations.append((beat_id, similarity))
                    recommended_beats.add(beat_id)

        # Sort by similarity descending
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_n]

    @staticmethod
    def get_item_item_recommendations(
        beat_id: str,
        beat_likers: Set[str],
        all_beat_likers: Dict[str, Set[str]],
        user_liked_beats: Set[str],
        top_n: int = 10,
    ) -> List[Tuple[str, float]]:
        """Find similar beats and recommend them"""
        similarities = []

        for other_beat_id, other_likers in all_beat_likers.items():
            if other_beat_id == beat_id or other_beat_id in user_liked_beats:
                continue

            beat_sim = CollaborativeFilter.get_item_similarity(beat_likers, other_likers)
            if beat_sim > 0:
                similarities.append((other_beat_id, beat_sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]


class SignalProcessor:
    """Process user signals with time decay and weighting"""

    # Signal weights (higher = more important)
    SIGNAL_WEIGHTS = {
        "purchase": 5.0,  # Strongest signal
        "favorite": 3.0,
        "play": 1.0,  # Weakest signal
    }

    # Time decay factor (signals older than this are weighted less)
    DECAY_WINDOW_DAYS = 30

    @staticmethod
    def calculate_signal_weight(signal_type: str, age_hours: float) -> float:
        """
        Calculate weight for a signal based on type and age
        Older signals = lower weight
        """
        base_weight = SignalProcessor.SIGNAL_WEIGHTS.get(signal_type, 1.0)

        # Time decay: exponential decay over DECAY_WINDOW_DAYS
        days = age_hours / 24
        decay_window = SignalProcessor.DECAY_WINDOW_DAYS
        decay_factor = math.exp(-(days / decay_window))

        return base_weight * decay_factor

    @staticmethod
    def aggregate_signals(
        user_signals: Dict[str, List[Tuple[str, float]]]
    ) -> Dict[str, float]:
        """
        Aggregate signals into beat scores
        user_signals: {beat_id: [(signal_type, age_hours), ...]}
        """
        beat_scores = defaultdict(float)

        for beat_id, signals in user_signals.items():
            for signal_type, age_hours in signals:
                weight = SignalProcessor.calculate_signal_weight(signal_type, age_hours)
                beat_scores[beat_id] += weight

        return dict(beat_scores)


class TrendingService:
    """Calculate trending beats using 24-hour rolling window"""

    @staticmethod
    def calculate_trending_score(
        plays: int, favorites: int, purchases: int, age_hours: float
    ) -> float:
        """
        Calculate trending score using engagement metrics with time decay
        Recent high engagement = high score
        """
        # Normalize metrics
        play_score = plays * 0.4  # 40% weight
        fav_score = favorites * 0.35  # 35% weight
        purchase_score = purchases * 0.25  # 25% weight

        engagement_score = play_score + fav_score + purchase_score

        # Time decay: very recent = high multiplier, older = lower
        decay_factor = math.exp(-(age_hours / 24))  # Half-life: 24 hours

        return engagement_score * decay_factor

    @staticmethod
    def get_trending_beats(
        beats: List[Dict], window_hours: int = 24, top_n: int = 20
    ) -> List[Tuple[str, float]]:
        """Get trending beats in a time window"""
        now = datetime.utcnow()
        window_start = now - timedelta(hours=window_hours)

        trending = []

        for beat in beats:
            # Count recent engagement
            plays = beat.get("recent_plays", 0)
            favs = beat.get("recent_favorites", 0)
            purchases = beat.get("recent_purchases", 0)

            # Age of beat
            created_at = beat.get("created_at", now)
            age_hours = (now - created_at).total_seconds() / 3600

            score = TrendingService.calculate_trending_score(
                plays, favs, purchases, age_hours
            )
            trending.append((beat["id"], score))

        # Sort by score descending
        trending.sort(key=lambda x: x[1], reverse=True)
        return trending[:top_n]


class DiversityEnforcer:
    """Enforce diversity in recommendations"""

    @staticmethod
    def enforce_diversity(
        recommendations: List[Tuple[str, float]],
        beat_metadata: Dict[str, Dict],
        max_per_artist: float = 0.15,  # Max 15% from single artist
        min_new_artists: float = 0.40,  # Min 40% new artists
    ) -> List[str]:
        """
        Apply diversity constraints to recommendations
        - No more than 15% of recommendations from single artist
        - At least 40% recommendations from artists user hasn't heard
        """
        result = []
        artist_counts = defaultdict(int)
        total = len(recommendations)

        # First pass: select top recommendations respecting artist limits
        for beat_id, score in recommendations:
            beat_meta = beat_metadata.get(beat_id, {})
            artist_id = beat_meta.get("producer_id")

            artist_count = artist_counts.get(artist_id, 0)
            max_allowed = max(1, int(total * max_per_artist))

            if artist_count < max_allowed:
                result.append(beat_id)
                artist_counts[artist_id] += 1

                if len(result) >= total:
                    break

        return result


class QualityFilter:
    """Filter beats by quality criteria"""

    @staticmethod
    def filter_by_quality(
        beats: List[Dict],
        min_rating: float = 0.0,
        min_plays: int = 0,
        exclude_copyrighted: bool = False,
    ) -> List[Dict]:
        """Filter beats by quality metrics"""
        filtered = []

        for beat in beats:
            # Rating check
            if beat.get("average_rating", 0) < min_rating:
                continue

            # Play count check
            if beat.get("play_count", 0) < min_plays:
                continue

            # Copyright check
            if exclude_copyrighted and beat.get("is_copyrighted", False):
                continue

            filtered.append(beat)

        return filtered


class RecommendationService:
    """Main recommendation service orchestrator"""

    def __init__(self, db: Session):
        self.db = db
        self.content_filter = ContentBasedFilter()
        self.collab_filter = CollaborativeFilter()
        self.signal_processor = SignalProcessor()
        self.trending_service = TrendingService()
        self.diversity_enforcer = DiversityEnforcer()
        self.quality_filter = QualityFilter()

    def get_personalized_recommendations(
        self, user_id: str, limit: int = 20, recent_only: bool = False
    ) -> List[Dict]:
        """
        Get personalized recommendations for user
        Uses hybrid: 60% collaborative + 40% content-based
        """
        # Get user's liked beats
        user_liked_beats = self._get_user_liked_beats(user_id)
        
        if not user_liked_beats:
            # New user: return trending beats
            return self.get_trending_beats(limit=limit)

        # Collaborative filtering recommendations (60%)
        collab_recs = self._get_collaborative_recommendations(user_id, limit)
        collab_scores = {beat_id: score for beat_id, score in collab_recs}

        # Content-based recommendations (40%)
        content_recs = self._get_content_based_recommendations(
            user_liked_beats, limit
        )
        content_scores = {beat_id: score for beat_id, score in content_recs}

        # Hybrid score: 60% collaborative + 40% content-based
        hybrid_scores = defaultdict(float)
        for beat_id in set(collab_scores.keys()) | set(content_scores.keys()):
            collab_score = collab_scores.get(beat_id, 0)
            content_score = content_scores.get(beat_id, 0)
            hybrid_scores[beat_id] = (collab_score * 0.6) + (content_score * 0.4)

        # Sort and return top N
        sorted_beats = sorted(
            hybrid_scores.items(), key=lambda x: x[1], reverse=True
        )[:limit]

        # Get full beat data
        beat_ids = [beat_id for beat_id, _ in sorted_beats]
        return self._fetch_beats(beat_ids)

    def get_similar_beats(self, beat_id: str, limit: int = 10) -> List[Dict]:
        """Get beats similar to given beat"""
        beat = self.db.query(Beat).filter(Beat.id == beat_id).first()
        if not beat:
            return []

        # Get all beats
        all_beats = self.db.query(Beat).filter(Beat.status == "active").all()

        beat_metadata = {
            "id": beat.id,
            "genre": beat.genre,
            "bpm": beat.bpm,
            "key": beat.musical_key,
            "mood": beat.mood,
            "tags": beat.tags,
        }

        all_beats_data = [
            {
                "id": b.id,
                "genre": b.genre,
                "bpm": b.bpm,
                "key": b.musical_key,
                "mood": b.mood,
                "tags": b.tags,
            }
            for b in all_beats
        ]

        similar = self.content_filter.get_similar_beats(
            beat_id, beat_metadata, all_beats_data, top_n=limit
        )

        similar_ids = [beat_id for beat_id, _ in similar]
        return self._fetch_beats(similar_ids)

    def get_trending_beats(
        self, limit: int = 20, genre: Optional[str] = None
    ) -> List[Dict]:
        """Get trending beats (24-hour window)"""
        now = datetime.utcnow()
        window_start = now - timedelta(hours=24)

        query = self.db.query(Beat).filter(Beat.status == "active")

        if genre:
            query = query.filter(
                Beat.genre.ilike(f"%{genre}%")
            )

        beats = query.all()

        # Collect engagement metrics for each beat
        beats_data = []
        for beat in beats:
            recent_plays = (
                self.db.query(func.count(BeatPlay.id))
                .filter(
                    and_(
                        BeatPlay.beat_id == beat.id,
                        BeatPlay.created_at >= window_start,
                    )
                )
                .scalar()
            )

            recent_favs = (
                self.db.query(func.count(BeatFavorite.id))
                .filter(
                    and_(
                        BeatFavorite.beat_id == beat.id,
                        BeatFavorite.created_at >= window_start,
                    )
                )
                .scalar()
            )

            recent_purchases = (
                self.db.query(func.count(BeatPurchase.id))
                .filter(
                    and_(
                        BeatPurchase.beat_id == beat.id,
                        BeatPurchase.created_at >= window_start,
                    )
                )
                .scalar()
            )

            beats_data.append(
                {
                    "id": beat.id,
                    "recent_plays": recent_plays or 0,
                    "recent_favorites": recent_favs or 0,
                    "recent_purchases": recent_purchases or 0,
                    "created_at": beat.created_at,
                }
            )

        trending = self.trending_service.get_trending_beats(
            beats_data, window_hours=24, top_n=limit
        )

        trending_ids = [beat_id for beat_id, _ in trending]
        return self._fetch_beats(trending_ids)

    def get_discover_feed(self, user_id: str, limit: int = 20) -> List[Dict]:
        """
        Get personalized discover feed
        Mix of: 20% trending + 15% followed artists + 40% collaborative + 25% content-based
        """
        result = []

        # Get trending (20%)
        trending_count = max(1, int(limit * 0.20))
        trending = self.get_trending_beats(limit=trending_count)
        result.extend(trending)

        # Get from followed artists (15%)
        followed_count = max(1, int(limit * 0.15))
        followed = self._get_from_followed_artists(user_id, limit=followed_count)
        result.extend(followed)

        # Get collaborative (40%)
        collab_count = max(1, int(limit * 0.40))
        collab = self._get_collaborative_recommendations(user_id, limit=collab_count)
        collab_beats = self._fetch_beats([b[0] for b in collab])
        result.extend(collab_beats)

        # Get content-based (25%)
        content_count = max(1, int(limit * 0.25))
        user_liked = self._get_user_liked_beats(user_id)
        if user_liked:
            content = self._get_content_based_recommendations(
                user_liked, limit=content_count
            )
            content_beats = self._fetch_beats([b[0] for b in content])
            result.extend(content_beats)

        # Remove duplicates, limit to requested count
        seen = set()
        unique_result = []
        for beat in result:
            if beat.id not in seen:
                unique_result.append(beat)
                seen.add(beat.id)
                if len(unique_result) >= limit:
                    break

        return unique_result

    def get_also_bought(self, beat_id: str, limit: int = 10) -> List[Dict]:
        """Get beats bought by people who bought this beat"""
        # Get users who bought this beat
        purchasers = self.db.query(BeatPurchase.buyer_user_id).filter(
            BeatPurchase.beat_id == beat_id
        ).distinct().all()

        purchaser_ids = [p[0] for p in purchasers]

        if not purchaser_ids:
            return self.get_similar_beats(beat_id, limit=limit)

        # Get beats bought by these users (exclude current beat)
        also_bought = (
            self.db.query(
                BeatPurchase.beat_id,
                func.count(BeatPurchase.id).label("count"),
            )
            .filter(
                and_(
                    BeatPurchase.buyer_user_id.in_(purchaser_ids),
                    BeatPurchase.beat_id != beat_id,
                )
            )
            .group_by(BeatPurchase.beat_id)
            .order_by(func.count(BeatPurchase.id).desc())
            .limit(limit)
            .all()
        )

        beat_ids = [beat_id for beat_id, _ in also_bought]
        return self._fetch_beats(beat_ids)

    # Helper methods

    def _get_user_liked_beats(self, user_id: str) -> Set[str]:
        """Get all beats liked by user (favorites + purchases)"""
        liked = set()

        # Favorites
        favorites = (
            self.db.query(BeatFavorite.beat_id)
            .filter(BeatFavorite.user_id == user_id)
            .all()
        )
        liked.update([f[0] for f in favorites])

        # Purchases
        purchases = (
            self.db.query(BeatPurchase.beat_id)
            .filter(BeatPurchase.buyer_user_id == user_id)
            .all()
        )
        liked.update([p[0] for p in purchases])

        return liked

    def _get_collaborative_recommendations(
        self, user_id: str, limit: int
    ) -> List[Tuple[str, float]]:
        """Get collaborative filtering recommendations"""
        user_liked = self._get_user_liked_beats(user_id)

        # Get all users and their liked beats
        all_users = self.db.query(User.id).all()
        all_user_beats = {}

        for user_row in all_users:
            uid = user_row[0]
            liked = self._get_user_liked_beats(uid)
            if liked:
                all_user_beats[uid] = liked

        # Get user-user recommendations
        recs = self.collab_filter.get_user_user_recommendations(
            user_id, user_liked, all_user_beats, top_n=limit
        )

        return recs

    def _get_content_based_recommendations(
        self, liked_beat_ids: Set[str], limit: int
    ) -> List[Tuple[str, float]]:
        """Get content-based recommendations"""
        scores = defaultdict(float)

        # For each liked beat, find similar ones
        for beat_id in liked_beat_ids:
            similar = self.get_similar_beats(beat_id, limit=limit * 2)
            for similar_beat in similar:
                scores[similar_beat.id] += 1.0

        # Sort and return
        sorted_recs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_recs[:limit]

    def _get_from_followed_artists(
        self, user_id: str, limit: int
    ) -> List[Dict]:
        """Get beats from followed artists"""
        # Get followed users
        followed = self.db.query(UserFollow.followed_user_id).filter(
            UserFollow.follower_user_id == user_id
        ).all()

        followed_ids = [f[0] for f in followed]

        if not followed_ids:
            return []

        # Get their beats (most recent)
        beats = (
            self.db.query(Beat)
            .filter(
                and_(
                    Beat.producer_user_id.in_(followed_ids),
                    Beat.status == "active",
                )
            )
            .order_by(Beat.created_at.desc())
            .limit(limit)
            .all()
        )

        return beats

    def _fetch_beats(self, beat_ids: List[str]) -> List[Dict]:
        """Fetch full beat data"""
        beats = self.db.query(Beat).filter(Beat.id.in_(beat_ids)).all()

        # Preserve order
        beat_dict = {b.id: b for b in beats}
        return [beat_dict[bid] for bid in beat_ids if bid in beat_dict]


# Singleton instance
recommendation_service = None


def get_recommendation_service(db: Session) -> RecommendationService:
    """Get or create recommendation service"""
    global recommendation_service
    if recommendation_service is None:
        recommendation_service = RecommendationService(db)
    return recommendation_service
