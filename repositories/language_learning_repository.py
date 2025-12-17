"""
Language Learning Repository - Data access layer for language learning operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from models.database import db
from models.language_learning_models import (
    LanguageLearningSession, Vocabulary, Grammar, 
    LearningProgress, LanguageGoal
)

class LanguageLearningRepository:
    """Repository for language learning data access operations"""

    # Learning Session methods
    @staticmethod
    def create_session(user_id: str, session_data: Dict[str, Any]) -> LanguageLearningSession:
        """Create a new learning session"""
        session = LanguageLearningSession(user_id=user_id, **session_data)
        db.session.add(session)
        db.session.commit()
        return session

    @staticmethod
    def get_user_sessions(user_id: str, language: Optional[str] = None, 
                         limit: Optional[int] = None) -> List[LanguageLearningSession]:
        """Get learning sessions for a user"""
        query = LanguageLearningSession.query.filter_by(user_id=user_id)
        if language:
            query = query.filter_by(language=language)
        query = query.order_by(LanguageLearningSession.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    # Vocabulary methods
    @staticmethod
    def add_vocabulary(user_id: str, vocab_data: Dict[str, Any]) -> Vocabulary:
        """Add new vocabulary item"""
        vocab = Vocabulary(user_id=user_id, **vocab_data)
        db.session.add(vocab)
        db.session.commit()
        return vocab

    @staticmethod
    def get_user_vocabulary(user_id: str, language: Optional[str] = None,
                           difficulty: Optional[str] = None) -> List[Vocabulary]:
        """Get vocabulary for a user"""
        query = Vocabulary.query.filter_by(user_id=user_id)
        if language:
            query = query.filter_by(language=language)
        if difficulty:
            query = query.filter_by(difficulty_level=difficulty)
        return query.order_by(Vocabulary.created_at.desc()).all()

    @staticmethod
    def get_vocabulary_for_review(user_id: str, language: str, limit: int = 20) -> List[Vocabulary]:
        """Get vocabulary items that need review"""
        return Vocabulary.query.filter_by(user_id=user_id, language=language)\
                              .filter(Vocabulary.next_review <= datetime.utcnow())\
                              .order_by(Vocabulary.next_review.asc())\
                              .limit(limit).all()

    # Grammar methods
    @staticmethod
    def add_grammar_rule(user_id: str, grammar_data: Dict[str, Any]) -> Grammar:
        """Add new grammar rule"""
        grammar = Grammar(user_id=user_id, **grammar_data)
        db.session.add(grammar)
        db.session.commit()
        return grammar

    @staticmethod
    def get_user_grammar(user_id: str, language: Optional[str] = None) -> List[Grammar]:
        """Get grammar rules for a user"""
        query = Grammar.query.filter_by(user_id=user_id)
        if language:
            query = query.filter_by(language=language)
        return query.order_by(Grammar.created_at.desc()).all()

    # Progress tracking methods
    @staticmethod
    def update_progress(user_id: str, progress_data: Dict[str, Any]) -> LearningProgress:
        """Update learning progress"""
        progress = LearningProgress.query.filter_by(
            user_id=user_id, 
            language=progress_data.get('language')
        ).first()
        
        if progress:
            for key, value in progress_data.items():
                if hasattr(progress, key):
                    setattr(progress, key, value)
        else:
            progress = LearningProgress(user_id=user_id, **progress_data)
            db.session.add(progress)
        
        db.session.commit()
        return progress

    @staticmethod
    def get_user_progress(user_id: str, language: Optional[str] = None) -> List[LearningProgress]:
        """Get learning progress for a user"""
        query = LearningProgress.query.filter_by(user_id=user_id)
        if language:
            query = query.filter_by(language=language)
        return query.all()

    # Language goals methods
    @staticmethod
    def create_language_goal(user_id: str, goal_data: Dict[str, Any]) -> LanguageGoal:
        """Create a new language learning goal"""
        goal = LanguageGoal(user_id=user_id, **goal_data)
        db.session.add(goal)
        db.session.commit()
        return goal

    @staticmethod
    def get_user_language_goals(user_id: str, language: Optional[str] = None,
                               status: Optional[str] = None) -> List[LanguageGoal]:
        """Get language goals for a user"""
        query = LanguageGoal.query.filter_by(user_id=user_id)
        if language:
            query = query.filter_by(language=language)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(LanguageGoal.target_date.asc()).all()

    @staticmethod
    def update_goal_progress(goal_id: int, progress: float) -> Optional[LanguageGoal]:
        """Update language goal progress"""
        goal = LanguageGoal.query.get(goal_id)
        if goal:
            goal.progress = progress
            if progress >= 100:
                goal.status = 'completed'
                goal.completed_at = datetime.utcnow()
            db.session.commit()
        return goal