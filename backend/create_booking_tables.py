"""
Create booking tables for booking system
Task 5.3: Booking System
"""

import sqlite3
from datetime import datetime

def create_booking_tables():
    """Create booking system tables"""
    conn = sqlite3.connect('beatpush.db')
    cursor = conn.cursor()
    
    print("📅 Creating booking tables...")
    
    # Table 1: bookings - Main bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id VARCHAR(36) PRIMARY KEY,
            
            -- Parties
            client_user_id VARCHAR(36) NOT NULL,
            artist_user_id VARCHAR(36) NOT NULL,
            
            -- Event details
            event_name VARCHAR(255) NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            event_date DATETIME NOT NULL,
            event_duration INTEGER,
            location VARCHAR(500) NOT NULL,
            venue_name VARCHAR(255),
            
            -- Financial
            budget REAL NOT NULL,
            currency VARCHAR(3) DEFAULT 'USD',
            deposit_amount REAL DEFAULT 0.0,
            platform_commission_rate REAL DEFAULT 0.125,
            platform_commission REAL DEFAULT 0.0,
            artist_payout REAL DEFAULT 0.0,
            
            -- Details
            description TEXT,
            special_requirements TEXT,
            
            -- Status
            status VARCHAR(20) DEFAULT 'pending',
            
            -- Contract & Payment
            contract_url VARCHAR(500),
            contract_signed BOOLEAN DEFAULT FALSE,
            contract_signed_at DATETIME,
            invoice_url VARCHAR(500),
            payment_status VARCHAR(20) DEFAULT 'pending',
            payment_held BOOLEAN DEFAULT FALSE,
            
            -- Completion
            completed_at DATETIME,
            rating INTEGER,
            review TEXT,
            
            -- Cancellation
            cancelled_by VARCHAR(36),
            cancellation_reason TEXT,
            cancellation_fee REAL DEFAULT 0.0,
            
            -- Timestamps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            accepted_at DATETIME,
            declined_at DATETIME,
            
            FOREIGN KEY (client_user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (artist_user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_client ON bookings (client_user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_artist ON bookings (artist_user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings (status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings (event_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_created ON bookings (created_at)")
    print("  ✅ bookings table created")
    
    # Table 2: booking_availability - Artist availability
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking_availability (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            
            -- Availability
            date DATETIME NOT NULL,
            is_available BOOLEAN DEFAULT TRUE,
            
            -- Pricing
            base_rate REAL,
            currency VARCHAR(3) DEFAULT 'USD',
            
            -- Notes
            notes TEXT,
            
            -- Timestamps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_availability_user ON booking_availability (user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_availability_date ON booking_availability (date)")
    print("  ✅ booking_availability table created")
    
    # Table 3: booking_messages - Messages between client and artist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking_messages (
            id VARCHAR(36) PRIMARY KEY,
            booking_id VARCHAR(36) NOT NULL,
            
            -- Message
            sender_user_id VARCHAR(36) NOT NULL,
            message TEXT NOT NULL,
            
            -- Attachments
            attachment_url VARCHAR(500),
            
            -- Read status
            is_read BOOLEAN DEFAULT FALSE,
            read_at DATETIME,
            
            -- Timestamps
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (booking_id) REFERENCES bookings (id) ON DELETE CASCADE,
            FOREIGN KEY (sender_user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_booking ON booking_messages (booking_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_sender ON booking_messages (sender_user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_created ON booking_messages (created_at)")
    print("  ✅ booking_messages table created")
    
    conn.commit()
    conn.close()
    
    print("✅ All booking tables created successfully!")
    print("\n📅 Tables created:")
    print("  1. bookings (32 fields)")
    print("  2. booking_availability (9 fields)")
    print("  3. booking_messages (9 fields)")

if __name__ == "__main__":
    create_booking_tables()
