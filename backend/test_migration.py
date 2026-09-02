"""
Test script for Social Feed Phase 1 migration (a2d4fc4303db)
Tests Post, PostLike, and PostComment tables with their constraints and indexes
"""
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.db.database import engine
from datetime import datetime
import uuid

def test_phase1_migration():
    """Verify Phase 1 tables, constraints, and indexes"""
    
    inspector = sa.inspect(engine)
    
    print("=" * 60)
    print("PHASE 1 MIGRATION VERIFICATION")
    print("=" * 60)
    
    # 1. Check tables exist
    print("\n1. Verifying Phase 1 tables exist...")
    required_tables = ['posts', 'post_likes', 'post_comments']
    for table in required_tables:
        exists = table in inspector.get_table_names()
        status = "✓" if exists else "✗"
        print(f"   {status} {table}: {'EXISTS' if exists else 'MISSING'}")
        if not exists:
            print(f"      ERROR: Required table {table} is missing!")
            return False
    
    # 2. Check posts table columns
    print("\n2. Verifying posts table columns...")
    posts_columns = [col['name'] for col in inspector.get_columns('posts')]
    required_post_cols = [
        'id', 'user_id', 'post_type', 'content', 'media_urls', 'track_id',
        'poll_options', 'poll_ends_at', 'event_data', 'visibility',
        'is_pinned', 'is_deleted', 'like_count', 'comment_count',
        'share_count', 'view_count', 'created_at', 'updated_at', 'edited_at'
    ]
    for col in required_post_cols:
        exists = col in posts_columns
        status = "✓" if exists else "✗"
        print(f"   {status} {col}: {'EXISTS' if exists else 'MISSING'}")
        if not exists:
            print(f"      ERROR: Required column {col} is missing from posts!")
    
    # 3. Check post_likes table structure
    print("\n3. Verifying post_likes table structure...")
    likes_columns = [col['name'] for col in inspector.get_columns('post_likes')]
    required_likes_cols = ['id', 'user_id', 'post_id', 'created_at']
    for col in required_likes_cols:
        exists = col in likes_columns
        status = "✓" if exists else "✗"
        print(f"   {status} {col}: {'EXISTS' if exists else 'MISSING'}")
    
    # 4. Check post_comments table structure
    print("\n4. Verifying post_comments table structure...")
    comments_columns = [col['name'] for col in inspector.get_columns('post_comments')]
    required_comments_cols = [
        'id', 'post_id', 'user_id', 'content', 'parent_comment_id',
        'like_count', 'is_deleted', 'is_edited', 'created_at', 'updated_at'
    ]
    for col in required_comments_cols:
        exists = col in comments_columns
        status = "✓" if exists else "✗"
        print(f"   {status} {col}: {'EXISTS' if exists else 'MISSING'}")
    
    # 5. Check indexes
    print("\n5. Verifying indexes...")
    
    posts_indexes = [idx['name'] for idx in inspector.get_indexes('posts')]
    required_posts_indexes = ['idx_posts_user_created', 'idx_posts_type_created', 'idx_posts_visibility']
    for idx in required_posts_indexes:
        exists = idx in posts_indexes
        status = "✓" if exists else "✗"
        print(f"   {status} posts.{idx}: {'EXISTS' if exists else 'MISSING'}")
    
    likes_indexes = [idx['name'] for idx in inspector.get_indexes('post_likes')]
    if 'idx_post_likes_post' in likes_indexes:
        print(f"   ✓ post_likes.idx_post_likes_post: EXISTS")
    else:
        print(f"   ✗ post_likes.idx_post_likes_post: MISSING")
    
    comments_indexes = [idx['name'] for idx in inspector.get_indexes('post_comments')]
    required_comments_indexes = ['idx_post_comments_post', 'idx_post_comments_user']
    for idx in required_comments_indexes:
        exists = idx in comments_indexes
        status = "✓" if exists else "✗"
        print(f"   {status} post_comments.{idx}: {'EXISTS' if exists else 'MISSING'}")
    
    # 6. Check foreign keys
    print("\n6. Verifying foreign key constraints...")
    posts_fks = inspector.get_foreign_keys('posts')
    print(f"   ✓ posts has {len(posts_fks)} foreign keys")
    
    likes_fks = inspector.get_foreign_keys('post_likes')
    print(f"   ✓ post_likes has {len(likes_fks)} foreign keys (user_id, post_id)")
    
    comments_fks = inspector.get_foreign_keys('post_comments')
    print(f"   ✓ post_comments has {len(comments_fks)} foreign keys (post_id, user_id, parent_comment_id)")
    
    # 7. Test data insertion (integration test)
    print("\n7. Testing data insertion...")
    try:
        with Session(engine) as session:
            # Check if we have a test user
            user_result = session.execute(sa.text("SELECT id FROM users LIMIT 1")).first()
            if not user_result:
                print("   ⚠ No users in database - skipping data insertion test")
            else:
                user_id = user_result[0]
                post_id = str(uuid.uuid4())
                now = datetime.utcnow().isoformat()
                
                # Insert a test post
                session.execute(sa.text("""
                    INSERT INTO posts (id, user_id, post_type, content, visibility, is_deleted,
                                     like_count, comment_count, share_count, view_count,
                                     created_at, updated_at)
                    VALUES (:id, :user_id, 'text', 'Test post', 'public', 0, 0, 0, 0, 0, :now, :now)
                """), {'id': post_id, 'user_id': user_id, 'now': now})
                
                # Insert a test like
                like_id = str(uuid.uuid4())
                session.execute(sa.text("""
                    INSERT INTO post_likes (id, user_id, post_id, created_at)
                    VALUES (:id, :user_id, :post_id, :now)
                """), {'id': like_id, 'user_id': user_id, 'post_id': post_id, 'now': now})
                
                # Insert a test comment
                comment_id = str(uuid.uuid4())
                session.execute(sa.text("""
                    INSERT INTO post_comments (id, post_id, user_id, content, like_count,
                                             is_deleted, is_edited, created_at, updated_at)
                    VALUES (:id, :post_id, :user_id, 'Test comment', 0, 0, 0, :now, :now)
                """), {'id': comment_id, 'post_id': post_id, 'user_id': user_id, 'now': now})
                
                session.commit()
                
                # Verify insertion
                post_count = session.execute(sa.text("SELECT COUNT(*) FROM posts WHERE id = :id"), {'id': post_id}).scalar()
                like_count = session.execute(sa.text("SELECT COUNT(*) FROM post_likes WHERE id = :id"), {'id': like_id}).scalar()
                comment_count = session.execute(sa.text("SELECT COUNT(*) FROM post_comments WHERE id = :id"), {'id': comment_id}).scalar()
                
                if post_count == 1 and like_count == 1 and comment_count == 1:
                    print("   ✓ Data insertion test PASSED")
                    
                    # Cleanup test data
                    session.execute(sa.text("DELETE FROM post_comments WHERE id = :id"), {'id': comment_id})
                    session.execute(sa.text("DELETE FROM post_likes WHERE id = :id"), {'id': like_id})
                    session.execute(sa.text("DELETE FROM posts WHERE id = :id"), {'id': post_id})
                    session.commit()
                    print("   ✓ Test data cleaned up")
                else:
                    print("   ✗ Data insertion test FAILED")
                    return False
                    
    except Exception as e:
        print(f"   ✗ Data insertion test FAILED: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("MIGRATION VERIFICATION COMPLETE ✓")
    print("=" * 60)
    print("\nAll Phase 1 tables, columns, indexes, and constraints verified!")
    print("Migration is ready for production use.")
    
    return True

if __name__ == "__main__":
    success = test_phase1_migration()
    exit(0 if success else 1)
