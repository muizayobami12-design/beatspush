"""
Add security features to database (Day 2 migration)
Adds device tracking and security event logging
"""

import sqlite3
import sys

def add_security_features():
    """Add security fields to users table and create security_events table"""
    
    try:
        # Connect to database
        conn = sqlite3.connect('beatpush.db')
        cursor = conn.cursor()
        
        print("🔧 Adding security features to database...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add security columns to users table if they don't exist
        new_columns = {
            'device_id': 'VARCHAR(255)',
            'device_info': 'VARCHAR(1000)',
            'last_login_ip': 'VARCHAR(45)',
            'last_login_country': 'VARCHAR(2)',
            'failed_login_attempts': 'INTEGER DEFAULT 0'
        }
        
        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                print(f"  ✓ Adding column: {col_name}")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            else:
                print(f"  ⚠ Column already exists: {col_name}")
        
        # Create security_events table if it doesn't exist
        print("  ✓ Creating security_events table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id VARCHAR(36) PRIMARY KEY,
                event_type VARCHAR(50) NOT NULL,
                user_id VARCHAR(36),
                ip_address VARCHAR(45),
                device_id VARCHAR(255),
                user_agent VARCHAR(500),
                country VARCHAR(2),
                risk_score REAL,
                flags TEXT,
                decision VARCHAR(20),
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        print("  ✓ Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_device_id ON users(device_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_security_events_event_type ON security_events(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_security_events_user_id ON security_events(user_id)")
        
        # Commit changes
        conn.commit()
        
        print("\n✅ Security features added successfully!")
        print("\nNew user columns:")
        for col_name in new_columns.keys():
            print(f"  - {col_name}")
        print("\nNew tables:")
        print("  - security_events")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM security_events")
        count = cursor.fetchone()[0]
        print(f"\nVerification: security_events table has {count} rows")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = add_security_features()
    sys.exit(0 if success else 1)
