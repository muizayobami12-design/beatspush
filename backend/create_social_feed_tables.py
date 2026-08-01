"""
Create Social Feed Tables
Task 7.1: Social Feed

Creates tables for social feed functionality
"""

import sqlite3
import uuid
from datetime import datetime

# Connect to database
conn = sqlite3.connect('beatpush.db')
cursor = conn.cursor()

print("📊 Creating social feed tables...")

# 1. Posts table
cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    post_type TEXT NOT NULL,  -- status, track_share, event, milestone, poll
    content TEXT,
    media_url TEXT,  -- Image/video URL
    track_id TEXT,  -- If sharing a track
    event_date TEXT,  -- For event announcements
    poll_options TEXT,  -- JSON array for polls
    poll_ends_at TEXT,  -- Poll expiration
    
    -- Engagement counts
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    
    -- Visibility
    visibility TEXT DEFAULT 'public',  -- public, followers, private
    is_pinned BOOLEAN DEFAULT 0,
    
    -- Metadata
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (track_id) REFERENCES tracks(id)
)
""")

# 2. Post likes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS post_likes (
    id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(post_id, user_id)
)
""")

# 3. Post comments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS post_comments (
    id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    parent_comment_id TEXT,  -- For nested replies
    content TEXT NOT NULL,
    
    -- Engagement
    like_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    is_edited BOOLEAN DEFAULT 0,
    
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (parent_comment_id) REFERENCES post_comments(id) ON DELETE CASCADE
)
""")

# 4. Comment likes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS comment_likes (
    id TEXT PRIMARY KEY,
    comment_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    
    FOREIGN KEY (comment_id) REFERENCES post_comments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(comment_id, user_id)
)
""")

# 5. Post shares table
cursor.execute("""
CREATE TABLE IF NOT EXISTS post_shares (
    id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    share_type TEXT NOT NULL,  -- repost, quote, external
    quote_text TEXT,  -- For quote reposts
    created_at TEXT NOT NULL,
    
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# 6. Follows table
cursor.execute("""
CREATE TABLE IF NOT EXISTS follows (
    id TEXT PRIMARY KEY,
    follower_id TEXT NOT NULL,  -- User who follows
    following_id TEXT NOT NULL,  -- User being followed
    created_at TEXT NOT NULL,
    
    FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(follower_id, following_id)
)
""")

# 7. Post bookmarks table
cursor.execute("""
CREATE TABLE IF NOT EXISTS post_bookmarks (
    id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(post_id, user_id)
)
""")

# 8. Poll votes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS poll_votes (
    id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    option_index INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(post_id, user_id)
)
""")

# Create indices for performance
print("📊 Creating indices...")

cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_post_type ON posts(post_type)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_likes_post_id ON post_likes(post_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_likes_user_id ON post_likes(user_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_comments_post_id ON post_comments(post_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_comments_user_id ON post_comments(user_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_follows_follower_id ON follows(follower_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_follows_following_id ON follows(following_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_shares_post_id ON post_shares(post_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_bookmarks_user_id ON post_bookmarks(user_id)")

# Commit changes
conn.commit()

print("\n✅ Social feed tables created successfully!")

# Show table stats
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'post%' OR name='follows'")
tables = cursor.fetchall()

print(f"\n📊 Created {len(tables)} tables:")
for table in tables:
    print(f"  ✅ {table[0]}")

conn.close()

print("\n🎉 Database setup complete!")
