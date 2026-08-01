"""
Seed campaign templates into the database
"""
import uuid
from app.db.database import SessionLocal
from app.models.campaign import CampaignTemplate

# Template data
templates = [
    {
        "name": "New Release",
        "slug": "new-release",
        "description": "Promote a newly released track with excitement and energy. Perfect for track launch day.",
        "icon": "🎵",
        "prompt_strategy": {
            "tone_emphasis": "excitement",
            "keywords": ["new", "out now", "available now", "streaming everywhere", "just dropped"],
            "call_to_action": "Listen now",
            "style_notes": "High energy, create urgency, emphasize availability"
        },
        "recommended_platforms": ["instagram", "tiktok", "twitter", "facebook"]
    },
    {
        "name": "Pre-Release Teaser",
        "slug": "pre-release-teaser",
        "description": "Build anticipation before your track drops. Create mystery and excitement.",
        "icon": "🔥",
        "prompt_strategy": {
            "tone_emphasis": "mysterious",
            "keywords": ["coming soon", "dropping", "get ready", "countdown", "sneak peek"],
            "call_to_action": "Save the date",
            "style_notes": "Build anticipation, create mystery, use countdown language"
        },
        "recommended_platforms": ["instagram", "tiktok", "twitter"]
    },
    {
        "name": "Behind The Scenes",
        "slug": "behind-the-scenes",
        "description": "Share your creative process and connect authentically with fans.",
        "icon": "🎬",
        "prompt_strategy": {
            "tone_emphasis": "authentic",
            "keywords": ["behind the scenes", "making of", "studio", "creative process", "how I made"],
            "call_to_action": "Want to see more?",
            "style_notes": "Personal, authentic, showcase creativity and hard work"
        },
        "recommended_platforms": ["instagram", "tiktok", "facebook"]
    },
    {
        "name": "Fan Engagement",
        "slug": "fan-engagement",
        "description": "Engage with your audience, ask questions, and build community.",
        "icon": "💬",
        "prompt_strategy": {
            "tone_emphasis": "interactive",
            "keywords": ["let me know", "what do you think", "comment below", "tell me", "your favorite"],
            "call_to_action": "Drop a comment",
            "style_notes": "Conversational, ask questions, encourage interaction"
        },
        "recommended_platforms": ["instagram", "twitter", "facebook"]
    },
    {
        "name": "Milestone Celebration",
        "slug": "milestone-celebration",
        "description": "Celebrate achievements and thank your supporters.",
        "icon": "🎉",
        "prompt_strategy": {
            "tone_emphasis": "gratitude",
            "keywords": ["thank you", "grateful", "achieved", "milestone", "amazing", "support"],
            "call_to_action": "Thank you for the support",
            "style_notes": "Grateful, celebratory, acknowledge fans' role in success"
        },
        "recommended_platforms": ["instagram", "twitter", "facebook"]
    },
    {
        "name": "Throwback Thursday",
        "slug": "throwback-thursday",
        "description": "Share nostalgic content about your older tracks and journey.",
        "icon": "⏮️",
        "prompt_strategy": {
            "tone_emphasis": "nostalgic",
            "keywords": ["throwback", "remember when", "classic", "took me back", "nostalgia"],
            "call_to_action": "Relive the moment",
            "style_notes": "Nostalgic, storytelling, connect past to present"
        },
        "recommended_platforms": ["instagram", "twitter", "facebook"]
    }
]

def seed_templates():
    """Seed campaign templates"""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding campaign templates...")
        
        # Check if templates already exist
        existing_count = db.query(CampaignTemplate).count()
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing templates. Skipping seed.")
            return
        
        # Create templates
        created_count = 0
        for template_data in templates:
            template = CampaignTemplate(
                id=str(uuid.uuid4()),
                **template_data
            )
            db.add(template)
            created_count += 1
            print(f"  ✅ Created: {template.name}")
        
        db.commit()
        print(f"\n✅ Successfully seeded {created_count} campaign templates!")
        
        # Verify
        total = db.query(CampaignTemplate).count()
        print(f"📊 Total templates in database: {total}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding templates: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_templates()
