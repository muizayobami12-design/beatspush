"""
Create campaign tables in the database
"""
from app.db.database import engine, Base
from app.models.campaign import Campaign, CampaignContent, CampaignTemplate, CampaignActivityLog

print("Creating campaign tables...")

# Import all models to register them
from app.models import *

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ Campaign tables created successfully!")

# Verify tables
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()

campaign_tables = [t for t in tables if 'campaign' in t]
print(f"\n📊 Campaign tables in database:")
for table in campaign_tables:
    print(f"  - {table}")

if len(campaign_tables) == 4:
    print(f"\n✅ All 4 campaign tables created successfully!")
else:
    print(f"\n⚠️  Expected 4 tables, found {len(campaign_tables)}")
