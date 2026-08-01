"""
Quick database check script
"""
import sqlite3

# Connect to database
conn = sqlite3.connect('beatpush.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("📊 Database Tables:")
for table in tables:
    print(f"  ✅ {table[0]}")

# Get users table structure
print("\n👤 Users table structure:")
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
for col in columns:
    print(f"  • {col[1]:20} {col[2]}")

# Count users
cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
print(f"\n📈 Total users: {count}")

conn.close()
print("\n✅ Database check complete!")
