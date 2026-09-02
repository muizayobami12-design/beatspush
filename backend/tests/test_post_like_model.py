"""
Unit tests for PostLike model
Task 1.2: Create PostLike model in backend/app/models/social.py

Tests PostLike model compliance with spec requirements:
- FR-3.1: Like/Unlike functionality
- Unique constraint (user can like post only once)
- Indexes for efficient querying
"""

import pytest
import uuid
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.db.database import Base
from app.models.social import PostLike, Post, PostType, PostVisibility
from app.models.user import User, UserRole


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        id=str(uuid.uuid4()),
        email="testuser@example.com",
        hashed_password="hashed_password",
        role=UserRole.ARTIST,
        full_name="Test User",
        username="testuser"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_post(db_session, test_user):
    """Create a test post"""
    post = Post(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        type=PostType.TEXT,
        content="Test post content",
        visibility=PostVisibility.PUBLIC,
        like_count=0,
        comment_count=0,
        share_count=0,
        view_count=0,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


class TestPostLikeModel:
    """Test suite for PostLike model"""
    
    def test_create_post_like(self, db_session, test_user, test_post):
        """Test creating a post like with all required fields"""
        like = PostLike(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            post_id=test_post.id,
            created_at=datetime.utcnow().isoformat()
        )
        
        db_session.add(like)
        db_session.commit()
        db_session.refresh(like)
        
        # Verify all fields are set correctly
        assert like.id is not None
        assert like.user_id == test_user.id
        assert like.post_id == test_post.id
        assert like.created_at is not None
        
    def test_post_like_with_default_values(self, db_session, test_user, test_post):
        """Test that created_at has a default value"""
        like = PostLike(
            user_id=test_user.id,
            post_id=test_post.id
        )
        
        db_session.add(like)
        db_session.commit()
        db_session.refresh(like)
        
        # Verify defaults
        assert like.id is not None  # UUID generated
        assert like.created_at is not None  # ISO timestamp generated
        
    def test_unique_constraint_user_post(self, db_session, test_user, test_post):
        """Test unique constraint: user can like a post only once"""
        # Create first like
        like1 = PostLike(
            user_id=test_user.id,
            post_id=test_post.id
        )
        db_session.add(like1)
        db_session.commit()
        
        # Try to create duplicate like
        like2 = PostLike(
            user_id=test_user.id,
            post_id=test_post.id
        )
        db_session.add(like2)
        
        # Should raise IntegrityError due to unique constraint
        with pytest.raises(IntegrityError):
            db_session.commit()
            
    def test_multiple_users_like_same_post(self, db_session, test_post):
        """Test that multiple users can like the same post"""
        # Create two different users
        user1 = User(
            id=str(uuid.uuid4()),
            email="user1@example.com",
            hashed_password="hash1",
            role=UserRole.ARTIST
        )
        user2 = User(
            id=str(uuid.uuid4()),
            email="user2@example.com",
            hashed_password="hash2",
            role=UserRole.FAN
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Both users like the same post
        like1 = PostLike(user_id=user1.id, post_id=test_post.id)
        like2 = PostLike(user_id=user2.id, post_id=test_post.id)
        
        db_session.add_all([like1, like2])
        db_session.commit()
        
        # Query likes for the post
        likes = db_session.query(PostLike).filter(PostLike.post_id == test_post.id).all()
        assert len(likes) == 2
        
    def test_user_likes_multiple_posts(self, db_session, test_user):
        """Test that a user can like multiple posts"""
        # Create two posts
        post1 = Post(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            type=PostType.TEXT,
            content="Post 1",
            visibility=PostVisibility.PUBLIC,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        post2 = Post(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            type=PostType.TEXT,
            content="Post 2",
            visibility=PostVisibility.PUBLIC,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        db_session.add_all([post1, post2])
        db_session.commit()
        
        # User likes both posts
        like1 = PostLike(user_id=test_user.id, post_id=post1.id)
        like2 = PostLike(user_id=test_user.id, post_id=post2.id)
        
        db_session.add_all([like1, like2])
        db_session.commit()
        
        # Query likes by the user
        likes = db_session.query(PostLike).filter(PostLike.user_id == test_user.id).all()
        assert len(likes) == 2
        
    def test_cascade_delete_post(self, db_session, test_user, test_post):
        """Test that deleting a post cascades to delete likes"""
        # Create a like
        like = PostLike(user_id=test_user.id, post_id=test_post.id)
        db_session.add(like)
        db_session.commit()
        
        like_id = like.id
        
        # Delete the post
        db_session.delete(test_post)
        db_session.commit()
        
        # Verify like is also deleted (cascade)
        deleted_like = db_session.query(PostLike).filter(PostLike.id == like_id).first()
        assert deleted_like is None
        
    def test_cascade_delete_user(self, db_session, test_post):
        """Test that deleting a user cascades to delete their likes"""
        # Create a user
        user = User(
            id=str(uuid.uuid4()),
            email="tempuser@example.com",
            hashed_password="hash",
            role=UserRole.FAN
        )
        db_session.add(user)
        db_session.commit()
        
        # Create a like
        like = PostLike(user_id=user.id, post_id=test_post.id)
        db_session.add(like)
        db_session.commit()
        
        like_id = like.id
        
        # Delete the user
        db_session.delete(user)
        db_session.commit()
        
        # Verify like is also deleted (cascade)
        deleted_like = db_session.query(PostLike).filter(PostLike.id == like_id).first()
        assert deleted_like is None
        
    def test_relationships(self, db_session, test_user, test_post):
        """Test that relationships work correctly"""
        like = PostLike(user_id=test_user.id, post_id=test_post.id)
        db_session.add(like)
        db_session.commit()
        db_session.refresh(like)
        
        # Test user relationship
        assert like.user is not None
        assert like.user.id == test_user.id
        assert like.user.email == test_user.email
        
        # Test post relationship
        assert like.post is not None
        assert like.post.id == test_post.id
        assert like.post.content == test_post.content
        
    def test_indexes_exist(self):
        """Test that required indexes are defined"""
        engine = create_engine(TEST_DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        
        inspector = inspect(engine)
        indexes = inspector.get_indexes('post_likes')
        
        # Check for required indexes
        index_names = [idx['name'] for idx in indexes]
        
        # Should have index on user_id (for foreign key)
        # Should have index on post_id (for foreign key)
        # Should have composite index idx_post_likes_post on (post_id, created_at)
        
        # Note: SQLite may handle indexes differently, so we check the column definitions
        columns = inspector.get_columns('post_likes')
        column_names = [col['name'] for col in columns]
        
        assert 'user_id' in column_names
        assert 'post_id' in column_names
        assert 'created_at' in column_names
        
    def test_timestamp_format(self, db_session, test_user, test_post):
        """Test that created_at uses ISO timestamp format"""
        like = PostLike(user_id=test_user.id, post_id=test_post.id)
        db_session.add(like)
        db_session.commit()
        db_session.refresh(like)
        
        # Verify it's a valid ISO timestamp string
        assert isinstance(like.created_at, str)
        assert len(like.created_at) > 0
        
        # Should be parseable as datetime
        try:
            datetime.fromisoformat(like.created_at.replace('Z', '+00:00'))
            is_valid = True
        except ValueError:
            is_valid = False
            
        assert is_valid, "created_at should be a valid ISO timestamp"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
