"""
Beat Service
Task 5.4: Beat Marketplace

Handles beat listing, purchasing, analytics, and earnings
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import secrets

from app.models.beat import Beat, BeatPurchase, BeatFavorite, BeatPlay, LicenseType, BeatStatus, PurchaseStatus
from app.models.user import User
from app.schemas.beat import (
    BeatCreateRequest,
    BeatUpdateRequest,
    BeatPurchaseRequest,
    BeatPlayRequest,
)


class BeatService:
    """Service for beat marketplace"""
    
    # Platform commission percentage (15%)
    PLATFORM_COMMISSION_RATE = 0.15
    
    # Default license terms
    DEFAULT_LEASE_TERMS = """
LEASE LICENSE TERMS:
- Non-exclusive rights to use the beat
- Up to 10,000 streams/copies allowed
- Cannot resell or sublicense
- Producer retains all ownership
- Valid for 2 years from purchase date
- 10 downloads allowed
"""
    
    DEFAULT_EXCLUSIVE_TERMS = """
EXCLUSIVE LICENSE TERMS:
- Full exclusive rights to the beat
- Unlimited streams/copies allowed
- Can register copyright in your name
- Producer transfers all rights
- Lifetime license (no expiration)
- Unlimited downloads
- Beat removed from marketplace after purchase
"""
    
    @staticmethod
    def create_beat(db: Session, producer_user_id: str, request: BeatCreateRequest) -> Beat:
        """Create new beat listing"""
        
        # Set default license terms if not provided
        lease_terms = request.lease_terms or BeatService.DEFAULT_LEASE_TERMS
        exclusive_terms = request.exclusive_terms or BeatService.DEFAULT_EXCLUSIVE_TERMS
        
        beat = Beat(
            id=str(uuid.uuid4()),
            producer_user_id=producer_user_id,
            title=request.title,
            description=request.description,
            tagged_audio_url=request.tagged_audio_url,
            untagged_audio_url=request.untagged_audio_url,
            cover_art_url=request.cover_art_url,
            bpm=request.bpm,
            musical_key=request.musical_key,
            genre=request.genre,
            mood=request.mood,
            duration=request.duration,
            lease_price=request.lease_price,
            exclusive_price=request.exclusive_price,
            lease_terms=lease_terms,
            exclusive_terms=exclusive_terms,
            tags=request.tags,
            status=BeatStatus.ACTIVE.value,
            published_at=datetime.utcnow(),
        )
        
        db.add(beat)
        db.commit()
        db.refresh(beat)
        
        return beat
    
    @staticmethod
    def get_beat(db: Session, beat_id: str, user_id: Optional[str] = None) -> Optional[Beat]:
        """Get beat by ID"""
        beat = db.query(Beat).filter(Beat.id == beat_id).first()
        
        if beat and user_id:
            # Check if user has favorited
            beat.is_favorited = db.query(BeatFavorite).filter(
                BeatFavorite.beat_id == beat_id,
                BeatFavorite.user_id == user_id
            ).first() is not None
            
            # Check if user has purchased
            beat.is_purchased = db.query(BeatPurchase).filter(
                BeatPurchase.beat_id == beat_id,
                BeatPurchase.buyer_user_id == user_id,
                BeatPurchase.status == PurchaseStatus.COMPLETED.value
            ).first() is not None
        
        return beat
    
    @staticmethod
    def browse_beats(
        db: Session,
        genre: Optional[str] = None,
        min_bpm: Optional[int] = None,
        max_bpm: Optional[int] = None,
        musical_key: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search: Optional[str] = None,
        sort_by: str = "newest",
        skip: int = 0,
        limit: int = 20,
        user_id: Optional[str] = None
    ) -> Tuple[List[Beat], int]:
        """Browse beats with filters"""
        
        query = db.query(Beat).filter(
            Beat.status == BeatStatus.ACTIVE.value,
            Beat.is_available == True
        )
        
        # Apply filters
        if genre:
            query = query.filter(Beat.genre == genre)
        if min_bpm:
            query = query.filter(Beat.bpm >= min_bpm)
        if max_bpm:
            query = query.filter(Beat.bpm <= max_bpm)
        if musical_key:
            query = query.filter(Beat.musical_key == musical_key)
        if min_price:
            query = query.filter(
                or_(Beat.lease_price >= min_price, Beat.exclusive_price >= min_price)
            )
        if max_price:
            query = query.filter(
                or_(Beat.lease_price <= max_price, Beat.exclusive_price <= max_price)
            )
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Beat.title.like(search_pattern),
                    Beat.description.like(search_pattern),
                    Beat.tags.like(search_pattern)
                )
            )
        
        # Get total before pagination
        total = query.count()
        
        # Apply sorting
        if sort_by == "newest":
            query = query.order_by(desc(Beat.published_at))
        elif sort_by == "popular":
            query = query.order_by(desc(Beat.play_count))
        elif sort_by == "price_low":
            query = query.order_by(Beat.lease_price.asc())
        elif sort_by == "price_high":
            query = query.order_by(Beat.lease_price.desc())
        else:
            query = query.order_by(desc(Beat.created_at))
        
        # Pagination
        beats = query.offset(skip).limit(limit).all()
        
        # Add user-specific data
        if user_id:
            for beat in beats:
                beat.is_favorited = db.query(BeatFavorite).filter(
                    BeatFavorite.beat_id == beat.id,
                    BeatFavorite.user_id == user_id
                ).first() is not None
                
                beat.is_purchased = db.query(BeatPurchase).filter(
                    BeatPurchase.beat_id == beat.id,
                    BeatPurchase.buyer_user_id == user_id,
                    BeatPurchase.status == PurchaseStatus.COMPLETED.value
                ).first() is not None
        
        return beats, total
    
    @staticmethod
    def update_beat(
        db: Session,
        beat_id: str,
        producer_user_id: str,
        request: BeatUpdateRequest
    ) -> Beat:
        """Update beat listing (producer only)"""
        
        beat = db.query(Beat).filter(
            Beat.id == beat_id,
            Beat.producer_user_id == producer_user_id
        ).first()
        
        if not beat:
            raise ValueError("Beat not found or you're not the producer")
        
        # Update fields
        if request.title:
            beat.title = request.title
        if request.description is not None:
            beat.description = request.description
        if request.cover_art_url is not None:
            beat.cover_art_url = request.cover_art_url
        if request.bpm is not None:
            beat.bpm = request.bpm
        if request.musical_key is not None:
            beat.musical_key = request.musical_key
        if request.genre is not None:
            beat.genre = request.genre
        if request.mood is not None:
            beat.mood = request.mood
        if request.lease_price is not None:
            beat.lease_price = request.lease_price
        if request.exclusive_price is not None:
            beat.exclusive_price = request.exclusive_price
        if request.lease_terms is not None:
            beat.lease_terms = request.lease_terms
        if request.exclusive_terms is not None:
            beat.exclusive_terms = request.exclusive_terms
        if request.tags is not None:
            beat.tags = request.tags
        if request.is_available is not None:
            beat.is_available = request.is_available
        
        beat.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(beat)
        
        return beat
    
    @staticmethod
    def delete_beat(db: Session, beat_id: str, producer_user_id: str) -> bool:
        """Delete beat (producer only, no sales)"""
        
        beat = db.query(Beat).filter(
            Beat.id == beat_id,
            Beat.producer_user_id == producer_user_id
        ).first()
        
        if not beat:
            raise ValueError("Beat not found or you're not the producer")
        
        # Check if beat has any sales
        if beat.purchase_count > 0:
            raise ValueError("Cannot delete beat with existing sales")
        
        db.delete(beat)
        db.commit()
        
        return True
    
    @staticmethod
    def purchase_beat(
        db: Session,
        beat_id: str,
        buyer_user_id: str,
        request: BeatPurchaseRequest
    ) -> BeatPurchase:
        """Purchase beat"""
        
        beat = db.query(Beat).filter(Beat.id == beat_id).first()
        
        if not beat:
            raise ValueError("Beat not found")
        
        if not beat.is_available:
            raise ValueError("Beat is not available")
        
        # Can't buy your own beat
        if buyer_user_id == beat.producer_user_id:
            raise ValueError("Cannot purchase your own beat")
        
        # Validate license type
        if request.license_type not in [LicenseType.LEASE.value, LicenseType.EXCLUSIVE.value]:
            raise ValueError("Invalid license type")
        
        # Check exclusive availability
        if request.license_type == LicenseType.EXCLUSIVE.value:
            if beat.is_exclusive_sold:
                raise ValueError("Exclusive rights already sold")
        
        # Get price
        if request.license_type == LicenseType.LEASE.value:
            if not beat.lease_price:
                raise ValueError("Lease not available for this beat")
            purchase_price = beat.lease_price
        else:  # exclusive
            if not beat.exclusive_price:
                raise ValueError("Exclusive not available for this beat")
            purchase_price = beat.exclusive_price
        
        # Calculate fees
        platform_commission = purchase_price * BeatService.PLATFORM_COMMISSION_RATE
        producer_payout = purchase_price - platform_commission
        
        # Generate license key
        license_key = f"BT-{secrets.token_hex(8).upper()}"
        
        # Create purchase
        purchase = BeatPurchase(
            id=str(uuid.uuid4()),
            beat_id=beat_id,
            buyer_user_id=buyer_user_id,
            producer_user_id=beat.producer_user_id,
            license_type=request.license_type,
            purchase_price=purchase_price,
            platform_commission_rate=BeatService.PLATFORM_COMMISSION_RATE,
            platform_commission=platform_commission,
            producer_payout=producer_payout,
            payment_status="succeeded",  # Simulated
            license_key=license_key,
            download_url=beat.untagged_audio_url,
            status=PurchaseStatus.COMPLETED.value,
        )
        
        # Set expiration for lease (2 years)
        if request.license_type == LicenseType.LEASE.value:
            purchase.expires_at = datetime.utcnow() + timedelta(days=730)
        
        db.add(purchase)
        
        # Update beat stats
        beat.purchase_count += 1
        beat.total_revenue += purchase_price
        
        # If exclusive, mark as sold and make unavailable
        if request.license_type == LicenseType.EXCLUSIVE.value:
            beat.is_exclusive_sold = True
            beat.is_available = False
            beat.status = BeatStatus.SOLD_EXCLUSIVE.value
        
        db.commit()
        db.refresh(purchase)
        
        return purchase
    
    @staticmethod
    def get_user_purchases(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[BeatPurchase], int]:
        """Get user's beat purchases"""
        
        query = db.query(BeatPurchase).filter(BeatPurchase.buyer_user_id == user_id)
        
        total = query.count()
        purchases = query.order_by(desc(BeatPurchase.created_at)).offset(skip).limit(limit).all()
        
        return purchases, total
    
    @staticmethod
    def get_producer_sales(
        db: Session,
        producer_user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[BeatPurchase], int]:
        """Get producer's beat sales"""
        
        query = db.query(BeatPurchase).filter(BeatPurchase.producer_user_id == producer_user_id)
        
        total = query.count()
        sales = query.order_by(desc(BeatPurchase.created_at)).offset(skip).limit(limit).all()
        
        return sales, total
    
    @staticmethod
    def toggle_favorite(db: Session, beat_id: str, user_id: str) -> bool:
        """Toggle favorite status"""
        
        existing = db.query(BeatFavorite).filter(
            BeatFavorite.beat_id == beat_id,
            BeatFavorite.user_id == user_id
        ).first()
        
        if existing:
            # Unfavorite
            db.delete(existing)
            
            # Update count
            beat = db.query(Beat).filter(Beat.id == beat_id).first()
            if beat:
                beat.favorite_count = max(0, beat.favorite_count - 1)
            
            db.commit()
            return False
        else:
            # Favorite
            favorite = BeatFavorite(
                id=str(uuid.uuid4()),
                beat_id=beat_id,
                user_id=user_id
            )
            db.add(favorite)
            
            # Update count
            beat = db.query(Beat).filter(Beat.id == beat_id).first()
            if beat:
                beat.favorite_count += 1
            
            db.commit()
            return True
    
    @staticmethod
    def get_user_favorites(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Beat], int]:
        """Get user's favorite beats"""
        
        query = db.query(Beat).join(BeatFavorite).filter(
            BeatFavorite.user_id == user_id
        )
        
        total = query.count()
        beats = query.order_by(desc(BeatFavorite.created_at)).offset(skip).limit(limit).all()
        
        return beats, total
    
    @staticmethod
    def track_play(
        db: Session,
        beat_id: str,
        user_id: Optional[str],
        request: BeatPlayRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> BeatPlay:
        """Track beat play"""
        
        play = BeatPlay(
            id=str(uuid.uuid4()),
            beat_id=beat_id,
            user_id=user_id,
            duration_played=request.duration_played,
            completed=request.completed,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(play)
        
        # Update play count
        beat = db.query(Beat).filter(Beat.id == beat_id).first()
        if beat:
            beat.play_count += 1
        
        db.commit()
        db.refresh(play)
        
        return play
    
    @staticmethod
    def get_beat_stats(db: Session, producer_user_id: str) -> Dict[str, Any]:
        """Get beat statistics for producer"""
        
        # Beat counts
        total_beats = db.query(func.count(Beat.id)).filter(
            Beat.producer_user_id == producer_user_id
        ).scalar() or 0
        
        active_beats = db.query(func.count(Beat.id)).filter(
            Beat.producer_user_id == producer_user_id,
            Beat.status == BeatStatus.ACTIVE.value
        ).scalar() or 0
        
        # Sales stats
        sales_stats = db.query(
            func.count(BeatPurchase.id),
            func.sum(BeatPurchase.purchase_price)
        ).filter(
            BeatPurchase.producer_user_id == producer_user_id,
            BeatPurchase.status == PurchaseStatus.COMPLETED.value
        ).first()
        
        total_sales = sales_stats[0] or 0
        total_revenue = float(sales_stats[1] or 0)
        
        # License breakdown
        lease_sales = db.query(func.count(BeatPurchase.id)).filter(
            BeatPurchase.producer_user_id == producer_user_id,
            BeatPurchase.license_type == LicenseType.LEASE.value,
            BeatPurchase.status == PurchaseStatus.COMPLETED.value
        ).scalar() or 0
        
        exclusive_sales = db.query(func.count(BeatPurchase.id)).filter(
            BeatPurchase.producer_user_id == producer_user_id,
            BeatPurchase.license_type == LicenseType.EXCLUSIVE.value,
            BeatPurchase.status == PurchaseStatus.COMPLETED.value
        ).scalar() or 0
        
        # Top beats
        top_beats = db.query(Beat).filter(
            Beat.producer_user_id == producer_user_id
        ).order_by(desc(Beat.total_revenue)).limit(5).all()
        
        # Recent purchases
        recent_purchases = db.query(BeatPurchase).filter(
            BeatPurchase.producer_user_id == producer_user_id
        ).order_by(desc(BeatPurchase.created_at)).limit(5).all()
        
        return {
            "total_beats": total_beats,
            "active_beats": active_beats,
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "lease_sales": lease_sales,
            "exclusive_sales": exclusive_sales,
            "top_beats": top_beats,
            "recent_purchases": recent_purchases,
        }
    
    @staticmethod
    def get_producer_earnings(db: Session, producer_user_id: str) -> Dict[str, Any]:
        """Get producer earnings dashboard"""
        
        # Total earnings
        earnings = db.query(
            func.sum(BeatPurchase.producer_payout)
        ).filter(
            BeatPurchase.producer_user_id == producer_user_id,
            BeatPurchase.status == PurchaseStatus.COMPLETED.value
        ).scalar() or 0.0
        
        total_earned = float(earnings)
        
        # Sales count
        total_sales = db.query(func.count(BeatPurchase.id)).filter(
            BeatPurchase.producer_user_id == producer_user_id,
            BeatPurchase.status == PurchaseStatus.COMPLETED.value
        ).scalar() or 0
        
        # Average sale price
        average_sale_price = total_earned / total_sales if total_sales > 0 else 0.0
        
        # License breakdown
        lease_revenue = db.query(func.sum(BeatPurchase.producer_payout)).filter(
            BeatPurchase.producer_user_id == producer_user_id,
            BeatPurchase.license_type == LicenseType.LEASE.value,
            BeatPurchase.status == PurchaseStatus.COMPLETED.value
        ).scalar() or 0.0
        
        exclusive_revenue = db.query(func.sum(BeatPurchase.producer_payout)).filter(
            BeatPurchase.producer_user_id == producer_user_id,
            BeatPurchase.license_type == LicenseType.EXCLUSIVE.value,
            BeatPurchase.status == PurchaseStatus.COMPLETED.value
        ).scalar() or 0.0
        
        # Top selling beats
        top_sellers = db.query(
            Beat.id,
            Beat.title,
            func.count(BeatPurchase.id).label('sales'),
            func.sum(BeatPurchase.producer_payout).label('revenue')
        ).join(
            BeatPurchase, Beat.id == BeatPurchase.beat_id
        ).filter(
            Beat.producer_user_id == producer_user_id,
            BeatPurchase.status == PurchaseStatus.COMPLETED.value
        ).group_by(
            Beat.id, Beat.title
        ).order_by(desc('revenue')).limit(5).all()
        
        top_sellers_list = [
            {
                "beat_id": seller.id,
                "beat_title": seller.title,
                "sales_count": seller.sales,
                "revenue": float(seller.revenue)
            }
            for seller in top_sellers
        ]
        
        return {
            "total_earned": total_earned,
            "pending_earnings": 0.0,  # For future implementation
            "withdrawn_earnings": 0.0,  # For future implementation
            "total_sales": total_sales,
            "average_sale_price": average_sale_price,
            "lease_revenue": float(lease_revenue),
            "exclusive_revenue": float(exclusive_revenue),
            "top_sellers": top_sellers_list,
        }
    
    @staticmethod
    def generate_license_certificate(db: Session, purchase_id: str) -> Dict[str, Any]:
        """Generate license certificate"""
        
        purchase = db.query(BeatPurchase).filter(BeatPurchase.id == purchase_id).first()
        
        if not purchase:
            raise ValueError("Purchase not found")
        
        # Get details
        beat = db.query(Beat).filter(Beat.id == purchase.beat_id).first()
        buyer = db.query(User).filter(User.id == purchase.buyer_user_id).first()
        producer = db.query(User).filter(User.id == purchase.producer_user_id).first()
        
        # Generate certificate text
        license_terms = beat.lease_terms if purchase.license_type == LicenseType.LEASE.value else beat.exclusive_terms
        
        certificate_text = f"""
BEAT LICENSE CERTIFICATE

License Key: {purchase.license_key}
License Type: {purchase.license_type.upper()}

BEAT DETAILS:
Title: {beat.title}
Producer: {producer.full_name or producer.username}
BPM: {beat.bpm or 'N/A'}
Key: {beat.musical_key or 'N/A'}
Genre: {beat.genre or 'N/A'}

LICENSEE INFORMATION:
Name: {buyer.full_name or buyer.username}
Email: {buyer.email}

PURCHASE INFORMATION:
Purchase Date: {purchase.created_at.strftime('%B %d, %Y')}
Purchase Price: {purchase.currency} {purchase.purchase_price:.2f}
{f'Expires: {purchase.expires_at.strftime("%B %d, %Y")}' if purchase.expires_at else 'Expires: Never (Lifetime)'}

LICENSE TERMS:
{license_terms}

This certificate confirms that the above licensee has purchased a {purchase.license_type} license
for the beat "{beat.title}" and is authorized to use it according to the terms above.

Certificate ID: {purchase_id}
Generated: {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}

Managed by BeatPush Platform
"""
        
        return {
            "purchase_id": purchase_id,
            "license_key": purchase.license_key,
            "license_type": purchase.license_type,
            "beat_title": beat.title,
            "producer_name": producer.full_name or producer.username,
            "buyer_name": buyer.full_name or buyer.username,
            "certificate_text": certificate_text,
            "certificate_url": None,  # Would be storage URL in production
            "generated_at": datetime.utcnow(),
        }
