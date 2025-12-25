"""
Language Learning Service

This module provides services for language learning features including
vocabulary management, learning sessions, translation, pronunciation,
and conversation practice.
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import openai
from flask import current_app

from models.language_learning_models import (
    LanguageProfile, VocabularyItem, LearningSession,
    ConversationTemplate, ConversationPrompt
)
from repositories.language_learning import (
    LanguageProfileRepository, VocabularyRepository,
    LearningSessionRepository, ConversationTemplateRepository
)
from utils.multilingual_voice import generate_speech, transcribe_speech, get_pronunciation_feedback

logger = logging.getLogger(__name__)

# Language code mappings
LANGUAGE_CODES = {
    'en-US': 'English (US)',
    'en-GB': 'English (UK)',
    'es-ES': 'Spanish (Spain)',
    'es-MX': 'Spanish (Mexico)',
    'fr-FR': 'French',
    'de-DE': 'German',
    'it-IT': 'Italian',
    'ja-JP': 'Japanese',
    'ko-KR': 'Korean',
    'zh-CN': 'Chinese (Simplified)',
    'zh-TW': 'Chinese (Traditional)',
    'pt-BR': 'Portuguese (Brazil)'
}

# TTS voice mappings by language
TTS_VOICES = {
    'en-US': 'nova',  # English - female voice
    'en-GB': 'fable',  # English - male voice with British accent
    'es-ES': 'nova',  # Spanish - using standard voice
    'es-MX': 'nova',  # Spanish - using standard voice
    'fr-FR': 'alloy',  # French - using alternative voice
    'de-DE': 'onyx',   # German - using alternative voice
    'it-IT': 'shimmer',  # Italian
    'ja-JP': 'nova',   # Japanese
    'ko-KR': 'alloy',  # Korean
    'zh-CN': 'onyx',   # Chinese
    'zh-TW': 'nova',   # Chinese (Traditional)
    'pt-BR': 'shimmer'  # Portuguese
}


class LanguageLearningService:
    """Service for language learning features"""
    
    def __init__(self):
        """Initialize the language learning service"""
        self.profile_repo = LanguageProfileRepository()
        self.vocab_repo = VocabularyRepository()
        self.session_repo = LearningSessionRepository()
        self.template_repo = ConversationTemplateRepository()
    
    def get_user_language_profiles(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all language profiles for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of language profiles with additional metadata
        """
        profiles = self.profile_repo.get_by_user_id(user_id)
        result = []
        
        for profile in profiles:
            # Get progress statistics
            vocab_count = len(self.vocab_repo.get_by_profile_id(profile.id))
            sessions = self.session_repo.get_by_profile_id(profile.id)
            
            # Calculate statistics
            total_minutes = sum(s.duration_minutes for s in sessions if s.completed_at)
            avg_score = None
            if sessions:
                scores = [s.score for s in sessions if s.score is not None]
                avg_score = sum(scores) / len(scores) if scores else None
            
            # Add to result
            result.append({
                'profile': profile,
                'language_name': LANGUAGE_CODES.get(profile.learning_language, profile.learning_language),
                'native_language_name': LANGUAGE_CODES.get(profile.native_language, profile.native_language),
                'vocabulary_count': vocab_count,
                'total_sessions': len(sessions),
                'total_minutes': total_minutes,
                'average_score': avg_score
            })
        
        return result
        
    def get_language_profile_details(self, profile_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a language profile
        
        Args:
            profile_id: Language profile ID
            
        Returns:
            Dictionary with profile details or None if not found
        """
        profile = self.profile_repo.get_by_id(profile_id)
        if not profile:
            return None
            
        # Get vocabulary statistics
        vocabulary = self.vocab_repo.get_by_profile_id(profile_id)
        vocab_by_mastery = {
            'beginner': 0,    # 0.0-0.3
            'learning': 0,    # 0.3-0.7
            'mastered': 0     # 0.7-1.0
        }
        
        for item in vocabulary:
            if item.mastery_level < 0.3:
                vocab_by_mastery['beginner'] += 1
            elif item.mastery_level < 0.7:
                vocab_by_mastery['learning'] += 1
            else:
                vocab_by_mastery['mastered'] += 1
                
        # Get learning sessions
        sessions = self.session_repo.get_by_profile_id(profile_id)
        
        # Calculate statistics
        total_minutes = sum(s.duration_minutes for s in sessions if s.completed_at)
        avg_score = None
        if sessions:
            scores = [s.score for s in sessions if s.score is not None]
            avg_score = sum(scores) / len(scores) if scores else None
            
        # Get recent sessions (up to 5)
        recent_sessions = sorted(
            [s for s in sessions if s.completed_at],
            key=lambda s: s.completed_at,
            reverse=True
        )[:5]
        
        # Create result
        return {
            'profile': profile,
            'language_name': LANGUAGE_CODES.get(profile.learning_language, profile.learning_language),
            'native_language_name': LANGUAGE_CODES.get(profile.native_language, profile.native_language),
            'vocabulary_count': len(vocabulary),
            'vocabulary_by_mastery': vocab_by_mastery,
            'total_sessions': len(sessions),
            'completed_sessions': len([s for s in sessions if s.completed_at]),
            'total_minutes': total_minutes,
            'average_score': avg_score,
            'recent_sessions': recent_sessions
        }
    
    def create_language_profile(self, user_id: str, learning_language: str, 
                              native_language: str = 'en-US', **kwargs) -> Optional[LanguageProfile]:
        """
        Create a new language profile for a user
        
        Args:
            user_id: User ID
            learning_language: Target language code
            native_language: User's native language code
            **kwargs: Additional profile settings
            
        Returns:
            Created profile or None if creation failed
        """
        # Check if profile already exists
        existing = self.profile_repo.get_by_user_and_language(user_id, learning_language)
        if existing:
            logger.info(f"Language profile already exists for {user_id}/{learning_language}")
            return existing
            
        # Create new profile
        return self.profile_repo.create_profile(
            user_id=user_id,
            learning_language=learning_language,
            native_language=native_language,
            **kwargs
        )
    
    def get_vocabulary_for_review(self, profile_id: int, limit: int = 20) -> List[VocabularyItem]:
        """
        Get vocabulary items due for review
        
        Args:
            profile_id: Language profile ID
            limit: Maximum number of items to return
            
        Returns:
            List of vocabulary items
        """
        return self.vocab_repo.get_items_for_review(profile_id, limit)
        
    def get_all_vocabulary(self, profile_id: int) -> List[VocabularyItem]:
        """
        Get all vocabulary items for a profile
        
        Args:
            profile_id: Language profile ID
            
        Returns:
            List of vocabulary items
        """
        return self.vocab_repo.get_by_profile_id(profile_id)
    
    def add_vocabulary_item(self, profile_id: int, word: str, translation: str, 
                          pronunciation: Optional[str] = None, example: Optional[str] = None, 
                          part_of_speech: Optional[str] = None) -> Optional[VocabularyItem]:
        """
        Add a new vocabulary item
        
        Args:
            profile_id: Language profile ID
            word: Word in target language
            translation: Translation in native language
            pronunciation: Pronunciation guide
            example: Example sentence
            part_of_speech: Part of speech
            
        Returns:
            Created vocabulary item or None if creation failed
        """
        # Create dictionary of kwargs for optional parameters
        kwargs = {
            'difficulty': 3,  # Medium difficulty by default
            'mastery_level': 0.0,  # Starting mastery
            'next_review': datetime.utcnow()  # Review immediately
        }
        
        # Add optional parameters if they're not None
        if pronunciation is not None:
            kwargs['pronunciation'] = pronunciation
        if example is not None:
            kwargs['example_sentence'] = example
        if part_of_speech is not None:
            kwargs['part_of_speech'] = part_of_speech
            
        return self.vocab_repo.add_vocabulary_item(
            profile_id=profile_id,
            word=word,
            translation=translation,
            **kwargs
        )
    
    def update_vocabulary_after_review(self, item_id: int, correct: bool) -> Optional[VocabularyItem]:
        """
        Update vocabulary item after being reviewed
        
        Args:
            item_id: Vocabulary item ID
            correct: Whether the answer was correct
            
        Returns:
            Updated vocabulary item or None if update failed
        """
        return self.vocab_repo.update_after_review(item_id, correct)
    
    def start_learning_session(self, profile_id: int, session_type: str) -> Optional[LearningSession]:
        """
        Start a new learning session
        
        Args:
            profile_id: Language profile ID
            session_type: Type of session (vocabulary, conversation, etc.)
            
        Returns:
            Created learning session or None if creation failed
        """
        return self.session_repo.create_session(
            profile_id=profile_id,
            session_type=session_type,
            duration_minutes=0,  # Will be updated on completion
            started_at=datetime.utcnow()
        )
    
    def complete_learning_session(self, session_id: int, duration_minutes: int,
                                score: float = None, items_covered: int = None,
                                success_rate: float = None, notes: str = None) -> Optional[LearningSession]:
        """
        Complete a learning session
        
        Args:
            session_id: Learning session ID
            duration_minutes: Duration in minutes
            score: Optional session score
            items_covered: Number of items covered
            success_rate: Success rate as percentage
            notes: Session notes
            
        Returns:
            Updated learning session or None if update failed
        """
        session = self.session_repo.get_by_id(session_id)
        if not session:
            return None
            
        session.duration_minutes = duration_minutes
        return self.session_repo.complete_session(
            session_id=session_id,
            score=score,
            items_covered=items_covered,
            success_rate=success_rate,
            notes=notes
        )
    
    def get_conversation_templates(self, language: str, difficulty: str = None) -> List[ConversationTemplate]:
        """
        Get conversation templates for practice
        
        Args:
            language: Target language code
            difficulty: Optional difficulty filter
            
        Returns:
            List of conversation templates
        """
        if difficulty:
            return self.template_repo.get_by_language_and_difficulty(language, difficulty)
        return self.template_repo.get_by_language(language)
        
    def get_template_with_prompts(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a conversation template with all its prompts
        
        Args:
            template_id: Template ID
            
        Returns:
            Dictionary with template and prompts or None if not found
        """
        return self.template_repo.get_template_with_prompts(template_id)
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """
        Translate text between languages
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Dictionary with translation results
        """
        try:
            # Get API key from environment
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                return {"error": "Translation service unavailable (missing API key)"}
            
            # Use OpenAI for translation
            client = openai.OpenAI(api_key=api_key)
            
            source_lang_name = LANGUAGE_CODES.get(source_lang, source_lang)
            target_lang_name = LANGUAGE_CODES.get(target_lang, target_lang)
            
            prompt = f"""
            Translate the following text from {source_lang_name} to {target_lang_name}:
            
            {text}
            
            Please provide:
            1. The translation
            2. A pronunciation guide (if applicable)
            3. Any cultural notes or explanations
            
            Return as a JSON object with fields: translation, pronunciation, notes
            """
            
            # Use configurable model (default: gpt-4o-mini for cost-effective translation)
            model = os.environ.get("OPENAI_TRANSLATION_MODEL", "gpt-4o-mini")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional translator."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "original_text": text,
                "translation": result.get("translation", ""),
                "pronunciation": result.get("pronunciation", ""),
                "notes": result.get("notes", ""),
                "source_language": source_lang,
                "target_language": target_lang
            }
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "original_text": text
            }
    
    def get_pronunciation_audio(self, text: str, language: str) -> Dict[str, Any]:
        """
        Generate pronunciation audio for a word or phrase
        
        Args:
            text: Text to pronounce
            language: Language code
            
        Returns:
            Dictionary with audio data
        """
        try:
            # Select appropriate voice for language
            voice = TTS_VOICES.get(language, "nova")
            
            # Use voice_interaction util to generate speech
            result = generate_speech(text, {"voice": voice, "speed": 0.9})
            
            # Add language info to result
            if result.get("success", False):
                result["language"] = language
                result["language_name"] = LANGUAGE_CODES.get(language, language)
                
            return result
            
        except Exception as e:
            logger.error(f"Pronunciation audio error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "language": language
            }
    
    def generate_vocabulary_examples(self, word: str, language: str, 
                                  difficulty: str = "intermediate") -> Dict[str, Any]:
        """
        Generate example sentences for vocabulary
        
        Args:
            word: Word to generate examples for
            language: Language code
            difficulty: Difficulty level
            
        Returns:
            Dictionary with examples
        """
        try:
            # Get API key from environment
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                return {"error": "Service unavailable (missing API key)"}
                
            # Use OpenAI to generate examples
            client = openai.OpenAI(api_key=api_key)
            
            language_name = LANGUAGE_CODES.get(language, language)
            
            prompt = f"""
            Generate 3 example sentences in {language_name} using the word "{word}".
            
            Make the sentences appropriate for {difficulty} level learners.
            
            For each sentence:
            1. Provide the sentence in {language_name}
            2. Provide an English translation
            3. Highlight the usage of "{word}" in context
            
            Return as a JSON array with objects containing: sentence, translation, note
            """
            
            # Use configurable model (default: gpt-4o-mini for cost-effective language learning)
            model = os.environ.get("OPENAI_LANGUAGE_MODEL", "gpt-4o-mini")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"You are a {language_name} language teacher."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "word": word,
                "language": language,
                "examples": result.get("examples", [])
            }
            
        except Exception as e:
            logger.error(f"Example generation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "word": word
            }