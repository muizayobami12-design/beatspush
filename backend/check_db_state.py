"""Check current database state"""
from app.db.database import engine
from sqlalchemy import inspect, text

# Check existing tables
insp = inspect(engine)
tables = sorted(insp.get_table_names())

print("=" * 60)
print("EXISTING TABLES IN DATABASE:")
print("=" * 60)
for t in tables:
    print(f"  ✓ {t}")
print(f"\nTotal: {len(tables)} tables")

# Check alembic version
print("\n" + "=" * 60)
print("ALEMBIC VERSION:")
print("=" * 60)
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT version_num FROM alembic_version'))
        version = result.scalar()
        print(f"  Current migration: {version}")
except Exception as e:
    print(f"  ⚠️  No alembic_version table found: {e}")

print("=" * 60)
