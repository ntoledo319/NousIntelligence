"""
Language Learning Repository Module

This module provides repository implementations for language learning feature operations
including vocabulary management, learning sessions, and conversation practice.
"""

from typing import Optional, List, Dict, Any, Union
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime, timedelta

from models.language_learning_models import (
    LanguageProfile, VocabularyItem, LearningSession,
    ConversationTemplate, ConversationPrompt
)
from repositories.base import Repository
from models import db

# Configure logging
logger = logging.getLogger(__name__)


class LanguageProfileRepository(Repository):
    """Repository for LanguageProfile model operations"""
    
    def __init__(self):
        """Initialize repository with LanguageProfile model"""
        super().__init__(LanguageProfile)
    
    def get_by_user_id(self, user_id: str) -> List[LanguageProfile]:
        """
        Get all language profiles for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of LanguageProfile objects
        """
        return self.find_by(user_id=user_id)
    
    def get_by_user_and_language(self, user_id: str, learning_language: str) -> Optional[LanguageProfile]:
        """
        Get a specific language profile for a user
        
        Args:
            user_id: User ID
            learning_language: Language code being learned
            
        Returns:
            LanguageProfile or None if not found
        """
        return self.find_one_by(user_id=user_id, learning_language=learning_language)
    
    def create_profile(self, user_id: str, learning_language: str, 
                      native_language: str = 'en-US', 
                      proficiency_level: str = 'beginner',
                      **kwargs) -> Optional[LanguageProfile]:
        """
        Create a new language profile
        
        Args:
            user_id: User ID
            learning_language: Language code being learned
            native_language: User's native language code
            proficiency_level: Initial proficiency level
            **kwargs: Additional profile settings
            
        Returns:
            Created LanguageProfile or None if creation failed
        """
        try:
            profile = LanguageProfile()
            profile.user_id = user_id
            profile.learning_language = learning_language
            profile.native_language = native_language
            profile.proficiency_level = proficiency_level
            
            # Apply any additional kwargs to the profile
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
                    
            db.session.add(profile)
            db.session.commit()
            return profile
        except SQLAlchemyError as e:
            logger.error(f"Error creating language profile: {e}")
            db.session.rollback()
            return None


class VocabularyRepository(Repository):
    """Repository for VocabularyItem model operations"""
    
    def __init__(self):
        """Initialize repository with VocabularyItem model"""
        super().__init__(VocabularyItem)
    
    def get_by_profile_id(self, profile_id: int) -> List[VocabularyItem]:
        """
        Get all vocabulary items for a language profile
        
        Args:
            profile_id: Language profile ID
            
        Returns:
            List of VocabularyItem objects
        """
        return self.find_by(profile_id=profile_id)
    
    def get_items_for_review(self, profile_id: int, limit: int = 20) -> List[VocabularyItem]:
        """
        Get vocabulary items due for review based on spaced repetition
        
        Args:
            profile_id: Language profile ID
            limit: Maximum number of items to return
            
        Returns:
            List of VocabularyItem objects due for review
        """
        now = datetime.utcnow()
        return (VocabularyItem.query
                .filter(VocabularyItem.profile_id == profile_id)
                .filter((VocabularyItem.next_review <= now) | 
                        (VocabularyItem.next_review == None))
                .order_by(VocabularyItem.mastery_level)
                .limit(limit)
                .all())
    
    def add_vocabulary_item(self, profile_id: int, word: str, translation: str, **kwargs) -> Optional[VocabularyItem]:
        """
        Add a new vocabulary item
        
        Args:
            profile_id: Language profile ID
            word: Word in target language
            translation: Translation in native language
            **kwargs: Additional item properties
            
        Returns:
            Created VocabularyItem or None if creation failed
        """
        try:
            item = VocabularyItem()
            item.profile_id = profile_id
            item.word = word
            item.translation = translation
            
            # Apply any additional kwargs to the item
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
                    
            db.session.add(item)
            db.session.commit()
            return item
        except SQLAlchemyError as e:
            logger.error(f"Error adding vocabulary item: {e}")
            db.session.rollback()
            return None
    
    def update_after_review(self, item_id: int, correct: bool) -> Optional[VocabularyItem]:
        """
        Update a vocabulary item after being reviewed
        
        Args:
            item_id: Vocabulary item ID
            correct: Whether the review was correct
            
        Returns:
            Updated VocabularyItem or None if update failed
        """
        try:
            item = self.get_by_id(item_id)
            if not item:
                return None
                
            item.times_reviewed += 1
            item.last_reviewed = datetime.utcnow()
            
            # Adjust mastery level based on correctness
            if correct:
                # Increase mastery level (max 1.0)
                item.mastery_level = min(1.0, item.mastery_level + (1.0 - item.mastery_level) * 0.25)
            else:
                # Decrease mastery level (min 0.0)
                item.mastery_level = max(0.0, item.mastery_level * 0.8)
            
            # Calculate next review time using spaced repetition algorithm
            # Higher mastery = longer intervals between reviews
            days_until_review = self._calculate_review_interval(item.mastery_level, item.times_reviewed)
            item.next_review = datetime.utcnow() + timedelta(days=days_until_review)
            
            db.session.commit()
            return item
        except SQLAlchemyError as e:
            logger.error(f"Error updating vocabulary item after review: {e}")
            db.session.rollback()
            return None
    
    def _calculate_review_interval(self, mastery_level: float, times_reviewed: int) -> float:
        """
        Calculate spaced repetition interval in days
        
        Args:
            mastery_level: Current mastery level (0.0-1.0)
            times_reviewed: Number of previous reviews
            
        Returns:
            Number of days until next review
        """
        # Base interval factors based on mastery level
        if mastery_level < 0.3:
            base_interval = 1  # 1 day
        elif mastery_level < 0.5:
            base_interval = 3  # 3 days
        elif mastery_level < 0.7:
            base_interval = 7  # 1 week
        elif mastery_level < 0.9:
            base_interval = 14  # 2 weeks
        else:
            base_interval = 30  # 1 month
        
        # Adjust for review history - each review increases interval slightly
        review_factor = 1 + (0.1 * min(times_reviewed, 10))
        
        return base_interval * review_factor


class LearningSessionRepository(Repository):
    """Repository for LearningSession model operations"""
    
    def __init__(self):
        """Initialize repository with LearningSession model"""
        super().__init__(LearningSession)
    
    def get_by_profile_id(self, profile_id: int, limit: int = 20) -> List[LearningSession]:
        """
        Get learning sessions for a language profile
        
        Args:
            profile_id: Language profile ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of LearningSession objects
        """
        return (LearningSession.query
                .filter(LearningSession.profile_id == profile_id)
                .order_by(LearningSession.started_at.desc())
                .limit(limit)
                .all())
    
    def create_session(self, profile_id: int, session_type: str, 
                      duration_minutes: int, **kwargs) -> Optional[LearningSession]:
        """
        Create a new learning session
        
        Args:
            profile_id: Language profile ID
            session_type: Type of learning session
            duration_minutes: Duration in minutes
            **kwargs: Additional session properties
            
        Returns:
            Created LearningSession or None if creation failed
        """
        try:
            session = LearningSession()
            session.profile_id = profile_id
            session.session_type = session_type
            session.duration_minutes = duration_minutes
            
            # Apply any additional kwargs to the session
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
                    
            db.session.add(session)
            db.session.commit()
            return session
        except SQLAlchemyError as e:
            logger.error(f"Error creating learning session: {e}")
            db.session.rollback()
            return None
    
    def complete_session(self, session_id: int, score: Optional[float] = None, 
                        items_covered: Optional[int] = None, success_rate: Optional[float] = None,
                        notes: Optional[str] = None) -> Optional[LearningSession]:
        """
        Mark a learning session as completed
        
        Args:
            session_id: Learning session ID
            score: Optional session score
            items_covered: Number of items covered
            success_rate: Success rate as percentage
            notes: Session notes
            
        Returns:
            Updated LearningSession or None if update failed
        """
        try:
            session = self.get_by_id(session_id)
            if not session:
                return None
                
            session.completed_at = datetime.utcnow()
            
            if score is not None:
                session.score = score
            if items_covered is not None:
                session.items_covered = items_covered
            if success_rate is not None:
                session.success_rate = success_rate
            if notes is not None:
                session.notes = notes
                
            db.session.commit()
            return session
        except SQLAlchemyError as e:
            logger.error(f"Error completing learning session: {e}")
            db.session.rollback()
            return None


class ConversationTemplateRepository(Repository):
    """Repository for ConversationTemplate model operations"""
    
    def __init__(self):
        """Initialize repository with ConversationTemplate model"""
        super().__init__(ConversationTemplate)
    
    def get_by_language(self, language: str) -> List[ConversationTemplate]:
        """
        Get conversation templates for a specific language
        
        Args:
            language: Target language code
            
        Returns:
            List of ConversationTemplate objects
        """
        return self.find_by(language=language)
    
    def get_by_language_and_difficulty(self, language: str, difficulty: str) -> List[ConversationTemplate]:
        """
        Get conversation templates by language and difficulty
        
        Args:
            language: Target language code
            difficulty: Difficulty level
            
        Returns:
            List of ConversationTemplate objects
        """
        return self.find_by(language=language, difficulty=difficulty)
    
    def get_template_with_prompts(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a conversation template with all its prompts
        
        Args:
            template_id: Template ID
            
        Returns:
            Dictionary with template and prompts or None if not found
        """
        template = self.get_by_id(template_id)
        if not template:
            return None
            
        return {
            'template': template,
            'prompts': sorted(template.prompts, key=lambda p: p.sequence)
        }