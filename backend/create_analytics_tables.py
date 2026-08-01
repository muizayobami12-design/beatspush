"""
Create analytics tables for unified dashboard
Task 4.2: Unified Analytics Dashboard
"""

import sqlite3
from datetime import datetime

def create_analytics_tables():
    """Create analytics tables"""
    conn = sqlite3.connect('beatpush.db')
    cursor = conn.cursor()
    
    print("📊 Creating analytics tables...")
    
    # Table 1: user_activity - Track all user activities
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activity (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            
            -- Activity details
            activity_type VARCHAR(50) NOT NULL,
            activity_data TEXT,
            
            -- Context
            ip_address VARCHAR(45),
            user_agent TEXT,
            
            -- Timestamp
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_user ON user_activity (user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_type ON user_activity (activity_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_created ON user_activity (created_at)")
    print("  ✅ user_activity table created")
    
    # Table 2: daily_stats - Aggregated daily statistics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            date DATETIME NOT NULL,
            
            -- Track stats
            total_tracks INTEGER DEFAULT 0,
            tracks_uploaded INTEGER DEFAULT 0,
            
            -- Engagement stats
            total_plays INTEGER DEFAULT 0,
            total_likes INTEGER DEFAULT 0,
            total_shares INTEGER DEFAULT 0,
            total_downloads INTEGER DEFAULT 0,
            
            -- Campaign stats
            campaigns_created INTEGER DEFAULT 0,
            campaigns_active INTEGER DEFAULT 0,
            
            -- Promo link stats
            promo_links_created INTEGER DEFAULT 0,
            promo_link_clicks INTEGER DEFAULT 0,
            promo_link_unique_clicks INTEGER DEFAULT 0,
            
            -- Revenue stats
            revenue REAL DEFAULT 0.0,
            tips_received REAL DEFAULT 0.0,
            
            -- Timestamps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_stats_user ON daily_stats (user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats (date)")
    print("  ✅ daily_stats table created")
    
    conn.commit()
    conn.close()
    
    print("✅ All analytics tables created successfully!")
    print("\n📊 Tables created:")
    print("  1. user_activity (6 fields)")
    print("  2. daily_stats (18 fields)")

if __name__ == "__main__":
    create_analytics_tables()
