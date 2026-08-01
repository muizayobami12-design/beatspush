"""
Create promo link tables for smart link generation and tracking
Task 3.5: Promo Link Generator
"""

import sqlite3
from datetime import datetime

def create_promo_link_tables():
    """Create promo link tables"""
    conn = sqlite3.connect('beatpush.db')
    cursor = conn.cursor()
    
    print("🔗 Creating promo link tables...")
    
    # Table 1: promo_links - Main smart link table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promo_links (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            track_id VARCHAR(36) NOT NULL,
            short_code VARCHAR(20) UNIQUE NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            
            -- Platform links
            spotify_url VARCHAR(500),
            apple_music_url VARCHAR(500),
            youtube_url VARCHAR(500),
            tidal_url VARCHAR(500),
            soundcloud_url VARCHAR(500),
            audiomack_url VARCHAR(500),
            boomplay_url VARCHAR(500),
            deezer_url VARCHAR(500),
            
            -- Branding
            cover_image_url VARCHAR(500),
            background_color VARCHAR(7) DEFAULT '#000000',
            text_color VARCHAR(7) DEFAULT '#FFFFFF',
            custom_domain VARCHAR(255),
            
            -- Analytics
            total_clicks INTEGER DEFAULT 0,
            unique_clicks INTEGER DEFAULT 0,
            
            -- UTM Parameters
            utm_source VARCHAR(100),
            utm_medium VARCHAR(100),
            utm_campaign VARCHAR(100),
            
            -- Status
            is_active BOOLEAN DEFAULT TRUE,
            expires_at DATETIME,
            
            -- Metadata
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (track_id) REFERENCES tracks (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_promo_links_user ON promo_links (user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_promo_links_track ON promo_links (track_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_promo_links_short_code ON promo_links (short_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_promo_links_created ON promo_links (created_at)")
    print("  ✅ promo_links table created")
    
    # Table 2: link_clicks - Click tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS link_clicks (
            id VARCHAR(36) PRIMARY KEY,
            promo_link_id VARCHAR(36) NOT NULL,
            
            -- Platform clicked
            platform VARCHAR(50) NOT NULL,
            
            -- Visitor info
            ip_address VARCHAR(45),
            user_agent TEXT,
            referrer VARCHAR(500),
            
            -- Location (from IP or provided)
            country VARCHAR(100),
            region VARCHAR(100),
            city VARCHAR(100),
            
            -- Device info
            device_type VARCHAR(50),
            os VARCHAR(100),
            browser VARCHAR(100),
            
            -- UTM Parameters (captured from URL)
            utm_source VARCHAR(100),
            utm_medium VARCHAR(100),
            utm_campaign VARCHAR(100),
            utm_term VARCHAR(100),
            utm_content VARCHAR(100),
            
            -- Session tracking
            session_id VARCHAR(100),
            is_unique_click BOOLEAN DEFAULT TRUE,
            
            -- Timestamp
            clicked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (promo_link_id) REFERENCES promo_links (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_link_clicks_promo_link ON link_clicks (promo_link_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_link_clicks_platform ON link_clicks (platform)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_link_clicks_country ON link_clicks (country)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_link_clicks_clicked_at ON link_clicks (clicked_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_link_clicks_session ON link_clicks (session_id)")
    print("  ✅ link_clicks table created")
    
    # Table 3: geo_rules - Geo-targeted redirect rules
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS geo_rules (
            id VARCHAR(36) PRIMARY KEY,
            promo_link_id VARCHAR(36) NOT NULL,
            
            -- Geographic targeting
            country_codes TEXT,
            
            -- Platform priority for this region
            platform VARCHAR(50) NOT NULL,
            priority INTEGER DEFAULT 0,
            
            -- Fallback URL if platform not available
            fallback_url VARCHAR(500),
            
            -- Status
            is_active BOOLEAN DEFAULT TRUE,
            
            -- Metadata
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (promo_link_id) REFERENCES promo_links (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_geo_rules_promo_link ON geo_rules (promo_link_id)")
    print("  ✅ geo_rules table created")
    
    conn.commit()
    conn.close()
    
    print("✅ All promo link tables created successfully!")
    print("\n📊 Tables created:")
    print("  1. promo_links (18 fields)")
    print("  2. link_clicks (21 fields)")
    print("  3. geo_rules (8 fields)")

if __name__ == "__main__":
    create_promo_link_tables()
