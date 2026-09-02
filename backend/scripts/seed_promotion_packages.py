"""
Seed Promotion Packages
Creates 6 tiers: Free, Mini, Starter, Growth, Pro, Premium
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import SessionLocal
import uuid
import json


PROMOTION_PACKAGES = [
    {
        "id": str(uuid.uuid4()),
        "name": "Free",
        "slug": "free",
        "price_ngn": 0,
        "duration_days": 0,
        "max_platforms": 0,
        "max_countries": 0,
        "estimated_reach": 0,
        "ad_spend_budget_ngn": 0,
        "features": {
            "ai_tools": [
                "Beat Analyzer (BPM, key, mood, quality score)",
                "Caption Generator (3 free per beat)",
                "Copyright Scanner (1 free per week)",
                "Best Posting Time Calculator",
                "Social Media Scheduler"
            ],
            "organic_posting": True,
            "paid_ads": False,
            "analytics": "basic",
            "target_audience": "Brand new artists, testing platform"
        },
        "is_active": True,
        "sort_order": 0
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Mini",
        "slug": "mini",
        "price_ngn": 5000,
        "duration_days": 3,
        "max_platforms": 1,
        "max_countries": 1,
        "estimated_reach": 5000,
        "ad_spend_budget_ngn": 3000,
        "features": {
            "platforms": ["Meta (Facebook + Instagram)"],
            "targeting": ["Nigeria only"],
            "analytics": True,
            "optimization": False,
            "purpose": "Testing which beats resonate",
            "target_audience": "First-time promotion buyers"
        },
        "is_active": True,
        "sort_order": 1
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Starter",
        "slug": "starter",
        "price_ngn": 25000,
        "duration_days": 7,
        "max_platforms": 1,
        "max_countries": 1,
        "estimated_reach": 20000,
        "ad_spend_budget_ngn": 15000,
        "features": {
            "platforms": ["Meta (Facebook + Instagram)"],
            "targeting": ["Nigeria only"],
            "analytics": True,
            "optimization": False,
            "split_payment": True,
            "pay_after_earnings": True,
            "split_options": "₦15K now + ₦10K in 1 week",
            "pae_terms": "30% of sales, ₦5K minimum",
            "target_audience": "Upcoming artists, first paid campaign"
        },
        "is_active": True,
        "sort_order": 2
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Growth",
        "slug": "growth",
        "price_ngn": 75000,
        "duration_days": 14,
        "max_platforms": 2,
        "max_countries": 2,
        "estimated_reach": 75000,
        "ad_spend_budget_ngn": 50000,
        "features": {
            "platforms": ["Meta (Facebook + Instagram)", "TikTok"],
            "targeting": ["Choose 2 countries: NG, GH, KE, ZA"],
            "analytics": True,
            "optimization": True,
            "ab_testing": True,
            "weekly_reports": True,
            "split_payment": True,
            "pay_after_earnings": True,
            "split_options": "₦40K now + ₦35K in 1 week",
            "pae_terms": "30% of sales, ₦5K minimum",
            "target_audience": "Artists with some traction"
        },
        "is_active": True,
        "sort_order": 3
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Pro",
        "slug": "pro",
        "price_ngn": 200000,
        "duration_days": 21,
        "max_platforms": 3,
        "max_countries": 2,
        "estimated_reach": 200000,
        "ad_spend_budget_ngn": 140000,
        "features": {
            "platforms": ["Meta (Facebook + Instagram)", "TikTok", "Spotify"],
            "targeting": ["Choose 2 countries: NG, GH, KE, ZA"],
            "analytics": True,
            "optimization": True,
            "ab_testing": True,
            "influencer_post": "1 micro-influencer collaboration",
            "daily_optimization": True,
            "priority_support": False,
            "split_payment": True,
            "split_options": "₦70K × 3 weekly payments",
            "target_audience": "Serious artists, proven sales"
        },
        "is_active": True,
        "sort_order": 4
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Premium",
        "slug": "premium",
        "price_ngn": 500000,
        "duration_days": 30,
        "max_platforms": 5,
        "max_countries": 4,
        "estimated_reach": 750000,
        "ad_spend_budget_ngn": 350000,
        "features": {
            "platforms": [
                "Meta (Facebook + Instagram)",
                "TikTok",
                "Spotify",
                "Apple Music",
                "YouTube"
            ],
            "targeting": ["All 4 countries: NG, GH, KE, ZA"],
            "analytics": True,
            "optimization": True,
            "ab_testing": True,
            "influencer_posts": "Multiple micro/macro influencers",
            "daily_optimization": True,
            "priority_support": True,
            "account_manager": True,
            "music_video_promotion": True,
            "split_payment": True,
            "split_options": "₦250K × 2 payments (2 weeks apart)",
            "target_audience": "Established artists, label-backed"
        },
        "is_active": True,
        "sort_order": 5
    }
]


def seed_packages(db: Session):
    """Seed promotion packages into database"""
    
    print("🌱 Seeding Promotion Packages...")
    
    # Check if packages already exist
    existing_count = db.execute(text("SELECT COUNT(*) FROM promotion_packages")).scalar()
    
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing packages. Skipping seed.")
        print("💡 To re-seed, run: DELETE FROM promotion_packages;")
        return
    
    # Insert packages (SQLite compatible - no ::jsonb cast)
    for pkg in PROMOTION_PACKAGES:
        sql = text("""
            INSERT INTO promotion_packages (
                id, name, slug, price_ngn, duration_days, 
                max_platforms, max_countries, estimated_reach, 
                ad_spend_budget_ngn, features, is_active, sort_order
            ) VALUES (
                :id, :name, :slug, :price_ngn, :duration_days,
                :max_platforms, :max_countries, :estimated_reach,
                :ad_spend_budget_ngn, :features, :is_active, :sort_order
            )
        """)
        
        db.execute(sql, {
            "id": pkg["id"],
            "name": pkg["name"],
            "slug": pkg["slug"],
            "price_ngn": pkg["price_ngn"],
            "duration_days": pkg["duration_days"],
            "max_platforms": pkg["max_platforms"],
            "max_countries": pkg["max_countries"],
            "estimated_reach": pkg["estimated_reach"],
            "ad_spend_budget_ngn": pkg["ad_spend_budget_ngn"],
            "features": json.dumps(pkg["features"]),
            "is_active": pkg["is_active"],
            "sort_order": pkg["sort_order"]
        })
        
        print(f"✅ Created {pkg['name']} package (₦{pkg['price_ngn']:,})")
    
    db.commit()
    print(f"\n🎉 Successfully seeded {len(PROMOTION_PACKAGES)} promotion packages!")
    print("\n📊 Package Summary:")
    print("=" * 80)
    print(f"{'Package':<12} {'Price':<15} {'Duration':<12} {'Platforms':<12} {'Reach':<12}")
    print("=" * 80)
    for pkg in PROMOTION_PACKAGES:
        print(f"{pkg['name']:<12} ₦{pkg['price_ngn']:<13,} {pkg['duration_days']:>2} days      {pkg['max_platforms']:>2}           {pkg['estimated_reach']:>10,}")
    print("=" * 80)


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_packages(db)
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()
