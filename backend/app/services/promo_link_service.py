"""
Promo Link Service
Task 3.5: Promo Link Generator

Handles smart link creation, click tracking, analytics, and QR code generation.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid
import random
import string
import io
import base64
from collections import defaultdict

from app.models.promo_link import PromoLink, LinkClick, GeoRule
from app.models.track import Track
from app.schemas.promo_link import (
    PromoLinkCreateRequest,
    PromoLinkUpdateRequest,
    GeoRuleCreateRequest,
    GeoRuleUpdateRequest,
)


class PromoLinkService:
    """Service for managing promo links"""
    
    @staticmethod
    def generate_short_code(length: int = 6) -> str:
        """Generate unique short code for link"""
        # Use alphanumeric characters (exclude ambiguous ones: 0, O, l, 1, I)
        chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def create_promo_link(
        db: Session,
        user_id: str,
        request: PromoLinkCreateRequest
    ) -> PromoLink:
        """Create a new promo link"""
        # Verify track exists and belongs to user
        track = db.query(Track).filter(
            Track.id == request.track_id,
            Track.user_id == user_id
        ).first()
        
        if not track:
            raise ValueError("Track not found or doesn't belong to user")
        
        # Generate unique short code
        short_code = PromoLinkService.generate_short_code()
        while db.query(PromoLink).filter(PromoLink.short_code == short_code).first():
            short_code = PromoLinkService.generate_short_code()
        
        # Use track title if custom title not provided
        title = request.title or f"{track.title} - {track.artist_name}"
        
        # Create promo link
        promo_link = PromoLink(
            id=str(uuid.uuid4()),
            user_id=user_id,
            track_id=request.track_id,
            short_code=short_code,
            title=title,
            description=request.description,
            
            # Platform URLs
            spotify_url=request.spotify_url,
            apple_music_url=request.apple_music_url,
            youtube_url=request.youtube_url,
            tidal_url=request.tidal_url,
            soundcloud_url=request.soundcloud_url,
            audiomack_url=request.audiomack_url,
            boomplay_url=request.boomplay_url,
            deezer_url=request.deezer_url,
            
            # Use track cover art
            cover_image_url=track.cover_art_url,
            
            # Branding
            background_color=request.background_color or "#000000",
            text_color=request.text_color or "#FFFFFF",
            custom_domain=request.custom_domain,
            
            # UTM Parameters
            utm_source=request.utm_source,
            utm_medium=request.utm_medium,
            utm_campaign=request.utm_campaign,
            
            # Status
            expires_at=request.expires_at,
        )
        
        db.add(promo_link)
        db.commit()
        db.refresh(promo_link)
        
        return promo_link
    
    @staticmethod
    def get_promo_link(db: Session, link_id: str, user_id: str) -> Optional[PromoLink]:
        """Get promo link by ID"""
        return db.query(PromoLink).filter(
            PromoLink.id == link_id,
            PromoLink.user_id == user_id
        ).first()
    
    @staticmethod
    def get_promo_link_by_short_code(db: Session, short_code: str) -> Optional[PromoLink]:
        """Get promo link by short code (public access)"""
        return db.query(PromoLink).filter(
            PromoLink.short_code == short_code,
            PromoLink.is_active == True
        ).first()
    
    @staticmethod
    def update_promo_link(
        db: Session,
        link_id: str,
        user_id: str,
        request: PromoLinkUpdateRequest
    ) -> Optional[PromoLink]:
        """Update promo link"""
        promo_link = PromoLinkService.get_promo_link(db, link_id, user_id)
        if not promo_link:
            return None
        
        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(promo_link, field, value)
        
        promo_link.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(promo_link)
        
        return promo_link
    
    @staticmethod
    def delete_promo_link(db: Session, link_id: str, user_id: str) -> bool:
        """Delete promo link"""
        promo_link = PromoLinkService.get_promo_link(db, link_id, user_id)
        if not promo_link:
            return False
        
        db.delete(promo_link)
        db.commit()
        return True
    
    @staticmethod
    def get_user_links(
        db: Session,
        user_id: str,
        track_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[PromoLink], int]:
        """Get user's promo links with filters"""
        query = db.query(PromoLink).filter(PromoLink.user_id == user_id)
        
        # Filters
        if track_id:
            query = query.filter(PromoLink.track_id == track_id)
        
        if is_active is not None:
            query = query.filter(PromoLink.is_active == is_active)
        
        if search:
            query = query.filter(
                or_(
                    PromoLink.title.ilike(f"%{search}%"),
                    PromoLink.description.ilike(f"%{search}%"),
                    PromoLink.short_code.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        links = query.order_by(PromoLink.created_at.desc()).offset(skip).limit(limit).all()
        
        return links, total
    
    @staticmethod
    def track_click(
        db: Session,
        promo_link_id: str,
        platform: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referrer: Optional[str] = None,
        country: Optional[str] = None,
        region: Optional[str] = None,
        city: Optional[str] = None,
        device_type: Optional[str] = None,
        os: Optional[str] = None,
        browser: Optional[str] = None,
        session_id: Optional[str] = None,
        utm_params: Optional[Dict[str, str]] = None
    ) -> LinkClick:
        """Track a click on a promo link"""
        promo_link = db.query(PromoLink).filter(PromoLink.id == promo_link_id).first()
        if not promo_link:
            raise ValueError("Promo link not found")
        
        # Check if unique click (same session hasn't clicked before)
        is_unique = True
        if session_id:
            existing_click = db.query(LinkClick).filter(
                LinkClick.promo_link_id == promo_link_id,
                LinkClick.session_id == session_id
            ).first()
            is_unique = existing_click is None
        
        # Create click record
        click = LinkClick(
            id=str(uuid.uuid4()),
            promo_link_id=promo_link_id,
            platform=platform,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            country=country,
            region=region,
            city=city,
            device_type=device_type,
            os=os,
            browser=browser,
            session_id=session_id,
            is_unique_click=is_unique,
            utm_source=utm_params.get("utm_source") if utm_params else None,
            utm_medium=utm_params.get("utm_medium") if utm_params else None,
            utm_campaign=utm_params.get("utm_campaign") if utm_params else None,
            utm_term=utm_params.get("utm_term") if utm_params else None,
            utm_content=utm_params.get("utm_content") if utm_params else None,
        )
        
        db.add(click)
        
        # Update promo link stats
        promo_link.total_clicks += 1
        if is_unique:
            promo_link.unique_clicks += 1
        
        db.commit()
        db.refresh(click)
        
        return click
    
    @staticmethod
    def get_platform_url(
        promo_link: PromoLink,
        platform: str,
        country: Optional[str] = None
    ) -> Optional[str]:
        """Get platform URL, considering geo-targeting rules"""
        # Platform URL mapping
        platform_urls = {
            "spotify": promo_link.spotify_url,
            "apple_music": promo_link.apple_music_url,
            "youtube": promo_link.youtube_url,
            "tidal": promo_link.tidal_url,
            "soundcloud": promo_link.soundcloud_url,
            "audiomack": promo_link.audiomack_url,
            "boomplay": promo_link.boomplay_url,
            "deezer": promo_link.deezer_url,
        }
        
        return platform_urls.get(platform)
    
    @staticmethod
    def get_link_analytics(db: Session, link_id: str, user_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a promo link"""
        promo_link = PromoLinkService.get_promo_link(db, link_id, user_id)
        if not promo_link:
            return None
        
        # Get all clicks
        clicks = db.query(LinkClick).filter(LinkClick.promo_link_id == link_id).all()
        
        if not clicks:
            return {
                "promo_link_id": link_id,
                "short_code": promo_link.short_code,
                "total_clicks": 0,
                "unique_clicks": 0,
                "conversion_rate": 0.0,
                "platform_stats": {},
                "country_stats": {},
                "city_stats": {},
                "device_stats": {},
                "os_stats": {},
                "browser_stats": {},
                "daily_clicks": [],
                "top_referrers": [],
            }
        
        # Platform breakdown
        platform_stats = defaultdict(lambda: {"clicks": 0, "unique_clicks": 0})
        for click in clicks:
            platform_stats[click.platform]["clicks"] += 1
            if click.is_unique_click:
                platform_stats[click.platform]["unique_clicks"] += 1
        
        # Add percentages
        for platform, stats in platform_stats.items():
            stats["percentage"] = (stats["clicks"] / len(clicks)) * 100
        
        # Geographic breakdown
        country_stats = defaultdict(int)
        city_stats = defaultdict(int)
        for click in clicks:
            if click.country:
                country_stats[click.country] += 1
            if click.city:
                city_stats[click.city] += 1
        
        # Device breakdown
        device_stats = defaultdict(int)
        os_stats = defaultdict(int)
        browser_stats = defaultdict(int)
        for click in clicks:
            if click.device_type:
                device_stats[click.device_type] += 1
            if click.os:
                os_stats[click.os] += 1
            if click.browser:
                browser_stats[click.browser] += 1
        
        # Time series (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_clicks = [c for c in clicks if c.clicked_at >= thirty_days_ago]
        
        daily_clicks = defaultdict(int)
        for click in recent_clicks:
            date = click.clicked_at.date().isoformat()
            daily_clicks[date] += 1
        
        daily_clicks_list = [
            {"date": date, "clicks": count}
            for date, count in sorted(daily_clicks.items())
        ]
        
        # Top referrers
        referrer_stats = defaultdict(int)
        for click in clicks:
            if click.referrer:
                referrer_stats[click.referrer] += 1
        
        top_referrers = [
            {"referrer": ref, "clicks": count}
            for ref, count in sorted(referrer_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Calculate conversion rate
        unique_count = sum(1 for c in clicks if c.is_unique_click)
        conversion_rate = (unique_count / len(clicks)) * 100 if clicks else 0
        
        return {
            "promo_link_id": link_id,
            "short_code": promo_link.short_code,
            "total_clicks": len(clicks),
            "unique_clicks": unique_count,
            "conversion_rate": round(conversion_rate, 2),
            "platform_stats": dict(platform_stats),
            "country_stats": dict(country_stats),
            "city_stats": dict(city_stats),
            "device_stats": dict(device_stats),
            "os_stats": dict(os_stats),
            "browser_stats": dict(browser_stats),
            "daily_clicks": daily_clicks_list,
            "top_referrers": top_referrers,
        }
    
    @staticmethod
    def create_geo_rule(
        db: Session,
        link_id: str,
        user_id: str,
        request: GeoRuleCreateRequest
    ) -> GeoRule:
        """Create geo-targeting rule"""
        # Verify link exists and belongs to user
        promo_link = PromoLinkService.get_promo_link(db, link_id, user_id)
        if not promo_link:
            raise ValueError("Promo link not found")
        
        # Create geo rule
        geo_rule = GeoRule(
            id=str(uuid.uuid4()),
            promo_link_id=link_id,
            country_codes=",".join(request.country_codes),
            platform=request.platform,
            priority=request.priority,
            fallback_url=request.fallback_url,
        )
        
        db.add(geo_rule)
        db.commit()
        db.refresh(geo_rule)
        
        return geo_rule
    
    @staticmethod
    def generate_qr_code(promo_link: PromoLink, size: int = 300) -> str:
        """Generate QR code for promo link"""
        try:
            import qrcode
            from PIL import Image
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Use short URL
            short_url = f"https://beatpush.to/{promo_link.short_code}"
            qr.add_data(short_url)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((size, size))
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        
        except ImportError:
            # Fallback if qrcode not installed
            return None
