"""
AA Content Management Models
Models for managing AA (Alcoholics Anonymous) content, resources, and user progress
"""

from database import db
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class AAContentCategory(db.Model):
    """Categories for organizing AA content"""
    __tablename__ = 'aa_content_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    content_items = relationship("AAContentItem", back_populates="category")


class AAContentItem(db.Model):
    """Individual AA content items (readings, prayers, stories, etc.)"""
    __tablename__ = 'aa_content_items'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=False)  # reading, prayer, story, meditation
    category_id = Column(Integer)
    day_of_year = Column(Integer)  # For daily content (1-366)
    step_number = Column(Integer)  # For 12-step content (1-12)
    tradition_number = Column(Integer)  # For traditions (1-12)
    source = Column(String(255))  # Source book/author
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    category = relationship("AAContentCategory", back_populates="content_items")
    user_progress = relationship("AAUserProgress", back_populates="content_item")


class AAUserProgress(db.Model):
    """Track user progress through AA content"""
    __tablename__ = 'aa_user_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    content_item_id = Column(Integer, nullable=False)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notes = Column(Text)  # User's personal notes
    rating = Column(Integer)  # 1-5 star rating
    
    # Relationships
    content_item = relationship("AAContentItem", back_populates="user_progress")


class AAMilestone(db.Model):
    """Track AA milestones (sobriety dates, achievements, etc.)"""
    __tablename__ = 'aa_milestones'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    milestone_type = Column(String(50), nullable=False)  # sobriety_date, chip, anniversary
    milestone_date = Column(DateTime, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    is_achieved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AAMeeting(db.Model):
    """AA meeting information and tracking"""
    __tablename__ = 'aa_meetings'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    virtual_link = Column(String(500))
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    time = Column(String(10), nullable=False)  # HH:MM format
    meeting_type = Column(String(100))  # Open, Closed, Big Book, etc.
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    attendances = relationship("AAMeetingAttendance", back_populates="meeting")


class AAMeetingAttendance(db.Model):
    """Track user attendance at AA meetings"""
    __tablename__ = 'aa_meeting_attendance'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    meeting_id = Column(Integer, nullable=False)
    attended_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notes = Column(Text)
    
    # Relationships
    meeting = relationship("AAMeeting", back_populates="attendances")


class AASponsorRelationship(db.Model):
    """Track sponsor/sponsee relationships"""
    __tablename__ = 'aa_sponsor_relationships'
    
    id = Column(Integer, primary_key=True)
    sponsor_id = Column(Integer, nullable=False)
    sponsee_id = Column(Integer, nullable=False)
    relationship_type = Column(String(50), default='sponsor')  # sponsor, temporary_sponsor
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)


# Helper functions for AA content management
def get_daily_content(day_of_year=None):
    """Get daily AA content for a specific day"""
    if day_of_year is None:
        day_of_year = datetime.now().timetuple().tm_yday
    
    return AAContentItem.query.filter_by(
        day_of_year=day_of_year,
        is_active=True
    ).all()


def get_step_content(step_number):
    """Get content for a specific step"""
    return AAContentItem.query.filter_by(
        step_number=step_number,
        is_active=True
    ).all()


def get_user_progress(user_id, content_type=None):
    """Get user's progress through AA content"""
    query = AAUserProgress.query.filter_by(user_id=user_id)
    
    if content_type:
        query = query.join(AAContentItem).filter(AAContentItem.content_type == content_type)
    
    return query.all()


def create_daily_content_schedule():
    """Create a full year's worth of daily content"""
    categories = {
        'daily_reading': 'Daily readings and reflections',
        'meditation': 'Daily meditation and prayer',
        'step_work': 'Step work and reflection',
        'tradition': 'Tradition study and application'
    }
    
    # Create categories if they don't exist
    for name, description in categories.items():
        category = AAContentCategory.query.filter_by(name=name).first()
        if not category:
            category = AAContentCategory(name=name, description=description)
            db.session.add(category)
    
    db.session.commit()
    return "Daily content schedule framework created successfully"

class AABigBook(db.Model):
    __table_args__ = {"extend_existing": True}
    """AA Big Book content and chapters"""
    __tablename__ = 'aa_big_book'
    
    id = Column(Integer, primary_key=True)
    chapter_number = Column(Integer, nullable=False)
    chapter_title = Column(String(255), nullable=False)
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
