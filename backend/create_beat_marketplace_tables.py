"""
Create beat marketplace tables
Task 5.4: Beat Marketplace
"""

import sqlite3
from datetime import datetime

def create_beat_marketplace_tables():
    """Create beat marketplace tables"""
    conn = sqlite3.connect('beatpush.db')
    cursor = conn.cursor()
    
    print("🎵 Creating beat marketplace tables...")
    
    # Table 1: beats - Main beats/instrumentals listing
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beats (
            id VARCHAR(36) PRIMARY KEY,
            
            -- Producer
            producer_user_id VARCHAR(36) NOT NULL,
            
            -- Beat details
            title VARCHAR(255) NOT NULL,
            description TEXT,
            
            -- Audio files
            tagged_audio_url VARCHAR(500) NOT NULL,
            untagged_audio_url VARCHAR(500),
            waveform_url VARCHAR(500),
            cover_art_url VARCHAR(500),
            
            -- Technical details
            bpm INTEGER,
            musical_key VARCHAR(10),
            genre VARCHAR(100),
            mood VARCHAR(100),
            duration INTEGER,
            
            -- Pricing (in USD)
            lease_price REAL,
            exclusive_price REAL,
            
            -- License terms
            lease_terms TEXT,
            exclusive_terms TEXT,
            
            -- Availability
            is_available BOOLEAN DEFAULT TRUE,
            is_exclusive_sold BOOLEAN DEFAULT FALSE,
            
            -- Statistics
            play_count INTEGER DEFAULT 0,
            favorite_count INTEGER DEFAULT 0,
            purchase_count INTEGER DEFAULT 0,
            total_revenue REAL DEFAULT 0.0,
            
            -- Platform
            platform_commission_rate REAL DEFAULT 0.15,
            
            -- Metadata
            tags TEXT,
            
            -- Status
            status VARCHAR(20) DEFAULT 'active',
            
            -- Timestamps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            published_at DATETIME,
            
            FOREIGN KEY (producer_user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_beats_producer ON beats (producer_user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_beats_genre ON beats (genre)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_beats_bpm ON beats (bpm)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_beats_status ON beats (status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_beats_created ON beats (created_at)")
    print("  ✅ beats table created")
    
    # Table 2: beat_purchases - Purchase history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beat_purchases (
            id VARCHAR(36) PRIMARY KEY,
            
            -- Parties
            beat_id VARCHAR(36) NOT NULL,
            buyer_user_id VARCHAR(36) NOT NULL,
            producer_user_id VARCHAR(36) NOT NULL,
            
            -- Purchase details
            license_type VARCHAR(20) NOT NULL,
            purchase_price REAL NOT NULL,
            currency VARCHAR(3) DEFAULT 'USD',
            
            -- Platform fee
            platform_commission_rate REAL NOT NULL,
            platform_commission REAL NOT NULL,
            producer_payout REAL NOT NULL,
            
            -- Payment
            payment_status VARCHAR(20) DEFAULT 'pending',
            payment_transaction_id VARCHAR(255),
            
            -- License
            license_certificate_url VARCHAR(500),
            license_key VARCHAR(100),
            
            -- Download
            download_url VARCHAR(500),
            download_count INTEGER DEFAULT 0,
            download_limit INTEGER DEFAULT 10,
            
            -- Status
            status VARCHAR(20) DEFAULT 'completed',
            
            -- Timestamps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            
            FOREIGN KEY (beat_id) REFERENCES beats (id) ON DELETE CASCADE,
            FOREIGN KEY (buyer_user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (producer_user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_beat ON beat_purchases (beat_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_buyer ON beat_purchases (buyer_user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_producer ON beat_purchases (producer_user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_created ON beat_purchases (created_at)")
    print("  ✅ beat_purchases table created")
    
    # Table 3: beat_favorites - User favorites
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beat_favorites (
            id VARCHAR(36) PRIMARY KEY,
            beat_id VARCHAR(36) NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (beat_id) REFERENCES beats (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            
            UNIQUE(beat_id, user_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_favorites_beat ON beat_favorites (beat_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_favorites_user ON beat_favorites (user_id)")
    print("  ✅ beat_favorites table created")
    
    # Table 4: beat_plays - Play tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beat_plays (
            id VARCHAR(36) PRIMARY KEY,
            beat_id VARCHAR(36) NOT NULL,
            user_id VARCHAR(36),
            
            -- Play details
            duration_played INTEGER,
            completed BOOLEAN DEFAULT FALSE,
            
            -- Context
            ip_address VARCHAR(50),
            user_agent TEXT,
            
            -- Timestamp
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (beat_id) REFERENCES beats (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_plays_beat ON beat_plays (beat_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_plays_user ON beat_plays (user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_plays_created ON beat_plays (created_at)")
    print("  ✅ beat_plays table created")
    
    conn.commit()
    conn.close()
    
    print("✅ All beat marketplace tables created successfully!")
    print("\n🎵 Tables created:")
    print("  1. beats (30 fields)")
    print("  2. beat_purchases (20 fields)")
    print("  3. beat_favorites (4 fields)")
    print("  4. beat_plays (8 fields)")

if __name__ == "__main__":
    create_beat_marketplace_tables()
