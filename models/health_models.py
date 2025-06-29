"""
Health Models

This module contains health-related database models for the NOUS application,
including DBT (Dialectical Behavior Therapy) and AA (Alcoholics Anonymous) models.
"""

from datetime import datetime
from database import db
from sqlalchemy.ext.hybrid import hybrid_property

class DBTSkillRecommendation(db.Model):
    """Recommended DBT skills for specific situations"""
    __tablename__ = 'dbt_skill_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    situation_type = db.Column(db.String(100))
    skill_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    effectiveness_score = db.Column(db.Float, default=0.0)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_skill_recommendations', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'situation_type': self.situation_type,
            'skill_name': self.skill_name,
            'description': self.description,
            'effectiveness_score': self.effectiveness_score,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DBTSkillLog(db.Model):
    """Log of DBT skills used"""
    __tablename__ = 'dbt_skill_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    skill_name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    situation = db.Column(db.Text)
    effectiveness = db.Column(db.Integer)
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_skill_logs', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_name': self.skill_name,
            'category': self.category,
            'situation': self.situation,
            'effectiveness': self.effectiveness,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class DBTCrisisResource(db.Model):
    """Crisis resources for DBT users"""
    __tablename__ = 'dbt_crisis_resources'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100))
    contact_info = db.Column(db.String(255))
    resource_type = db.Column(db.String(50))
    notes = db.Column(db.Text)
    is_emergency = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_crisis_resources', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'contact_info': self.contact_info,
            'resource_type': self.resource_type,
            'notes': self.notes,
            'is_emergency': self.is_emergency,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DBTSkillCategory(db.Model):
    """Categories for DBT skills"""
    __tablename__ = 'dbt_skill_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class AAAchievement(db.Model):
    """Achievement badges for AA recovery progress"""
    __tablename__ = 'aa_achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.String(50))
    badge_name = db.Column(db.String(100))
    badge_description = db.Column(db.Text)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('aa_achievements', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'badge_name': self.badge_name,
            'badge_description': self.badge_description,
            'awarded_at': self.awarded_at.isoformat() if self.awarded_at else None
        }

class DBTDiaryCard(db.Model):
    """Diary card model for DBT tracking"""
    __tablename__ = 'dbt_diary_cards'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    mood_rating = db.Column(db.Integer)  # 1-10
    triggers = db.Column(db.Text)
    urges = db.Column(db.Text)
    skills_used = db.Column(db.Text)
    reflection = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_diary_cards', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'mood_rating': self.mood_rating,
            'triggers': self.triggers,
            'urges': self.urges,
            'skills_used': self.skills_used,
            'reflection': self.reflection,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DBTSkillChallenge(db.Model):
    """Skill challenge model for DBT practice"""
    __tablename__ = 'dbt_skill_challenges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    difficulty = db.Column(db.Integer, default=1)  # 1-5
    progress = db.Column(db.Integer, default=0)  # 0-100
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_skill_challenges', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'progress': self.progress,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    @hybrid_property
    def is_custom(self):
        """Check if challenge is user-created vs system"""
        return self.user_id is not None

class DBTEmotionTrack(db.Model):
    """Emotion tracking model for DBT"""
    __tablename__ = 'dbt_emotion_tracks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    emotion = db.Column(db.String(50))
    intensity = db.Column(db.Integer)  # 1-10
    trigger = db.Column(db.Text)
    thoughts = db.Column(db.Text)
    behaviors = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('dbt_emotion_tracks', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'emotion': self.emotion,
            'intensity': self.intensity,
            'trigger': self.trigger,
            'thoughts': self.thoughts,
            'behaviors': self.behaviors,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
class AABigBook(db.Model):
    """AA Big Book content model"""
    __tablename__ = 'aa_big_book'

    id = db.Column(db.Integer, primary_key=True)
    chapter_number = db.Column(db.Integer)
    chapter_title = db.Column(db.String(200))
    section_title = db.Column(db.String(200))
    content = db.Column(db.Text)
    page_number = db.Column(db.Integer)
    keywords = db.Column(db.Text)  # JSON string of keywords
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'chapter_number': self.chapter_number,
            'chapter_title': self.chapter_title,
            'section_title': self.section_title,
            'content': self.content,
            'page_number': self.page_number,
            'keywords': self.keywords,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def search_content(cls, query, limit=10):
        """Search AA Big Book content"""
        return cls.query.filter(
            db.or_(
                cls.content.contains(query),
                cls.chapter_title.contains(query),
                cls.section_title.contains(query),
                cls.keywords.contains(query)
            )
        ).limit(limit).all()

class AASpeakerRecording(db.Model):
    """AA Speaker recording model"""
    __tablename__ = 'aa_speaker_recordings'

    id = db.Column(db.Integer, primary_key=True)
    speaker_name = db.Column(db.String(200))
    title = db.Column(db.String(500))
    description = db.Column(db.Text)
    audio_url = db.Column(db.String(500))
    duration_minutes = db.Column(db.Integer)
    recorded_date = db.Column(db.Date)
    sobriety_years = db.Column(db.Float)
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'speaker_name': self.speaker_name,
            'title': self.title,
            'description': self.description,
            'audio_url': self.audio_url,
            'duration_minutes': self.duration_minutes,
            'recorded_date': self.recorded_date.isoformat() if self.recorded_date else None,
            'sobriety_years': self.sobriety_years,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AAFavorite(db.Model):
    """User favorites for AA content"""
    __tablename__ = 'aa_favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    content_type = db.Column(db.String(50))  # 'big_book', 'audio', 'speaker_recording'
    content_id = db.Column(db.Integer)  # ID of the favorited content
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('aa_favorites', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_type': self.content_type,
            'content_id': self.content_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ===== CBT (Cognitive Behavioral Therapy) Models =====

class CBTThoughtRecord(db.Model):
    """CBT thought record for identifying and challenging negative thoughts"""
    __tablename__ = 'cbt_thought_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    situation = db.Column(db.Text, nullable=False)
    automatic_thought = db.Column(db.Text, nullable=False)
    emotion = db.Column(db.String(100))
    emotion_intensity = db.Column(db.Integer)  # 1-10
    physical_symptoms = db.Column(db.Text)
    evidence_for = db.Column(db.Text)
    evidence_against = db.Column(db.Text)
    balanced_thought = db.Column(db.Text)
    new_emotion = db.Column(db.String(100))
    new_emotion_intensity = db.Column(db.Integer)  # 1-10
    behavioral_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('cbt_thought_records', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'situation': self.situation,
            'automatic_thought': self.automatic_thought,
            'emotion': self.emotion,
            'emotion_intensity': self.emotion_intensity,
            'physical_symptoms': self.physical_symptoms,
            'evidence_for': self.evidence_for,
            'evidence_against': self.evidence_against,
            'balanced_thought': self.balanced_thought,
            'new_emotion': self.new_emotion,
            'new_emotion_intensity': self.new_emotion_intensity,
            'behavioral_response': self.behavioral_response,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CBTCognitiveBias(db.Model):
    """CBT cognitive bias identification and tracking"""
    __tablename__ = 'cbt_cognitive_biases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    bias_type = db.Column(db.String(100), nullable=False)  # e.g., "catastrophizing", "all-or-nothing"
    description = db.Column(db.Text)
    example_thought = db.Column(db.Text)
    reframe_suggestion = db.Column(db.Text)
    frequency_count = db.Column(db.Integer, default=1)
    last_occurred = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('cbt_cognitive_biases', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bias_type': self.bias_type,
            'description': self.description,
            'example_thought': self.example_thought,
            'reframe_suggestion': self.reframe_suggestion,
            'frequency_count': self.frequency_count,
            'last_occurred': self.last_occurred.isoformat() if self.last_occurred else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CBTBehaviorExperiment(db.Model):
    """CBT behavioral experiments to test negative beliefs"""
    __tablename__ = 'cbt_behavior_experiments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    belief_to_test = db.Column(db.Text, nullable=False)
    experiment_description = db.Column(db.Text, nullable=False)
    predicted_outcome = db.Column(db.Text)
    confidence_before = db.Column(db.Integer)  # 1-10
    actual_outcome = db.Column(db.Text)
    confidence_after = db.Column(db.Integer)  # 1-10
    lessons_learned = db.Column(db.Text)
    status = db.Column(db.String(50), default='planned')  # planned, in_progress, completed
    planned_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('cbt_behavior_experiments', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'belief_to_test': self.belief_to_test,
            'experiment_description': self.experiment_description,
            'predicted_outcome': self.predicted_outcome,
            'confidence_before': self.confidence_before,
            'actual_outcome': self.actual_outcome,
            'confidence_after': self.confidence_after,
            'lessons_learned': self.lessons_learned,
            'status': self.status,
            'planned_date': self.planned_date.isoformat() if self.planned_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CBTActivitySchedule(db.Model):
    """CBT activity scheduling and behavioral activation"""
    __tablename__ = 'cbt_activity_schedules'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    activity_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # mastery, pleasure, routine, social
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_time = db.Column(db.Time)
    duration_minutes = db.Column(db.Integer)
    difficulty_level = db.Column(db.Integer)  # 1-10
    predicted_mood = db.Column(db.Integer)  # 1-10
    actual_mood_before = db.Column(db.Integer)  # 1-10
    actual_mood_after = db.Column(db.Integer)  # 1-10
    completion_status = db.Column(db.String(50), default='planned')  # planned, completed, skipped, partial
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('cbt_activity_schedules', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_name': self.activity_name,
            'category': self.category,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'duration_minutes': self.duration_minutes,
            'difficulty_level': self.difficulty_level,
            'predicted_mood': self.predicted_mood,
            'actual_mood_before': self.actual_mood_before,
            'actual_mood_after': self.actual_mood_after,
            'completion_status': self.completion_status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CBTMoodLog(db.Model):
    """CBT mood tracking and monitoring"""
    __tablename__ = 'cbt_mood_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    time_of_day = db.Column(db.Time, default=datetime.utcnow)
    primary_emotion = db.Column(db.String(100))
    emotion_intensity = db.Column(db.Integer)  # 1-10
    triggers = db.Column(db.Text)
    thoughts = db.Column(db.Text)
    physical_symptoms = db.Column(db.Text)
    coping_strategy_used = db.Column(db.String(200))
    effectiveness_rating = db.Column(db.Integer)  # 1-10
    energy_level = db.Column(db.Integer)  # 1-10
    sleep_quality = db.Column(db.Integer)  # 1-10
    social_interaction = db.Column(db.String(100))  # none, minimal, moderate, high
    medication_taken = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('cbt_mood_logs', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'time_of_day': self.time_of_day.isoformat() if self.time_of_day else None,
            'primary_emotion': self.primary_emotion,
            'emotion_intensity': self.emotion_intensity,
            'triggers': self.triggers,
            'thoughts': self.thoughts,
            'physical_symptoms': self.physical_symptoms,
            'coping_strategy_used': self.coping_strategy_used,
            'effectiveness_rating': self.effectiveness_rating,
            'energy_level': self.energy_level,
            'sleep_quality': self.sleep_quality,
            'social_interaction': self.social_interaction,
            'medication_taken': self.medication_taken,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CBTCopingSkill(db.Model):
    """CBT coping skills library and tracking"""
    __tablename__ = 'cbt_coping_skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)  # NULL for system skills
    skill_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # grounding, relaxation, cognitive, behavioral, social
    description = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    duration_minutes = db.Column(db.Integer)
    difficulty_level = db.Column(db.Integer)  # 1-5
    effectiveness_situations = db.Column(db.Text)  # JSON array of situation types
    contraindications = db.Column(db.Text)
    is_custom = db.Column(db.Boolean, default=False)
    usage_count = db.Column(db.Integer, default=0)
    average_effectiveness = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('cbt_coping_skills', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_name': self.skill_name,
            'category': self.category,
            'description': self.description,
            'instructions': self.instructions,
            'duration_minutes': self.duration_minutes,
            'difficulty_level': self.difficulty_level,
            'effectiveness_situations': self.effectiveness_situations,
            'contraindications': self.contraindications,
            'is_custom': self.is_custom,
            'usage_count': self.usage_count,
            'average_effectiveness': self.average_effectiveness,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CBTSkillUsage(db.Model):
    """CBT coping skill usage tracking"""
    __tablename__ = 'cbt_skill_usage'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('cbt_coping_skills.id'), nullable=False)
    situation = db.Column(db.Text)
    mood_before = db.Column(db.Integer)  # 1-10
    mood_after = db.Column(db.Integer)  # 1-10
    effectiveness_rating = db.Column(db.Integer)  # 1-10
    duration_used = db.Column(db.Integer)  # minutes
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('cbt_skill_usage', lazy=True))
    skill = db.relationship('CBTCopingSkill', backref=db.backref('usage_logs', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_id': self.skill_id,
            'situation': self.situation,
            'mood_before': self.mood_before,
            'mood_after': self.mood_after,
            'effectiveness_rating': self.effectiveness_rating,
            'duration_used': self.duration_used,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class CBTGoal(db.Model):
    """CBT therapy goals and progress tracking"""
    __tablename__ = 'cbt_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    goal_type = db.Column(db.String(100))  # behavioral, cognitive, emotional, social
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    target_behavior = db.Column(db.Text)
    success_criteria = db.Column(db.Text)  # SMART goal criteria
    baseline_measurement = db.Column(db.Float)
    current_measurement = db.Column(db.Float)
    target_measurement = db.Column(db.Float)
    measurement_unit = db.Column(db.String(50))
    start_date = db.Column(db.Date, default=datetime.utcnow)
    target_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='active')  # active, paused, completed, abandoned
    priority = db.Column(db.String(50), default='medium')  # low, medium, high
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('cbt_goals', lazy=True))

    @hybrid_property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if not all([self.baseline_measurement, self.current_measurement, self.target_measurement]):
            return 0
        
        total_change_needed = abs(self.target_measurement - self.baseline_measurement)
        current_change = abs(self.current_measurement - self.baseline_measurement)
        
        if total_change_needed == 0:
            return 100
        
        return min(100, (current_change / total_change_needed) * 100)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'goal_type': self.goal_type,
            'title': self.title,
            'description': self.description,
            'target_behavior': self.target_behavior,
            'success_criteria': self.success_criteria,
            'baseline_measurement': self.baseline_measurement,
            'current_measurement': self.current_measurement,
            'target_measurement': self.target_measurement,
            'measurement_unit': self.measurement_unit,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'status': self.status,
            'priority': self.priority,
            'progress_percentage': self.progress_percentage,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
