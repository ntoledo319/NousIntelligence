"""
API Key Rotation System Migration

Creates tables for API key management and rotation functionality.

Revision ID: api_key_rotation
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = 'api_key_rotation'
down_revision = '2fa_implementation'  # Link to the previous migration
branch_labels = None
depends_on = None

def upgrade():
    # Create API keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('key_prefix', sa.String(8), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False),
        sa.Column('scopes', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('use_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_rotated_at', sa.DateTime(), nullable=True),
        sa.Column('rotation_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rotated_from_id', sa.Integer(), nullable=True),
        sa.Column('rotated_to_id', sa.Integer(), nullable=True),
        sa.Column('hourly_usage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('daily_usage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('hourly_reset_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('daily_reset_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rotated_from_id'], ['api_keys.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['rotated_to_id'], ['api_keys.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_prefix', name='uq_api_key_prefix')
    )
    
    # Create API key events table for audit trail
    op.create_table(
        'api_key_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('api_key_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(20), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('performed_by_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['api_key_id'], ['api_keys.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['performed_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for faster lookups
    op.create_index('idx_api_key_user', 'api_keys', ['user_id'])
    op.create_index('idx_api_key_status', 'api_keys', ['status'])
    op.create_index('idx_api_key_expires', 'api_keys', ['expires_at'])
    op.create_index('idx_api_key_event_key', 'api_key_events', ['api_key_id'])
    op.create_index('idx_api_key_event_type', 'api_key_events', ['event_type'])
    op.create_index('idx_api_key_event_time', 'api_key_events', ['timestamp'])

def downgrade():
    # Drop tables and indexes
    op.drop_table('api_key_events')
    op.drop_table('api_keys') 