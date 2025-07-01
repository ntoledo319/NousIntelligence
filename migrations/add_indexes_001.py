"""Add database indexes for performance

Revision ID: add_indexes_001
Create Date: 2024-01-01

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add indexes to users table
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    op.create_index('idx_users_google_id', 'users', ['google_id'])
    
    # Add indexes to other tables
    op.create_index('idx_activities_user_id', 'activity', ['user_id'])
    op.create_index('idx_activities_created_at', 'activity', ['created_at'])

def downgrade():
    op.drop_index('idx_users_email')
    op.drop_index('idx_users_username')
    op.drop_index('idx_users_created_at')
    op.drop_index('idx_users_google_id')
    op.drop_index('idx_activities_user_id')
    op.drop_index('idx_activities_created_at')
