"""
Two-Factor Authentication Implementation Migration

Creates the two_factor_backup_codes table and adds two-factor 
authentication fields to the users table.

Revision ID: 2fa_implementation
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = '2fa_implementation'
down_revision = None  # Set this to the previous migration ID in your project
branch_labels = None
depends_on = None

def upgrade():
    # Add 2FA fields to users table
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('two_factor_secret', sa.String(32), nullable=True))
    
    # Create backup codes table
    op.create_table(
        'two_factor_backup_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code_hash', sa.String(255), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_backup_codes_user_id', 'two_factor_backup_codes', ['user_id'])
    op.create_index('idx_backup_codes_used', 'two_factor_backup_codes', ['used'])

def downgrade():
    # Drop backup codes table
    op.drop_table('two_factor_backup_codes')
    
    # Remove 2FA fields from users table
    op.drop_column('users', 'two_factor_secret')
    op.drop_column('users', 'two_factor_enabled') 