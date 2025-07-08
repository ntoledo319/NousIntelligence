"""
Migration: Add User Features Tables

This migration adds database tables for new user features:
- Social features (support groups, peer connections, anonymous sharing)
- Gamification features (achievements, points, streaks, leaderboards)
- Personal growth features (goals, habits, journaling, vision boards)

@module migrations.add_user_features_tables
@ai_prompt Run this migration to create tables for new user features
"""

import logging
from database import db
from models import (
    # Social models
    SupportGroup, GroupMembership, PeerConnection, AnonymousShare,
    AnonymousResponse, GroupPost, GroupComment,
    # Gamification models
    Achievement, UserAchievement, WellnessStreak, UserPoints,
    PointTransaction, Leaderboard, Challenge, ChallengeParticipation,
    # Personal growth models
    PersonalGoal, GoalMilestone, Habit, HabitEntry,
    JournalEntry, JournalAttachment, VisionBoard, VisionBoardItem,
    ReflectionPrompt,
    # Mental health resource models
    CrisisResource, TherapyProvider, PsychiatryProvider,
    CommunityResource, UserSavedResource
)

logger = logging.getLogger(__name__)


def run_migration():
    """
    Create tables for new user features
    
    To modify features:
    1) Update the model definitions in models/
    2) Add any new models to the imports above
    3) Run this migration again
    """
    try:
        logger.info("Starting user features migration...")
        
        # Create all tables
        db.create_all()
        
        logger.info("✅ Tables created successfully")
        
        # Add default achievements
        default_achievements = [
            # Wellness achievements
            {'name': 'First Steps', 'description': 'Complete your first mood log', 
             'category': 'wellness', 'points': 10, 'rarity': 'common',
             'criteria_type': 'count', 'criteria_value': 1, 'criteria_metric': 'mood_log'},
            {'name': 'Week of Wellness', 'description': 'Log your mood for 7 consecutive days',
             'category': 'wellness', 'points': 50, 'rarity': 'rare',
             'criteria_type': 'streak', 'criteria_value': 7, 'criteria_metric': 'mood_log'},
            {'name': 'Mindfulness Master', 'description': 'Complete 30 meditation sessions',
             'category': 'wellness', 'points': 100, 'rarity': 'epic',
             'criteria_type': 'count', 'criteria_value': 30, 'criteria_metric': 'meditation'},
            
            # Social achievements
            {'name': 'Community Builder', 'description': 'Join your first support group',
             'category': 'social', 'points': 20, 'rarity': 'common',
             'criteria_type': 'count', 'criteria_value': 1, 'criteria_metric': 'group_joined'},
            {'name': 'Helping Hand', 'description': 'Support 10 anonymous shares',
             'category': 'social', 'points': 30, 'rarity': 'rare',
             'criteria_type': 'count', 'criteria_value': 10, 'criteria_metric': 'support_given'},
            
            # Learning achievements
            {'name': 'Goal Setter', 'description': 'Create your first goal',
             'category': 'learning', 'points': 15, 'rarity': 'common',
             'criteria_type': 'count', 'criteria_value': 1, 'criteria_metric': 'goal_created'},
            {'name': 'Goal Achiever', 'description': 'Complete 5 goals',
             'category': 'learning', 'points': 75, 'rarity': 'rare',
             'criteria_type': 'count', 'criteria_value': 5, 'criteria_metric': 'goal_completed'},
            
            # Consistency achievements
            {'name': 'Habit Former', 'description': 'Track a habit for 21 days',
             'category': 'consistency', 'points': 60, 'rarity': 'rare',
             'criteria_type': 'streak', 'criteria_value': 21, 'criteria_metric': 'habit_tracking'},
            {'name': 'Century Club', 'description': 'Maintain any streak for 100 days',
             'category': 'consistency', 'points': 200, 'rarity': 'legendary',
             'criteria_type': 'streak', 'criteria_value': 100, 'criteria_metric': 'any_streak'},
        ]
        
        # Add default achievements if none exist
        existing_count = Achievement.query.count()
        if existing_count == 0:
            for achievement_data in default_achievements:
                achievement = Achievement(**achievement_data)
                db.session.add(achievement)
            logger.info(f"✅ Added {len(default_achievements)} default achievements")
        
        # Add default reflection prompts
        default_prompts = [
            # Gratitude prompts
            {'prompt_text': 'What are three things you are grateful for today?',
             'category': 'gratitude', 'difficulty_level': 'beginner'},
            {'prompt_text': 'Describe a person who made a positive impact on your life recently.',
             'category': 'gratitude', 'difficulty_level': 'intermediate'},
            
            # Growth prompts
            {'prompt_text': 'What is one thing you learned about yourself this week?',
             'category': 'growth', 'difficulty_level': 'beginner'},
            {'prompt_text': 'How have you grown as a person in the last year?',
             'category': 'growth', 'difficulty_level': 'advanced'},
            
            # Relationships prompts
            {'prompt_text': 'How did you show kindness to someone today?',
             'category': 'relationships', 'difficulty_level': 'beginner'},
            {'prompt_text': 'What relationship in your life needs more attention and why?',
             'category': 'relationships', 'difficulty_level': 'intermediate'},
            
            # Goals prompts
            {'prompt_text': 'What is one small step you can take tomorrow toward your biggest goal?',
             'category': 'goals', 'difficulty_level': 'beginner'},
            {'prompt_text': 'If you achieved all your goals, how would your life be different?',
             'category': 'goals', 'difficulty_level': 'advanced'},
        ]
        
        # Add default prompts if none exist
        prompt_count = ReflectionPrompt.query.count()
        if prompt_count == 0:
            for prompt_data in default_prompts:
                prompt = ReflectionPrompt(**prompt_data)
                db.session.add(prompt)
            logger.info(f"✅ Added {len(default_prompts)} default reflection prompts")
        
        # Commit all changes
        db.session.commit()
        logger.info("✅ User features migration completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        db.session.rollback()
        return False


def rollback_migration():
    """
    Rollback the migration by dropping the created tables
    
    ⚠️ WARNING: This will delete all data in these tables!
    """
    try:
        logger.info("Rolling back user features migration...")
        
        # Drop tables in reverse order to handle foreign keys
        tables_to_drop = [
            # Mental health resource tables
            'user_saved_resources', 'community_resources',
            'psychiatry_providers', 'therapy_providers', 'crisis_resources',
            
            # Personal growth tables
            'vision_board_items', 'vision_boards',
            'journal_attachments', 'journal_entries',
            'habit_entries', 'habits',
            'goal_milestones', 'goals',
            'reflection_prompts',
            
            # Gamification tables
            'challenge_participations', 'challenges',
            'leaderboard_entries', 'point_transactions',
            'user_points', 'wellness_streaks',
            'user_achievements', 'achievements',
            
            # Social tables
            'group_comments', 'group_posts',
            'anonymous_responses', 'anonymous_shares',
            'peer_connections', 'group_memberships',
            'support_groups'
        ]
        
        for table_name in tables_to_drop:
            try:
                db.session.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE')
                logger.info(f"  Dropped table: {table_name}")
            except Exception as e:
                logger.warning(f"  Could not drop table {table_name}: {e}")
        
        db.session.commit()
        logger.info("✅ Rollback completed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}")
        db.session.rollback()
        return False


if __name__ == '__main__':
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        # Run the migration
        success = run_migration()
        
        if success:
            print("\n✅ Migration completed successfully!")
            print("\nNew features available:")
            print("  - Social: Support groups, peer connections, anonymous sharing")
            print("  - Gamification: Achievements, points, streaks, leaderboards") 
            print("  - Personal Growth: Goals, habits, journaling, vision boards")
            print("  - Mental Health Resources: Crisis support, therapy/psychiatry search")
        else:
            print("\n❌ Migration failed. Check logs for details.")


# AI-GENERATED [2024-12-01]
# TRAINING_DATA: Database migration best practices
# NON-NEGOTIABLES: Always backup database before running migrations 