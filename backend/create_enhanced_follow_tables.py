"""
Database setup for Enhanced Follow System (Task 7.3)
Adds verified badges, notifications, and follow suggestions
"""

import sqlite3
from datetime import datetime

def create_enhanced_follow_tables():
    conn = sqlite3.connect('beatpush.db')
    cursor = conn.cursor()
    
    print("Creating enhanced follow system tables...")
    
    # 1. Add verified columns to users table
    print("1. Adding verification columns to users table...")
    try:
        cursor.execute('''
            ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0
        ''')
        cursor.execute('''
            ALTER TABLE users ADD COLUMN verification_date TIMESTAMP
        ''')
        cursor.execute('''
            ALTER TABLE users ADD COLUMN verification_badge_type VARCHAR(50) DEFAULT 'standard'
        ''')
        print("   ✓ Verification columns added to users")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("   ⚠ Verification columns already exist")
        else:
            raise
    
    # 2. User Verification Requests table
    print("2. Creating user_verifications table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_verifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            reason TEXT,
            social_links TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            reviewed_by TEXT,
            rejection_reason TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    print("   ✓ user_verifications table created")
    
    # 3. Notifications table
    print("3. Creating notifications table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            data TEXT,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    print("   ✓ notifications table created")
    
    # 4. Follow Suggestions table
    print("4. Creating follow_suggestions table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS follow_suggestions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            suggested_user_id TEXT NOT NULL,
            reason VARCHAR(255),
            suggestion_type VARCHAR(50),
            score FLOAT DEFAULT 0,
            is_dismissed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            dismissed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (suggested_user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, suggested_user_id)
        )
    ''')
    print("   ✓ follow_suggestions table created")
    
    # 5. Trending Creators Cache table
    print("5. Creating trending_creators table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trending_creators (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            trending_score FLOAT DEFAULT 0,
            follower_growth_rate FLOAT DEFAULT 0,
            engagement_rate FLOAT DEFAULT 0,
            period_start TIMESTAMP NOT NULL,
            period_end TIMESTAMP NOT NULL,
            genre VARCHAR(100),
            location VARCHAR(100),
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    print("   ✓ trending_creators table created")
    
    # 6. Notification Preferences table
    print("6. Creating notification_preferences table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_preferences (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL UNIQUE,
            new_follower BOOLEAN DEFAULT 1,
            mutual_follow BOOLEAN DEFAULT 1,
            verification_granted BOOLEAN DEFAULT 1,
            follow_suggestion BOOLEAN DEFAULT 1,
            follower_milestone BOOLEAN DEFAULT 1,
            post_like BOOLEAN DEFAULT 1,
            post_comment BOOLEAN DEFAULT 1,
            post_share BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    print("   ✓ notification_preferences table created")
    
    # Create indices for performance
    print("\n7. Creating indices...")
    
    indices = [
        ('idx_user_verifications_user_id', 'user_verifications', 'user_id'),
        ('idx_user_verifications_status', 'user_verifications', 'status'),
        ('idx_notifications_user_id', 'notifications', 'user_id'),
        ('idx_notifications_type', 'notifications', 'type'),
        ('idx_notifications_is_read', 'notifications', 'is_read'),
        ('idx_notifications_created_at', 'notifications', 'created_at'),
        ('idx_follow_suggestions_user_id', 'follow_suggestions', 'user_id'),
        ('idx_follow_suggestions_suggested_user', 'follow_suggestions', 'suggested_user_id'),
        ('idx_follow_suggestions_dismissed', 'follow_suggestions', 'is_dismissed'),
        ('idx_trending_creators_user_id', 'trending_creators', 'user_id'),
        ('idx_trending_creators_score', 'trending_creators', 'trending_score'),
        ('idx_trending_creators_genre', 'trending_creators', 'genre'),
        ('idx_trending_creators_period', 'trending_creators', 'period_start, period_end'),
        ('idx_users_verified', 'users', 'is_verified'),
    ]
    
    for index_name, table_name, columns in indices:
        try:
            cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({columns})')
            print(f"   ✓ Index {index_name} created")
        except Exception as e:
            print(f"   ⚠ Index {index_name} skipped: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Enhanced follow system tables created successfully!")
    print("\nSummary:")
    print("- Modified: users table (added is_verified, verification_date, verification_badge_type)")
    print("- Created: user_verifications table")
    print("- Created: notifications table")
    print("- Created: follow_suggestions table")
    print("- Created: trending_creators table")
    print("- Created: notification_preferences table")
    print("- Created: 14 indices for performance")

if __name__ == "__main__":
    create_enhanced_follow_tables()
