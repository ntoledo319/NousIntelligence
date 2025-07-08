"""Add all missing database indexes for performance"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    """Add performance indexes"""
    
    # User-related indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Task indexes
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'])
    op.create_index('idx_tasks_user_status', 'tasks', ['user_id', 'status'])
    op.create_index('idx_tasks_user_date', 'tasks', ['user_id', 'created_at'])
    
    # Mood entry indexes
    op.create_index('idx_mood_entries_user_id', 'mood_entries', ['user_id'])
    op.create_index('idx_mood_entries_created_at', 'mood_entries', ['created_at'])
    op.create_index('idx_mood_entries_user_date', 'mood_entries', ['user_id', 'created_at'])
    
    # Thought record indexes
    op.create_index('idx_thought_records_user_id', 'thought_records', ['user_id'])
    op.create_index('idx_thought_records_created_at', 'thought_records', ['created_at'])
    
    # Family-related indexes
    op.create_index('idx_families_created_by', 'families', ['created_by'])
    op.create_index('idx_family_members_family_id', 'family_members', ['family_id'])
    op.create_index('idx_family_members_user_id', 'family_members', ['user_id'])
    
    # Shopping list indexes
    op.create_index('idx_shopping_lists_user_id', 'shopping_lists', ['user_id'])
    op.create_index('idx_shopping_items_list_id', 'shopping_items', ['shopping_list_id'])
    
    # Product tracking indexes
    op.create_index('idx_products_user_id', 'products', ['user_id'])
    op.create_index('idx_products_next_order', 'products', ['next_order_date'])
    
    # Session and auth indexes
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('idx_sessions_expires', 'sessions', ['expires_at'])
    
    # Analytics indexes
    op.create_index('idx_analytics_user_id', 'analytics_events', ['user_id'])
    op.create_index('idx_analytics_event_type', 'analytics_events', ['event_type'])
    op.create_index('idx_analytics_timestamp', 'analytics_events', ['timestamp'])
    
    # Full text search indexes (PostgreSQL)
    try:
        op.execute("""
            CREATE INDEX idx_tasks_search ON tasks 
            USING gin(to_tsvector('english', title || ' ' || coalesce(description, '')))
        """)
        
        op.execute("""
            CREATE INDEX idx_thought_records_search ON thought_records 
            USING gin(to_tsvector('english', situation || ' ' || coalesce(thoughts, '')))
        """)
    except Exception:
        # Fallback for SQLite or other databases
        pass

def downgrade():
    """Remove performance indexes"""
    indexes = [
        'idx_users_email', 'idx_users_created_at',
        'idx_tasks_user_id', 'idx_tasks_status', 'idx_tasks_due_date',
        'idx_tasks_user_status', 'idx_tasks_user_date',
        'idx_mood_entries_user_id', 'idx_mood_entries_created_at', 
        'idx_mood_entries_user_date',
        'idx_thought_records_user_id', 'idx_thought_records_created_at',
        'idx_families_created_by', 'idx_family_members_family_id',
        'idx_family_members_user_id', 'idx_shopping_lists_user_id',
        'idx_shopping_items_list_id', 'idx_products_user_id',
        'idx_products_next_order', 'idx_sessions_user_id',
        'idx_sessions_expires', 'idx_analytics_user_id',
        'idx_analytics_event_type', 'idx_analytics_timestamp',
        'idx_tasks_search', 'idx_thought_records_search'
    ]
    
    for index in indexes:
        try:
            op.drop_index(index)
        except Exception:
            pass
