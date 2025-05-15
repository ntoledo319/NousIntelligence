"""
Alcoholics Anonymous Recovery Models
Provides database models for tracking recovery progress, meetings, reflections,
inventory entries, and other AA program features.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app import db

class AASettings(db.Model):
    """User settings for AA recovery features"""
    __tablename__ = 'aa_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    sponsor_name = Column(String(255))
    sponsor_phone = Column(String(20))
    backup_contact_name = Column(String(255))
    backup_contact_phone = Column(String(20))
    home_group = Column(String(255))
    sober_date = Column(DateTime)
    show_sober_days = Column(Boolean, default=True)
    track_honesty_streaks = Column(Boolean, default=True)
    daily_reflection_time = Column(String(5), default="07:00") # 24-hour format (HH:MM)
    nightly_inventory_time = Column(String(5), default="21:00") # 24-hour format (HH:MM)
    spot_checks_per_day = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sponsor_name': self.sponsor_name,
            'sponsor_phone': self.sponsor_phone,
            'backup_contact_name': self.backup_contact_name,
            'backup_contact_phone': self.backup_contact_phone,
            'home_group': self.home_group,
            'sober_date': self.sober_date.isoformat() if self.sober_date else None,
            'show_sober_days': self.show_sober_days,
            'track_honesty_streaks': self.track_honesty_streaks,
            'daily_reflection_time': self.daily_reflection_time,
            'nightly_inventory_time': self.nightly_inventory_time,
            'spot_checks_per_day': self.spot_checks_per_day,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AARecoveryLog(db.Model):
    """Log of recovery activities and entries"""
    __tablename__ = 'aa_recovery_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    log_type = Column(String(50), nullable=False, index=True)  # reflection, inventory, spot_check, etc.
    content = Column(Text)
    category = Column(String(50))  # resentment, fear, selfish, etc. for categorized entries
    is_honest_admit = Column(Boolean, default=False)  # For tracking honesty streaks
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'log_type': self.log_type,
            'content': self.content,
            'category': self.category,
            'is_honest_admit': self.is_honest_admit,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AAMeetingLog(db.Model):
    """Log of AA meetings attended"""
    __tablename__ = 'aa_meeting_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    meeting_name = Column(String(255))
    meeting_type = Column(String(50))  # in_person, online, phone
    meeting_id = Column(String(255))  # ID from Meeting Guide API, if available
    date_attended = Column(DateTime, nullable=False)
    pre_meeting_reflection = Column(Text)  # "What snagged you since your last meeting?"
    post_meeting_reflection = Column(Text)  # Post-meeting reflection
    post_meeting_honest_admit = Column(Text)  # "Did you catch a misstep?"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meeting_name': self.meeting_name,
            'meeting_type': self.meeting_type,
            'meeting_id': self.meeting_id,
            'date_attended': self.date_attended.isoformat() if self.date_attended else None,
            'pre_meeting_reflection': self.pre_meeting_reflection,
            'post_meeting_reflection': self.post_meeting_reflection,
            'post_meeting_honest_admit': self.post_meeting_honest_admit,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AANightlyInventory(db.Model):
    """Nightly 10th Step inventory entries"""
    __tablename__ = 'aa_nightly_inventories'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    resentful = Column(Text)
    selfish = Column(Text)
    dishonest = Column(Text)
    afraid = Column(Text)
    secrets = Column(Text)
    apologies_needed = Column(Text)
    gratitude = Column(Text)
    surrender = Column(Text)
    wrong_actions = Column(Text)  # "What did I do wrong?"
    amends_owed = Column(Text)  # "Who do I owe an apology to?"
    help_plan = Column(Text)  # "How will I help someone tomorrow?"
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'resentful': self.resentful,
            'selfish': self.selfish,
            'dishonest': self.dishonest,
            'afraid': self.afraid,
            'secrets': self.secrets,
            'apologies_needed': self.apologies_needed,
            'gratitude': self.gratitude,
            'surrender': self.surrender,
            'wrong_actions': self.wrong_actions,
            'amends_owed': self.amends_owed,
            'help_plan': self.help_plan,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AASpotCheck(db.Model):
    """Spot-check inventory responses"""
    __tablename__ = 'aa_spot_checks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    check_type = Column(String(50), nullable=False)  # resentment, selfish, dishonest, fear, anger, etc.
    question = Column(String(255))
    response = Column(Text)
    rating = Column(Integer, nullable=True)  # For questions with ratings (0-5)
    trigger = Column(String(255), nullable=True)  # What triggered the feeling/behavior
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'check_type': self.check_type,
            'question': self.question,
            'response': self.response,
            'rating': self.rating,
            'trigger': self.trigger,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AASponsorCall(db.Model):
    """Log of calls to sponsor or backup contact"""
    __tablename__ = 'aa_sponsor_calls'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    contact_type = Column(String(50))  # sponsor, backup_contact
    pre_call_admission = Column(Text)  # "Own your latest slip or win"
    post_call_admission = Column(Text)  # "What did you admit to them?"
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contact_type': self.contact_type,
            'pre_call_admission': self.pre_call_admission,
            'post_call_admission': self.post_call_admission,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AAMindfulnessLog(db.Model):
    """Log of mindfulness and CBT exercises used"""
    __tablename__ = 'aa_mindfulness_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    exercise_type = Column(String(50))  # breathing, thought_record, urge_surfing, TIPP, etc.
    exercise_name = Column(String(255))
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exercise_type': self.exercise_type,
            'exercise_name': self.exercise_name,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AAAchievement(db.Model):
    """Achievements and badges earned by users"""
    __tablename__ = 'aa_achievements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    badge_id = Column(String(50), nullable=False)  # Unique identifier for the badge type
    badge_name = Column(String(255), nullable=False)
    badge_description = Column(Text)
    earned_date = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'badge_name': self.badge_name,
            'badge_description': self.badge_description,
            'earned_date': self.earned_date.isoformat() if self.earned_date else None
        }

class AAForumPost(db.Model):
    """Forum posts for peer support"""
    __tablename__ = 'aa_forum_posts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)  # Still private, but not traceable to real identity
    display_name = Column(String(50), nullable=False)  # Anonymous display name
    topic = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey('aa_forum_posts.id'), nullable=True)  # For threaded replies
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship for replies
    replies = relationship("AAForumPost", 
                          backref="parent", 
                          remote_side=[id],
                          cascade="all, delete-orphan")
    
    def to_dict(self, include_replies=False):
        """Convert to dictionary"""
        result = {
            'id': self.id,
            'display_name': self.display_name,
            'topic': self.topic,
            'content': self.content,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_replies:
            result['replies'] = [reply.to_dict(False) for reply in self.replies]
            
        return result