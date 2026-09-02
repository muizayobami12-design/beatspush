"""Verify indexes were created by the migration"""
from app.db.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)

print("Beat plays indexes:")
for idx in inspector.get_indexes('beat_plays'):
    if any(keyword in idx['name'] for keyword in ['beat', 'user', 'created', 'completed']):
        print(f"  - {idx['name']}: {idx['column_names']}")

print("\nBeat favorites indexes:")
for idx in inspector.get_indexes('beat_favorites'):
    if any(keyword in idx['name'] for keyword in ['beat', 'user', 'created']):
        print(f"  - {idx['name']}: {idx['column_names']}")

print("\nBeat purchases indexes:")
for idx in inspector.get_indexes('beat_purchases'):
    if any(keyword in idx['name'] for keyword in ['beat', 'buyer', 'created', 'status']):
        print(f"  - {idx['name']}: {idx['column_names']}")

print("\nRecommendation engine tables:")
for table in ['user_preference_profiles', 'beat_similarity_cache', 'trending_beat_cache', 'recommendation_logs']:
    if table in inspector.get_table_names():
        print(f"\n{table} indexes:")
        for idx in inspector.get_indexes(table):
            print(f"  - {idx['name']}: {idx['column_names']}")
