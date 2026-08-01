"""
Create tips tables for tipping system
Task 5.2: Tipping System
"""

import sqlite3
from datetime import datetime

def create_tips_tables():
    """Create tipping system tables"""
    conn = sqlite3.connect('beatpush.db')
    cursor = conn.cursor()
    
    print("💰 Creating tipping tables...")
    
    # Table 1: tips - Main tips table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tips (
            id VARCHAR(36) PRIMARY KEY,
            
            -- Parties
            from_user_id VARCHAR(36) NOT NULL,
            to_user_id VARCHAR(36) NOT NULL,
            
            -- Amount
            amount REAL NOT NULL,
            currency VARCHAR(3) DEFAULT 'USD',
            
            -- Optional context
            track_id VARCHAR(36),
            campaign_id VARCHAR(36),
            message TEXT,
            
            -- Privacy
            is_anonymous BOOLEAN DEFAULT FALSE,
            
            -- Payment details
            payment_method VARCHAR(50),
            payment_status VARCHAR(20) DEFAULT 'pending',
            payment_provider VARCHAR(50),
            payment_transaction_id VARCHAR(255),
            
            -- Platform fee (2-3%)
            platform_fee REAL DEFAULT 0.0,
            net_amount REAL NOT NULL,
            
            -- Status
            status VARCHAR(20) DEFAULT 'completed',
            
            -- Timestamps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            paid_at DATETIME,
            
            FOREIGN KEY (from_user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (to_user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (track_id) REFERENCES tracks (id) ON DELETE SET NULL,
            FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE SET NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tips_from_user ON tips (from_user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tips_to_user ON tips (to_user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tips_track ON tips (track_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tips_status ON tips (status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tips_created ON tips (created_at)")
    print("  ✅ tips table created")
    
    # Table 2: tip_withdrawals - Withdrawal requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tip_withdrawals (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            
            -- Amount
            amount REAL NOT NULL,
            currency VARCHAR(3) DEFAULT 'USD',
            
            -- Withdrawal details
            withdrawal_method VARCHAR(50) NOT NULL,
            account_details TEXT,
            
            -- Status
            status VARCHAR(20) DEFAULT 'pending',
            
            -- Processing
            processed_by VARCHAR(36),
            processed_at DATETIME,
            transaction_id VARCHAR(255),
            
            -- Notes
            notes TEXT,
            rejection_reason TEXT,
            
            -- Timestamps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_withdrawals_user ON tip_withdrawals (user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_withdrawals_status ON tip_withdrawals (status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_withdrawals_created ON tip_withdrawals (created_at)")
    print("  ✅ tip_withdrawals table created")
    
    # Table 3: user_balances - User balance tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_balances (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) UNIQUE NOT NULL,
            
            -- Balance
            available_balance REAL DEFAULT 0.0,
            pending_balance REAL DEFAULT 0.0,
            total_earned REAL DEFAULT 0.0,
            total_withdrawn REAL DEFAULT 0.0,
            
            -- Currency
            currency VARCHAR(3) DEFAULT 'USD',
            
            -- Timestamps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_balances_user ON user_balances (user_id)")
    print("  ✅ user_balances table created")
    
    conn.commit()
    conn.close()
    
    print("✅ All tipping tables created successfully!")
    print("\n💰 Tables created:")
    print("  1. tips (18 fields)")
    print("  2. tip_withdrawals (13 fields)")
    print("  3. user_balances (8 fields)")

if __name__ == "__main__":
    create_tips_tables()
