"""Initial database models

Revision ID: 001_initial_models
Revises: 
Create Date: 2026-01-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create tasks table
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('recurring', sa.Boolean(), nullable=True),
        sa.Column('recurrence_pattern', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('google_task_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)
    op.create_index(op.f('ix_tasks_due_date'), 'tasks', ['due_date'], unique=False)
    op.create_index(op.f('ix_tasks_category'), 'tasks', ['category'], unique=False)
    op.create_index(op.f('ix_tasks_completed'), 'tasks', ['completed'], unique=False)

    # Create reminders table
    op.create_table('reminders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('reminder_time', sa.DateTime(), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('reminder_type', sa.String(length=50), nullable=True),
        sa.Column('sent', sa.Boolean(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reminders_user_id'), 'reminders', ['user_id'], unique=False)
    op.create_index(op.f('ix_reminders_task_id'), 'reminders', ['task_id'], unique=False)
    op.create_index(op.f('ix_reminders_reminder_time'), 'reminders', ['reminder_time'], unique=False)
    op.create_index(op.f('ix_reminders_sent'), 'reminders', ['sent'], unique=False)

    # Create thought_records table
    op.create_table('thought_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('situation', sa.Text(), nullable=False),
        sa.Column('automatic_thought', sa.Text(), nullable=False),
        sa.Column('emotions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('cognitive_distortions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('evidence_for', sa.Text(), nullable=True),
        sa.Column('evidence_against', sa.Text(), nullable=True),
        sa.Column('balanced_thought', sa.Text(), nullable=True),
        sa.Column('outcome_emotions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_thought_records_user_id'), 'thought_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_thought_records_created_at'), 'thought_records', ['created_at'], unique=False)

    # Create mood_entries table
    op.create_table('mood_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('mood_rating', sa.Integer(), nullable=False),
        sa.Column('emotions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('activities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('energy_level', sa.Integer(), nullable=True),
        sa.Column('sleep_hours', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('mood_rating >= 1 AND mood_rating <= 10', name='valid_mood_rating'),
        sa.CheckConstraint('energy_level IS NULL OR (energy_level >= 1 AND energy_level <= 10)', name='valid_energy_level'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mood_entries_user_id'), 'mood_entries', ['user_id'], unique=False)
    op.create_index(op.f('ix_mood_entries_created_at'), 'mood_entries', ['created_at'], unique=False)

    # Create cognitive_distortions reference table
    op.create_table('cognitive_distortions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('examples', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('counter_questions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )


def downgrade():
    op.drop_table('cognitive_distortions')
    op.drop_index(op.f('ix_mood_entries_created_at'), table_name='mood_entries')
    op.drop_index(op.f('ix_mood_entries_user_id'), table_name='mood_entries')
    op.drop_table('mood_entries')
    op.drop_index(op.f('ix_thought_records_created_at'), table_name='thought_records')
    op.drop_index(op.f('ix_thought_records_user_id'), table_name='thought_records')
    op.drop_table('thought_records')
    op.drop_index(op.f('ix_reminders_sent'), table_name='reminders')
    op.drop_index(op.f('ix_reminders_reminder_time'), table_name='reminders')
    op.drop_index(op.f('ix_reminders_task_id'), table_name='reminders')
    op.drop_index(op.f('ix_reminders_user_id'), table_name='reminders')
    op.drop_table('reminders')
    op.drop_index(op.f('ix_tasks_completed'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_category'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_due_date'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_user_id'), table_name='tasks')
    op.drop_table('tasks')
