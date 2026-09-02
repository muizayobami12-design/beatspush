"""
Fix security_events table schema
The table has 'metadata' but the model expects 'event_metadata'
"""

from sqlalchemy import create_engine, text, inspect

DATABASE_URL = "sqlite:///./beatpush.db"

print("=" * 60)
print("🔧 FIXING SECURITY_EVENTS TABLE")
print("=" * 60)

# Create engine
engine = create_engine(DATABASE_URL)

# Check current schema
print("\n1️⃣  Checking current schema...")
inspector = inspect(engine)
columns = inspector.get_columns('security_events')
print(f"   Found {len(columns)} columns:")
for col in columns:
    print(f"   - {col['name']} ({col['type']})")

# Check if 'metadata' exists and 'event_metadata' doesn't
has_metadata = any(col['name'] == 'metadata' for col in columns)
has_event_metadata = any(col['name'] == 'event_metadata' for col in columns)

print(f"\n   has 'metadata': {has_metadata}")
print(f"   has 'event_metadata': {has_event_metadata}")

if has_metadata and not has_event_metadata:
    print("\n2️⃣  Renaming 'metadata' to 'event_metadata'...")
    with engine.connect() as conn:
        # SQLite doesn't support RENAME COLUMN directly
        # We need to recreate the table
        
        # Step 1: Create new table with correct schema
        conn.execute(text("""
            CREATE TABLE security_events_new (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                user_id TEXT,
                ip_address TEXT,
                device_id TEXT,
                user_agent TEXT,
                country TEXT,
                risk_score REAL,
                flags TEXT,
                decision TEXT,
                event_metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
        print("   ✅ New table created")
        
        # Step 2: Copy data
        conn.execute(text("""
            INSERT INTO security_events_new 
            SELECT id, event_type, user_id, ip_address, device_id, user_agent,
                   country, risk_score, flags, decision, metadata as event_metadata, created_at
            FROM security_events
        """))
        conn.commit()
        print("   ✅ Data copied")
        
        # Step 3: Drop old table
        conn.execute(text("DROP TABLE security_events"))
        conn.commit()
        print("   ✅ Old table dropped")
        
        # Step 4: Rename new table
        conn.execute(text("ALTER TABLE security_events_new RENAME TO security_events"))
        conn.commit()
        print("   ✅ Table renamed")
        
        # Step 5: Recreate indexes
        conn.execute(text("CREATE INDEX ix_security_events_event_type ON security_events (event_type)"))
        conn.execute(text("CREATE INDEX ix_security_events_user_id ON security_events (user_id)"))
        conn.execute(text("CREATE INDEX ix_security_events_id ON security_events (id)"))
        conn.commit()
        print("   ✅ Indexes recreated")
    
    print("\n✅ Schema fixed successfully!")

elif has_event_metadata:
    print("\n✅ Schema is already correct (has 'event_metadata')")

else:
    print("\n⚠️  Table needs to be recreated from scratch")
    print("   Run: python -c 'from app.db.database import Base, engine; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)'")

print("\n" + "=" * 60)
print("✅ DONE!")
print("=" * 60)
