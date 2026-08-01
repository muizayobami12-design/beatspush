"""
Verification Test for BlockedUser Model (Task 2.4)

This test verifies that the BlockedUser model exists and is correctly implemented
according to the design specifications.

Verification Points:
1. Model exists in backend/app/models/messaging.py
2. All required fields are present (id, blocker_id, blocked_id, blocked_at, reason)
3. Unique constraint on (blocker_id, blocked_id)
4. Relationships are properly defined (blocker, blocked)
5. Indexes are created for performance
6. Model is imported in database.py and models/__init__.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_blocked_user_model_exists():
    """Verify BlockedUser model exists and can be imported."""
    try:
        from app.models.messaging import BlockedUser
        print("✅ BlockedUser model exists and can be imported")
        return True, BlockedUser
    except ImportError as e:
        print(f"❌ Failed to import BlockedUser model: {e}")
        return False, None


def test_blocked_user_fields(BlockedUser):
    """Verify BlockedUser has all required fields."""
    required_fields = {
        'id': 'primary key',
        'blocker_id': 'foreign key to users',
        'blocked_id': 'foreign key to users',
        'blocked_at': 'timestamp',
        'reason': 'optional text field'
    }
    
    all_passed = True
    
    # Check table name
    if hasattr(BlockedUser, '__tablename__'):
        if BlockedUser.__tablename__ == 'blocked_users':
            print("✅ Table name is correct: blocked_users")
        else:
            print(f"❌ Table name is incorrect: {BlockedUser.__tablename__}")
            all_passed = False
    else:
        print("❌ __tablename__ not defined")
        all_passed = False
    
    # Check each required field
    for field_name, description in required_fields.items():
        if hasattr(BlockedUser, field_name):
            print(f"✅ Field '{field_name}' exists ({description})")
        else:
            print(f"❌ Field '{field_name}' is missing ({description})")
            all_passed = False
    
    return all_passed


def test_blocked_user_relationships(BlockedUser):
    """Verify BlockedUser relationships are properly defined."""
    all_passed = True
    
    # Check blocker relationship
    if hasattr(BlockedUser, 'blocker'):
        print("✅ Relationship 'blocker' exists")
    else:
        print("❌ Relationship 'blocker' is missing")
        all_passed = False
    
    # Check blocked relationship
    if hasattr(BlockedUser, 'blocked'):
        print("✅ Relationship 'blocked' exists")
    else:
        print("❌ Relationship 'blocked' is missing")
        all_passed = False
    
    return all_passed


def test_blocked_user_constraints(BlockedUser):
    """Verify unique constraint on (blocker_id, blocked_id)."""
    all_passed = True
    
    if hasattr(BlockedUser, '__table_args__'):
        table_args = BlockedUser.__table_args__
        
        # Check for unique constraint
        has_unique_constraint = False
        has_indexes = False
        
        for arg in table_args:
            if hasattr(arg, 'name') and 'blocker_blocked' in arg.name:
                has_unique_constraint = True
                print(f"✅ Unique constraint found: {arg.name}")
            elif hasattr(arg, 'name') and 'blocks' in arg.name:
                has_indexes = True
                print(f"✅ Index found: {arg.name}")
        
        if not has_unique_constraint:
            print("❌ Unique constraint on (blocker_id, blocked_id) not found")
            all_passed = False
        
        if not has_indexes:
            print("⚠️  Performance indexes may be missing")
    else:
        print("❌ __table_args__ not defined")
        all_passed = False
    
    return all_passed


def test_blocked_user_in_database_init():
    """Verify BlockedUser is imported in database.py init_db function."""
    try:
        with open('backend/app/db/database.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'BlockedUser' in content:
            print("✅ BlockedUser is imported in database.py")
            return True
        else:
            print("❌ BlockedUser is NOT imported in database.py")
            return False
    except Exception as e:
        print(f"❌ Error reading database.py: {e}")
        return False


def test_blocked_user_in_models_init():
    """Verify BlockedUser is exported from models/__init__.py."""
    try:
        from app.models import BlockedUser
        print("✅ BlockedUser is exported from models/__init__.py")
        return True
    except ImportError as e:
        print(f"❌ BlockedUser is NOT exported from models/__init__.py: {e}")
        return False


def test_blocked_user_column_types(BlockedUser):
    """Verify column types are correct."""
    from sqlalchemy import String, Text, DateTime, ForeignKey
    
    all_passed = True
    
    # Check column types
    columns = BlockedUser.__table__.columns
    
    # Check id column
    if 'id' in columns:
        id_col = columns['id']
        if isinstance(id_col.type, String):
            print("✅ id column is String type")
        else:
            print(f"❌ id column type is incorrect: {type(id_col.type)}")
            all_passed = False
    
    # Check blocker_id column
    if 'blocker_id' in columns:
        blocker_col = columns['blocker_id']
        if isinstance(blocker_col.type, String):
            print("✅ blocker_id column is String type")
        else:
            print(f"❌ blocker_id column type is incorrect: {type(blocker_col.type)}")
            all_passed = False
        
        # Check foreign key constraint
        if blocker_col.foreign_keys:
            print("✅ blocker_id has foreign key constraint")
        else:
            print("❌ blocker_id is missing foreign key constraint")
            all_passed = False
    
    # Check blocked_id column
    if 'blocked_id' in columns:
        blocked_col = columns['blocked_id']
        if isinstance(blocked_col.type, String):
            print("✅ blocked_id column is String type")
        else:
            print(f"❌ blocked_id column type is incorrect: {type(blocked_col.type)}")
            all_passed = False
        
        # Check foreign key constraint
        if blocked_col.foreign_keys:
            print("✅ blocked_id has foreign key constraint")
        else:
            print("❌ blocked_id is missing foreign key constraint")
            all_passed = False
    
    # Check blocked_at column
    if 'blocked_at' in columns:
        blocked_at_col = columns['blocked_at']
        if isinstance(blocked_at_col.type, DateTime):
            print("✅ blocked_at column is DateTime type")
        else:
            print(f"❌ blocked_at column type is incorrect: {type(blocked_at_col.type)}")
            all_passed = False
    
    # Check reason column
    if 'reason' in columns:
        reason_col = columns['reason']
        if isinstance(reason_col.type, Text):
            print("✅ reason column is Text type")
        else:
            print(f"❌ reason column type is incorrect: {type(reason_col.type)}")
            all_passed = False
    
    return all_passed


def main():
    """Run all verification tests."""
    print("=" * 70)
    print("BLOCKED USER MODEL VERIFICATION TEST (Task 2.4)")
    print("=" * 70)
    print()
    
    all_tests_passed = True
    
    # Test 1: Model exists
    print("Test 1: Model Import")
    print("-" * 70)
    exists, BlockedUser = test_blocked_user_model_exists()
    all_tests_passed &= exists
    print()
    
    if not exists:
        print("❌ Cannot continue tests - model does not exist")
        return False
    
    # Test 2: Required fields
    print("Test 2: Required Fields")
    print("-" * 70)
    all_tests_passed &= test_blocked_user_fields(BlockedUser)
    print()
    
    # Test 3: Relationships
    print("Test 3: Relationships")
    print("-" * 70)
    all_tests_passed &= test_blocked_user_relationships(BlockedUser)
    print()
    
    # Test 4: Constraints
    print("Test 4: Constraints and Indexes")
    print("-" * 70)
    all_tests_passed &= test_blocked_user_constraints(BlockedUser)
    print()
    
    # Test 5: Column types
    print("Test 5: Column Types")
    print("-" * 70)
    all_tests_passed &= test_blocked_user_column_types(BlockedUser)
    print()
    
    # Test 6: Database import
    print("Test 6: Database Integration")
    print("-" * 70)
    all_tests_passed &= test_blocked_user_in_database_init()
    print()
    
    # Test 7: Models export
    print("Test 7: Models Export")
    print("-" * 70)
    all_tests_passed &= test_blocked_user_in_models_init()
    print()
    
    # Summary
    print("=" * 70)
    if all_tests_passed:
        print("✅ ALL VERIFICATION TESTS PASSED!")
        print("✅ BlockedUser model is correctly implemented")
    else:
        print("❌ SOME TESTS FAILED")
        print("❌ Please review the failed tests above")
    print("=" * 70)
    
    return all_tests_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
