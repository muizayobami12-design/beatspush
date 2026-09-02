"""Check which tables from migration 004 already exist"""
from app.db.database import engine
from sqlalchemy import inspect

# Tables that migration 004 should create
migration_004_tables = [
    'promotion_packages',
    'ai_conversations',
    'copyright_detections',
    'beat_recommendations',
    'producer_matchmaking',
    'social_accounts',
    'post_drafts',
    'platform_metrics',
    'payment_plans',
    'free_tier_usage',
    'bundle_purchases',
]

# Columns migration 004 should add to existing tables
migration_004_columns = {
    'campaigns': ['package_id', 'payment_id', 'paid_amount_currency', 'paid_amount', 
                  'paid_amount_ngn', 'target_countries', 'target_platforms', 
                  'budget_spent_ngn', 'earnings_ngn', 'total_reach', 'total_plays',
                  'total_likes', 'total_shares', 'total_comments', 'started_at', 'ends_at'],
    'beats': ['price_tiktok', 'price_instagram', 'price_facebook', 'price_spotify',
              'price_apple_music', 'copyright_status', 'copyright_scan_id'],
    'users': ['ai_conversation_enabled', 'default_target_countries']
}

insp = inspect(engine)
existing_tables = set(insp.get_table_names())

print("=" * 70)
print("MIGRATION 004 STATUS CHECK")
print("=" * 70)

print("\n📋 NEW TABLES:")
for table in migration_004_tables:
    status = "✅ EXISTS" if table in existing_tables else "❌ MISSING"
    print(f"  {status}: {table}")

print("\n📋 COLUMN ADDITIONS:")
for table, columns in migration_004_columns.items():
    if table in existing_tables:
        existing_columns = {col['name'] for col in insp.get_columns(table)}
        print(f"\n  Table: {table}")
        for col in columns:
            status = "✅ EXISTS" if col in existing_columns else "❌ MISSING"
            print(f"    {status}: {col}")
    else:
        print(f"\n  ⚠️  Table '{table}' doesn't exist - can't check columns")

print("\n" + "=" * 70)
