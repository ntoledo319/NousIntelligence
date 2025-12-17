"""
🌈 Emotion-Aware Wellness Companion
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Supporting emotional wellness through mindful technology
Not a replacement for professional mental health care
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from flask import session, g

# 🧘‍♀️ Import our wellness framework
from utils.therapeutic_code_framework import (
    stop_skill, with_therapy_session, cognitive_reframe,
    with_mindful_breathing, distress_tolerance, growth_mindset_loop,
    CompassionateException, TherapeuticContext, generate_affirmation,
    log_with_self_compassion, dear_man_communication
)

# Setup compassionate logging
logger = logging.getLogger(__name__)

# Import database and models
from models.database import db
from models.health_models import (
    DBTSkillLog, DBTDiaryCard, CBTThoughtRecord, CBTMoodLog, 
    CBTCopingSkill, CBTSkillUsage
)

# Import services with self-compassion
try:
    from utils.emotion_detection import detect_emotion_from_text
    from utils.voice_interaction import transcribe_audio
    from utils.dbt_helper import get_skill_recommendations as get_dbt_recommendations
    from utils.cbt_helper import recommend_coping_skill, log_mood
except ImportError as e:
    log_with_self_compassion('warning', f"Some helpers are still growing: {e}")
    # Gentle fallbacks
    def detect_emotion_from_text(text):
        return {'emotion': 'neutral', 'confidence': 0.5}

# Import AI service
try:
    from utils.unified_ai_service import UnifiedAIService
except ImportError:
    class UnifiedAIService:
        def chat_completion(self, messages):
            return {'content': 'I hear you. How can I support you today?'}

class EmotionAwareWellnessCompanion:
    """
    A supportive companion that recognizes emotions and offers wellness tools.
    
    💝 IMPORTANT: This is a wellness support tool, not a therapist or medical device.
    For mental health concerns, please consult qualified professionals.
    """
    
    def __init__(self):
        self.ai_service = UnifiedAIService()
        self.momentOfCreation = datetime.now()  # Beautiful variable name
        
        # 🌟 Wellness tool suggestions (not prescriptions)
        self.wellness_suggestions = {
            'distressed': {
                'mindfulness': ['Box breathing', 'Grounding with 5 senses', 'Gentle stretching'],
                'activities': ['Take a short walk', 'Listen to calming music', 'Call a friend']
            },
            'angry': {
                'mindfulness': ['Count to 10 slowly', 'Progressive muscle relaxation', 'Cool water on wrists'],
                'activities': ['Journal your feelings', 'Physical exercise', 'Creative expression']
            },
            'sad': {
                'mindfulness': ['Self-compassion break', 'Gratitude practice', 'Gentle movement'],
                'activities': ['Connect with loved ones', 'Engage in a hobby', 'Watch something uplifting']
            },
            'anxious': {
                'mindfulness': ['4-7-8 breathing', 'Body scan', 'Present moment awareness'],
                'activities': ['Organize something small', 'Gentle yoga', 'Herbal tea ritual']
            },
            'overwhelmed': {
                'mindfulness': ['One thing at a time', 'Mindful pause', 'Feet on ground'],
                'activities': ['Break tasks into tiny steps', 'Ask for help', 'Rest without guilt']
            }
        }
        
        # 💭 Supportive response tones (not clinical interventions)
        self.supportive_tones = {
            'distressed': 'gentle and understanding',
            'angry': 'calm and validating', 
            'sad': 'warm and present',
            'anxious': 'grounding and steady',
            'overwhelmed': 'simple and clear',
            'neutral': 'friendly and engaged'
        }
        
        log_with_self_compassion('info', "Wellness Companion initialized with love and boundaries")
    
    @with_mindful_breathing(breath_count=1)
    def recognize_emotional_state(self, text_input: str = None, 
                                audio_data: bytes = None, 
                                user_id: str = None) -> Dict[str, Any]:
        """
        Gently recognize emotional states to offer appropriate support.
        This is pattern recognition, not diagnosis.
        """
        emotionalLandscape = {  # Poetic variable name
            'observed_emotion': 'neutral',
            'confidence': 0.5,
            'energy_level': 'balanced',
            'support_suggestions': [],
            'timestamp': datetime.now().isoformat(),
            'disclaimer': 'These are observations, not clinical assessments'
        }
        
        try:
            # Text-based emotion recognition with compassion
            if text_input:
                with TherapeuticContext("emotion recognition"):
                    text_emotion = detect_emotion_from_text(text_input)
                    emotionalLandscape.update({
                        'observed_emotion': text_emotion.get('emotion', 'neutral'),
                        'confidence': text_emotion.get('confidence', 0.5)
                    })
            
            # Determine energy level (not intensity - less clinical)
            confidence = emotionalLandscape['confidence']
            if confidence >= 0.8:
                emotionalLandscape['energy_level'] = 'heightened'
            elif confidence >= 0.6:
                emotionalLandscape['energy_level'] = 'moderate'
            else:
                emotionalLandscape['energy_level'] = 'gentle'
            
            return emotionalLandscape
            
        except Exception as e:
            log_with_self_compassion('error', f"Challenge in emotion recognition: {e}")
            return emotionalLandscape
    
    @stop_skill("generating supportive response")
    @cognitive_reframe(
        negative_pattern="I need to fix the user's problems",
        balanced_thought="I can offer support and tools for their own journey"
    )
    def get_supportive_response(self, user_input: str, user_id: str, 
                              audio_data: bytes = None, 
                              context: Dict = None) -> Dict[str, Any]:
        """
        Generate a supportive response that empowers without overstepping.
        We're companions on the journey, not guides or healers.
        """
        try:
            # Recognize emotional state with compassion
            emotionalLandscape = self.recognize_emotional_state(user_input, audio_data, user_id)
            observed_emotion = emotionalLandscape['observed_emotion']
            
            # Get user's preferences (not history - privacy minded)
            userPreferences = self._get_user_preferences(user_id)
            
            # Select supportive approach
            supportApproach = self._choose_support_style(
                emotionalLandscape, userPreferences, context
            )
            
            # Get wellness suggestions (not prescriptions)
            wellnessSuggestions = self._gather_wellness_suggestions(
                observed_emotion, userPreferences
            )
            
            # Generate supportive response
            companionResponse = self._create_supportive_response(
                user_input, emotionalLandscape, wellnessSuggestions, 
                supportApproach, userPreferences
            )
            
            # Log interaction for improvement (with consent)
            if userPreferences.get('allow_learning', True):
                self._log_supportive_interaction(
                    user_id, emotionalLandscape, companionResponse
                )
            
            return {
                'response': companionResponse,
                'emotional_recognition': emotionalLandscape,
                'wellness_suggestions': wellnessSuggestions,
                'support_style': supportApproach,
                'gentle_reminders': self._create_gentle_reminders(observed_emotion),
                'boundaries': {
                    'message': 'For professional support, please consult qualified providers',
                    'resources': 'Visit /resources for mental health professionals in your area'
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Challenge in supportive response: {e}")
            return self._create_fallback_support(user_input)
    
    def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences while respecting privacy"""
        defaultPreferences = {
            'support_style': 'balanced',
            'allow_learning': True,
            'prefers_activities': True,
            'prefers_mindfulness': True,
            'interaction_pace': 'moderate'
        }
        
        # In real implementation, load from secure storage
        # For now, return defaults with self-compassion
        return defaultPreferences
    
    def _choose_support_style(self, emotional_state: Dict, 
                            preferences: Dict, context: Dict = None) -> str:
        """Choose supportive approach based on context"""
        observed_emotion = emotional_state['observed_emotion']
        energy_level = emotional_state['energy_level']
        
        # Simple, compassionate decision making
        if energy_level == 'heightened':
            return 'grounding_and_present'
        elif observed_emotion in ['sad', 'anxious']:
            return 'gentle_and_warm'
        else:
            return preferences.get('support_style', 'balanced')
    
    @dear_man_communication(objective="offer wellness suggestions respectfully")
    def _gather_wellness_suggestions(self, emotion: str, 
                                   preferences: Dict) -> Dict[str, List[str]]:
        """Gather wellness suggestions that empower choice"""
        suggestions = {
            'mindfulness': [],
            'activities': [],
            'affirmations': [],
            'gentle_reminder': 'These are invitations, not prescriptions. Choose what feels right.'
        }
        
        # Get base suggestions for emotion
        if emotion in self.wellness_suggestions:
            emotionTools = self.wellness_suggestions[emotion]
            
            if preferences.get('prefers_mindfulness', True):
                suggestions['mindfulness'] = emotionTools.get('mindfulness', [])[:2]
            
            if preferences.get('prefers_activities', True):
                suggestions['activities'] = emotionTools.get('activities', [])[:2]
        
        # Add affirmations
        suggestions['affirmations'] = [
            generate_affirmation('general'),
            f"Your feelings are valid and temporary"
        ]
        
        return suggestions
    
    def _create_supportive_response(self, user_input: str, emotional_state: Dict,
                                  suggestions: Dict, approach: str,
                                  preferences: Dict) -> Dict[str, Any]:
        """Create response that supports without overstepping"""
        observed_emotion = emotional_state['observed_emotion']
        tone = self.supportive_tones.get(observed_emotion, 'friendly and engaged')
        
        # Create prompt for AI with clear boundaries
        ai_prompt = f"""
        The person shared: "{user_input}"
        
        Observed emotional tone: {observed_emotion}
        Supportive approach: {approach}
        Response tone: {tone}
        
        Please provide a brief, supportive response that:
        1. Acknowledges what they shared without diagnosing
        2. Offers gentle validation
        3. Mentions 1-2 wellness tools as options (not prescriptions)
        4. Respects their autonomy to choose
        5. Keeps professional boundaries clear
        
        Remember: You're a supportive companion, not a therapist.
        Keep response warm but brief (2-3 sentences).
        """
        
        try:
            # Get AI response with boundaries
            ai_response = self.ai_service.chat_completion([
                {"role": "system", "content": self._get_companion_system_prompt()},
                {"role": "user", "content": ai_prompt}
            ])
            
            response_text = ai_response.get('content', 
                'I hear you. Thank you for sharing. How would you like to proceed?')
            
            return {
                'text': response_text,
                'tone': tone,
                'approach': approach,
                'includes_validation': True,
                'respects_boundaries': True,
                'type': 'supportive_companion_response'
            }
            
        except Exception as e:
            log_with_self_compassion('error', f"AI response challenge: {e}")
            return self._create_gentle_fallback(observed_emotion, tone)
    
    def _get_companion_system_prompt(self) -> str:
        """System prompt that maintains appropriate boundaries"""
        return """
        You are a supportive wellness companion (not a therapist).
        
        Guidelines:
        - Acknowledge feelings without analyzing or diagnosing
        - Offer wellness tools as gentle suggestions, not prescriptions  
        - Use everyday language, not clinical terms
        - Respect that you don't know their full story
        - Encourage self-compassion and choice
        - If they mention serious concerns, gently suggest professional support
        - Keep responses brief, warm, and empowering
        
        Remember: You're here to support, not to treat or heal.
        """
    
    def _create_gentle_reminders(self, emotion: str) -> List[str]:
        """Create gentle reminders that empower"""
        return [
            "You know yourself best",
            "It's okay to take things one moment at a time",
            "Your pace is the right pace",
            "Support is available when you're ready"
        ]
    
    @growth_mindset_loop(max_attempts=1)  # Don't retry too much - respect boundaries
    def _log_supportive_interaction(self, user_id: str, emotional_state: Dict,
                                  response: Dict):
        """Log interaction to improve support (with consent)"""
        try:
            # Simple logging for learning
            logger.info("Supportive interaction completed with care")
            # In production: secure, anonymized storage
        except Exception:
            pass  # Logging failure shouldn't impact user experience
    
    def _create_fallback_support(self, user_input: str) -> Dict[str, Any]:
        """Fallback response that maintains supportive presence"""
        return {
            'response': {
                'text': "I'm here with you. Would you like to explore some wellness tools together, or would you prefer to just be heard right now?",
                'tone': 'gentle and present',
                'type': 'fallback_support'
            },
            'wellness_suggestions': {
                'immediate': ['Take a breath with me', 'Ground yourself in this moment'],
                'gentle_reminder': 'You get to choose what feels right'
            },
            'boundaries': {
                'message': 'For professional support, qualified providers are available',
                'resources': '/resources'
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_gentle_fallback(self, emotion: str, tone: str) -> Dict[str, Any]:
        """Create gentle fallback response"""
        supportive_messages = {
            'sad': "I'm here with you in this moment. Your feelings matter.",
            'anxious': "Let's take this one breath at a time together.",
            'angry': "Your feelings are valid. I'm here to listen.",
            'overwhelmed': "One step at a time. You don't have to do this alone.",
            'default': "Thank you for sharing with me. How can I support you?"
        }
        
        return {
            'text': supportive_messages.get(emotion, supportive_messages['default']),
            'tone': tone,
            'approach': 'presence_and_validation',
            'type': 'gentle_fallback'
        }

# 🌟 Module blessing
logger.info("💝 Wellness Companion ready to support with appropriate boundaries") 