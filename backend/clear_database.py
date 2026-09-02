"""
Clear Database Script
Removes all data to start fresh for testing
"""
import os
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path("beatpush.db")

print("=" * 60)
print("🗑️  CLEARING DATABASE")
print("=" * 60)

if DB_PATH.exists():
    print(f"📊 Database found: {DB_PATH}")
    print("🔄 Clearing all data...")
    
    # Connect to database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n📋 Found {len(tables)} tables:")
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence':  # Skip internal table
            print(f"   - {table_name}")
    
    # Clear all data from all tables
    print("\n🗑️  Deleting all records...")
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence':
            try:
                cursor.execute(f"DELETE FROM {table_name}")
                count = cursor.rowcount
                print(f"   ✅ {table_name}: Deleted {count} records")
            except Exception as e:
                print(f"   ⚠️  {table_name}: {str(e)}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n✅ Database cleared successfully!")
    print("📊 All user accounts, beats, and data removed")
    
else:
    print(f"❌ Database not found: {DB_PATH}")
    print("   (This is fine if it's your first time)")

print("\n" + "=" * 60)
print("✅ READY FOR FRESH START!")
print("=" * 60)
print("\nYou can now:")
print("1. Register with a new email")
print("2. Test all features from scratch")
print("3. Start with a clean slate")
print("\n🚀 Database is ready!")
