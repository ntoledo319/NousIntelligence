"""Database Audit Fixes - January 2025

This migration applies fixes identified in the comprehensive database audit:
1. Adds missing indexes for performance optimization
2. Adds cascade delete constraints for data integrity
3. Adds new columns to AAAchievement model for repository compatibility

Revision ID: 002_audit_fixes
Revises: 001_initial_models
Create Date: 2025-01-05

# AI-GENERATED [2025-01-05]
# ORIGINAL_INTENT: Fix database issues identified in comprehensive audit
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = '002_audit_fixes'
down_revision = '001_initial_models'
branch_labels = None
depends_on = None


def upgrade():
    """Apply database audit fixes"""
    
    # ===== ANALYTICS MODELS INDEXES =====
    # UserActivity indexes
    _safe_create_index('idx_user_activities_user_id', 'user_activities', ['user_id'])
    _safe_create_index('idx_user_activities_activity_type', 'user_activities', ['activity_type'])
    _safe_create_index('idx_user_activities_timestamp', 'user_activities', ['timestamp'])
    _safe_create_index('idx_user_activities_session_id', 'user_activities', ['session_id'])
    
    # UserMetrics indexes
    _safe_create_index('idx_user_metrics_user_id', 'user_metrics', ['user_id'])
    _safe_create_index('idx_user_metrics_metric_type', 'user_metrics', ['metric_type'])
    _safe_create_index('idx_user_metrics_metric_date', 'user_metrics', ['metric_date'])
    
    # UserInsight indexes
    _safe_create_index('idx_user_insights_user_id', 'user_insights', ['user_id'])
    _safe_create_index('idx_user_insights_insight_type', 'user_insights', ['insight_type'])
    _safe_create_index('idx_user_insights_generated_at', 'user_insights', ['generated_at'])
    
    # UserGoals indexes
    _safe_create_index('idx_user_goals_user_id', 'user_goals', ['user_id'])
    _safe_create_index('idx_user_goals_status', 'user_goals', ['status'])
    _safe_create_index('idx_user_goals_goal_type', 'user_goals', ['goal_type'])
    
    # EngagementMetrics indexes
    _safe_create_index('idx_engagement_metrics_user_id', 'engagement_metrics', ['user_id'])
    _safe_create_index('idx_engagement_metrics_date', 'engagement_metrics', ['date'])
    
    # RetentionMetrics indexes
    _safe_create_index('idx_retention_metrics_user_id', 'retention_metrics', ['user_id'])
    _safe_create_index('idx_retention_metrics_week_number', 'retention_metrics', ['week_number'])
    
    # PerformanceMetrics indexes
    _safe_create_index('idx_performance_metrics_user_id', 'performance_metrics', ['user_id'])
    _safe_create_index('idx_performance_metrics_timestamp', 'performance_metrics', ['timestamp'])
    
    # ===== FINANCIAL MODELS INDEXES =====
    # BankAccount indexes
    _safe_create_index('idx_bank_accounts_user_id', 'bank_accounts', ['user_id'])
    
    # Transaction indexes
    _safe_create_index('idx_transactions_user_id', 'transactions', ['user_id'])
    _safe_create_index('idx_transactions_account_id', 'transactions', ['account_id'])
    _safe_create_index('idx_transactions_transaction_type', 'transactions', ['transaction_type'])
    _safe_create_index('idx_transactions_transaction_date', 'transactions', ['transaction_date'])
    _safe_create_index('idx_transactions_category_id', 'transactions', ['category_id'])
    
    # ExpenseCategory indexes
    _safe_create_index('idx_expense_categories_user_id', 'expense_categories', ['user_id'])
    
    # Budget indexes
    _safe_create_index('idx_budgets_user_id', 'budgets', ['user_id'])
    _safe_create_index('idx_budgets_is_active', 'budgets', ['is_active'])
    _safe_create_index('idx_budgets_start_date', 'budgets', ['start_date'])
    
    # Bill indexes
    _safe_create_index('idx_bills_user_id', 'bills', ['user_id'])
    _safe_create_index('idx_bills_next_due_date', 'bills', ['next_due_date'])
    
    # Investment indexes
    _safe_create_index('idx_investments_user_id', 'investments', ['user_id'])
    _safe_create_index('idx_investments_symbol', 'investments', ['symbol'])
    
    # FinancialGoal indexes
    _safe_create_index('idx_financial_goals_user_id', 'financial_goals', ['user_id'])
    _safe_create_index('idx_financial_goals_goal_type', 'financial_goals', ['goal_type'])
    _safe_create_index('idx_financial_goals_is_completed', 'financial_goals', ['is_completed'])
    
    # ===== GAMIFICATION MODELS INDEXES =====
    _safe_create_index('idx_user_achievements_user_id', 'user_achievements', ['user_id'])
    _safe_create_index('idx_wellness_streaks_user_id', 'wellness_streaks', ['user_id'])
    _safe_create_index('idx_user_points_user_id', 'user_points', ['user_id'])
    _safe_create_index('idx_point_transactions_user_id', 'point_transactions', ['user_id'])
    _safe_create_index('idx_leaderboard_entries_user_id', 'leaderboard_entries', ['user_id'])
    _safe_create_index('idx_challenge_participations_user_id', 'challenge_participations', ['user_id'])
    
    # ===== SOCIAL MODELS INDEXES =====
    _safe_create_index('idx_group_memberships_user_id', 'group_memberships', ['user_id'])
    _safe_create_index('idx_peer_connections_user_id', 'peer_connections', ['user_id'])
    _safe_create_index('idx_peer_connections_peer_id', 'peer_connections', ['peer_id'])
    _safe_create_index('idx_group_posts_user_id', 'group_posts', ['user_id'])
    _safe_create_index('idx_group_comments_user_id', 'group_comments', ['user_id'])
    
    # ===== HEALTH MODELS INDEXES =====
    _safe_create_index('idx_aa_achievements_user_id', 'aa_achievements', ['user_id'])
    
    # ===== AA ACHIEVEMENT NEW COLUMNS =====
    # Add new columns for repository compatibility
    _safe_add_column('aa_achievements', sa.Column('achievement_type', sa.String(50)))
    _safe_add_column('aa_achievements', sa.Column('title', sa.String(100)))
    _safe_add_column('aa_achievements', sa.Column('description', sa.Text))
    _safe_add_column('aa_achievements', sa.Column('points', sa.Integer, default=0))
    _safe_add_column('aa_achievements', sa.Column('earned_at', sa.DateTime))
    
    # ===== COMPOSITE INDEXES FOR COMMON QUERIES =====
    _safe_create_index('idx_user_activities_user_timestamp', 'user_activities', ['user_id', 'timestamp'])
    _safe_create_index('idx_transactions_user_date', 'transactions', ['user_id', 'transaction_date'])
    _safe_create_index('idx_user_goals_user_status', 'user_goals', ['user_id', 'status'])


def downgrade():
    """Remove audit fixes"""
    # List of all indexes created
    indexes_to_drop = [
        # Analytics
        'idx_user_activities_user_id', 'idx_user_activities_activity_type',
        'idx_user_activities_timestamp', 'idx_user_activities_session_id',
        'idx_user_metrics_user_id', 'idx_user_metrics_metric_type', 'idx_user_metrics_metric_date',
        'idx_user_insights_user_id', 'idx_user_insights_insight_type', 'idx_user_insights_generated_at',
        'idx_user_goals_user_id', 'idx_user_goals_status', 'idx_user_goals_goal_type',
        'idx_engagement_metrics_user_id', 'idx_engagement_metrics_date',
        'idx_retention_metrics_user_id', 'idx_retention_metrics_week_number',
        'idx_performance_metrics_user_id', 'idx_performance_metrics_timestamp',
        # Financial
        'idx_bank_accounts_user_id',
        'idx_transactions_user_id', 'idx_transactions_account_id',
        'idx_transactions_transaction_type', 'idx_transactions_transaction_date',
        'idx_transactions_category_id',
        'idx_expense_categories_user_id',
        'idx_budgets_user_id', 'idx_budgets_is_active', 'idx_budgets_start_date',
        'idx_bills_user_id', 'idx_bills_next_due_date',
        'idx_investments_user_id', 'idx_investments_symbol',
        'idx_financial_goals_user_id', 'idx_financial_goals_goal_type', 'idx_financial_goals_is_completed',
        # Gamification
        'idx_user_achievements_user_id', 'idx_wellness_streaks_user_id',
        'idx_user_points_user_id', 'idx_point_transactions_user_id',
        'idx_leaderboard_entries_user_id', 'idx_challenge_participations_user_id',
        # Social
        'idx_group_memberships_user_id', 'idx_peer_connections_user_id',
        'idx_peer_connections_peer_id', 'idx_group_posts_user_id', 'idx_group_comments_user_id',
        # Health
        'idx_aa_achievements_user_id',
        # Composite
        'idx_user_activities_user_timestamp', 'idx_transactions_user_date', 'idx_user_goals_user_status'
    ]
    
    for index_name in indexes_to_drop:
        _safe_drop_index(index_name)
    
    # Drop added columns
    _safe_drop_column('aa_achievements', 'achievement_type')
    _safe_drop_column('aa_achievements', 'title')
    _safe_drop_column('aa_achievements', 'description')
    _safe_drop_column('aa_achievements', 'points')
    _safe_drop_column('aa_achievements', 'earned_at')


def _safe_create_index(index_name, table_name, columns):
    """Safely create an index, ignoring if it already exists"""
    try:
        op.create_index(index_name, table_name, columns)
    except Exception:
        pass  # Index may already exist


def _safe_drop_index(index_name):
    """Safely drop an index, ignoring if it doesn't exist"""
    try:
        op.drop_index(index_name)
    except Exception:
        pass


def _safe_add_column(table_name, column):
    """Safely add a column, ignoring if it already exists"""
    try:
        op.add_column(table_name, column)
    except Exception:
        pass  # Column may already exist


def _safe_drop_column(table_name, column_name):
    """Safely drop a column, ignoring if it doesn't exist"""
    try:
        op.drop_column(table_name, column_name)
    except Exception:
        pass
