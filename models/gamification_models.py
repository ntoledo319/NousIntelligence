"""
Gamification Models

This module defines database models for gamification features including
achievements, badges, streaks, points, and leaderboards.

@module models.gamification_models
@context_boundary Gamification System
"""

from database import db
from datetime import datetime, timedelta
from sqlalchemy import func, and_


class Achievement(db.Model):
    """Model for achievement definitions"""
    
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # wellness, social, learning, consistency
    icon = db.Column(db.String(50))  # Icon identifier
    points = db.Column(db.Integer, default=10)
    rarity = db.Column(db.String(20), default='common')  # common, rare, epic, legendary
    
    # Criteria for earning
    criteria_type = db.Column(db.String(50))  # streak, count, milestone, special
    criteria_value = db.Column(db.Integer)  # e.g., 7 for 7-day streak
    criteria_metric = db.Column(db.String(50))  # e.g., 'mood_logs', 'dbt_skills'
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # VOCAB: Achievement - A milestone or accomplishment in the wellness journey
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'icon': self.icon,
            'points': self.points,
            'rarity': self.rarity,
            'criteria_type': self.criteria_type,
            'criteria_value': self.criteria_value,
            'criteria_metric': self.criteria_metric
        }


class UserAchievement(db.Model):
    """Model for user's earned achievements"""
    
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Float, default=100.0)  # Percentage for partial progress
    
    # Relationships
    user = db.relationship('User', backref='achievements')
    achievement = db.relationship('Achievement', backref='earned_by')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id', name='_user_achievement_uc'),)


class WellnessStreak(db.Model):
    """Model for tracking various wellness streaks"""
    
    __tablename__ = 'wellness_streaks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    streak_type = db.Column(db.String(50), nullable=False)  # meditation, mood_log, exercise, etc.
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # VOCAB: Wellness Streak - Consecutive days of healthy activities
    # Relationships
    user = db.relationship('User', backref='streaks')
    
    def check_and_update(self, activity_date=None):
        """Check and update streak based on activity date"""
        if activity_date is None:
            activity_date = datetime.utcnow().date()
        
        if self.last_activity_date is None:
            # First activity
            self.current_streak = 1
            self.longest_streak = 1
        elif activity_date == self.last_activity_date:
            # Same day, no change
            pass
        elif activity_date == self.last_activity_date + timedelta(days=1):
            # Consecutive day
            self.current_streak += 1
            self.longest_streak = max(self.longest_streak, self.current_streak)
        else:
            # Streak broken
            self.current_streak = 1
        
        self.last_activity_date = activity_date
        return self.current_streak


class UserPoints(db.Model):
    """Model for user points and levels"""
    
    __tablename__ = 'user_points'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False, unique=True)
    total_points = db.Column(db.Integer, default=0)
    current_level = db.Column(db.Integer, default=1)
    points_to_next_level = db.Column(db.Integer, default=100)
    
    # Point breakdown by category
    wellness_points = db.Column(db.Integer, default=0)
    social_points = db.Column(db.Integer, default=0)
    learning_points = db.Column(db.Integer, default=0)
    consistency_points = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('points', uselist=False))
    
    def add_points(self, points, category='general'):
        """Add points and check for level up"""
        self.total_points += points
        
        # Update category points
        if category == 'wellness':
            self.wellness_points += points
        elif category == 'social':
            self.social_points += points
        elif category == 'learning':
            self.learning_points += points
        elif category == 'consistency':
            self.consistency_points += points
        
        # Check for level up
        while self.total_points >= self.points_to_next_level:
            self.current_level += 1
            self.points_to_next_level = self.current_level * 100  # Simple progression
            
        return self.current_level


class PointTransaction(db.Model):
    """Model for tracking point transactions"""
    
    __tablename__ = 'point_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(50))  # earned, spent, bonus
    reason = db.Column(db.String(200))
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='point_transactions')


class Leaderboard(db.Model):
    """Model for leaderboard entries"""
    
    __tablename__ = 'leaderboard_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    leaderboard_type = db.Column(db.String(50), nullable=False)  # weekly, monthly, all-time
    category = db.Column(db.String(50), nullable=False)  # overall, wellness, social, etc.
    score = db.Column(db.Integer, nullable=False)
    rank = db.Column(db.Integer)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='leaderboard_entries')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'leaderboard_type', 'category', 'period_start', 
                          name='_user_leaderboard_uc'),
    )


class Challenge(db.Model):
    """Model for wellness challenges"""
    
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    challenge_type = db.Column(db.String(50))  # daily, weekly, monthly
    category = db.Column(db.String(50))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    points_reward = db.Column(db.Integer, default=50)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # VOCAB: Challenge - Time-limited wellness goal
    # Relationships
    participants = db.relationship('ChallengeParticipation', back_populates='challenge')


class ChallengeParticipation(db.Model):
    """Model for user participation in challenges"""
    
    __tablename__ = 'challenge_participations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    progress = db.Column(db.Float, default=0.0)  # Percentage
    
    # Relationships
    user = db.relationship('User', backref='challenge_participations')
    challenge = db.relationship('Challenge', back_populates='participants')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'challenge_id', name='_user_challenge_uc'),)


# AI-GENERATED [2024-12-01]
# ORIGINAL_INTENT: Encourage positive engagement through game mechanics 