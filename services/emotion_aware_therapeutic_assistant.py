"""
Emotion-Aware Therapeutic Assistant
Integrates vocal/textual emotion understanding with DBT/CBT skills for adaptive therapeutic guidance
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from flask import session
from sqlalchemy import and_, or_, desc, func

# Setup logger
logger = logging.getLogger(__name__)

# Import database and models
from database import db
from models.health_models import (
    DBTSkillLog, DBTDiaryCard, CBTThoughtRecord, CBTMoodLog, 
    CBTCopingSkill, CBTSkillUsage
)

# Import existing services
try:
    from utils.emotion_detection import detect_emotion_from_text
    from utils.voice_interaction import transcribe_audio
    from utils.dbt_helper import get_skill_recommendations as get_dbt_recommendations, log_dbt_skill
    from utils.cbt_helper import recommend_coping_skill, log_mood, get_coping_skills
except ImportError as e:
    print(f"Import warning: {e}")  # Temporary fallback until logger is defined
    # Fallback implementations
    def detect_emotion_from_text(text):
        return {'emotion': 'neutral', 'confidence': 0.5}
    def transcribe_audio(audio_data, user_id):
        return {'success': False, 'error': 'Audio processing unavailable'}

# Import AI service
try:
    from utils.unified_ai_service import UnifiedAIService
except ImportError:
    # Fallback AI service
    class UnifiedAIService:
        def chat_completion(self, messages):
            return {'content': 'I understand you\'re sharing something important. How can I best support you?'}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionAwareTherapeuticAssistant:
    """
    Main therapeutic assistant that integrates emotion detection with DBT/CBT skills
    for personalized, context-aware therapeutic guidance
    """
    
    def __init__(self):
        self.ai_service = UnifiedAIService()
        
        # Emotion to skill mapping
        self.emotion_skill_mapping = {
            'distressed': {
                'dbt': ['TIPP', 'Radical Acceptance', 'Distress Tolerance', 'Self-Soothing'],
                'cbt': ['Progressive Muscle Relaxation', 'Grounding Exercises', 'Breathing Techniques']
            },
            'angry': {
                'dbt': ['TIPP', 'Opposite Action', 'STOP skill', 'Wise Mind'],
                'cbt': ['Thought Challenging', 'Anger Management', 'Cooling Down Techniques']
            },
            'sad': {
                'dbt': ['Opposite Action', 'Behavioral Activation', 'PLEASE skill'],
                'cbt': ['Behavioral Activation', 'Pleasant Activity Scheduling', 'Mood Lifting']
            },
            'anxious': {
                'dbt': ['Paced Breathing', 'Mindfulness', 'Grounding'],
                'cbt': ['Breathing Techniques', 'Grounding Exercises', 'Worry Time']
            },
            'overwhelmed': {
                'dbt': ['TIPP', 'Radical Acceptance', 'One Thing at a Time'],
                'cbt': ['Priority Setting', 'Task Breaking', 'Mindfulness']
            },
            'frustrated': {
                'dbt': ['STOP skill', 'Wise Mind', 'Interpersonal Effectiveness'],
                'cbt': ['Problem Solving', 'Perspective Taking', 'Communication Skills']
            }
        }
        
        # Therapeutic tone adjustments based on emotion
        self.therapeutic_tones = {
            'distressed': 'gentle and validating',
            'angry': 'calm and non-confrontational', 
            'sad': 'warm and encouraging',
            'anxious': 'reassuring and grounding',
            'overwhelmed': 'structured and supportive',
            'frustrated': 'patient and understanding',
            'neutral': 'supportive and engaging'
        }
    
    def analyze_emotional_state(self, text_input: str = None, audio_data: bytes = None, 
                              user_id: str = None) -> Dict[str, Any]:
        """
        Comprehensive emotional state analysis from text and/or audio
        """
        emotion_data = {
            'primary_emotion': 'neutral',
            'confidence': 0.5,
            'emotional_intensity': 'moderate',
            'context_factors': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Text-based emotion detection
            if text_input:
                text_emotion = detect_emotion_from_text(text_input)
                emotion_data.update({
                    'primary_emotion': text_emotion.get('emotion', 'neutral'),
                    'confidence': text_emotion.get('confidence', 0.5),
                    'text_analysis': text_emotion
                })
            
            # Audio-based emotion detection
            if audio_data:
                audio_emotion = analyze_voice_audio(audio_data, user_id)
                if audio_emotion.get('success'):
                    audio_result = audio_emotion['result']
                    # Combine text and audio emotions
                    emotion_data['audio_analysis'] = audio_result
                    emotion_data['voice_characteristics'] = audio_result.get('voice_features', {})
            
            # Determine emotional intensity
            confidence = emotion_data['confidence']
            if confidence >= 0.8:
                emotion_data['emotional_intensity'] = 'high'
            elif confidence >= 0.6:
                emotion_data['emotional_intensity'] = 'moderate'
            else:
                emotion_data['emotional_intensity'] = 'low'
            
            # Add contextual factors
            emotion_data['context_factors'] = self._analyze_context_factors(
                text_input, emotion_data['primary_emotion']
            )
            
            return emotion_data
            
        except Exception as e:
            logger.error(f"Error analyzing emotional state: {str(e)}")
            return emotion_data
    
    def get_therapeutic_response(self, user_input: str, user_id: str, 
                               audio_data: bytes = None, context: Dict = None) -> Dict[str, Any]:
        """
        Generate adaptive therapeutic response based on emotional state and therapeutic skills
        """
        try:
            # Analyze emotional state
            emotion_analysis = self.analyze_emotional_state(user_input, audio_data, user_id)
            primary_emotion = emotion_analysis['primary_emotion']
            
            # Get user's therapeutic history and preferences
            user_profile = self._get_user_therapeutic_profile(user_id)
            
            # Determine appropriate therapeutic approach
            therapeutic_approach = self._select_therapeutic_approach(
                emotion_analysis, user_profile, context
            )
            
            # Get skill recommendations
            skill_recommendations = self._get_contextual_skill_recommendations(
                primary_emotion, user_profile, therapeutic_approach
            )
            
            # Generate adaptive response
            response = self._generate_adaptive_response(
                user_input, emotion_analysis, skill_recommendations, 
                therapeutic_approach, user_profile
            )
            
            # Log interaction for learning
            self._log_therapeutic_interaction(
                user_id, user_input, emotion_analysis, response, skill_recommendations
            )
            
            return {
                'response': response,
                'emotion_analysis': emotion_analysis,
                'skills_recommended': skill_recommendations,
                'therapeutic_approach': therapeutic_approach,
                'follow_up_suggestions': self._generate_follow_up_suggestions(
                    primary_emotion, skill_recommendations
                ),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating therapeutic response: {str(e)}")
            return self._generate_fallback_response(user_input)
    
    def _analyze_context_factors(self, text: str, emotion: str) -> List[str]:
        """Analyze additional context factors that might influence therapeutic approach"""
        factors = []
        
        if not text:
            return factors
        
        text_lower = text.lower()
        
        # Crisis indicators
        crisis_keywords = ['suicide', 'kill myself', 'end it all', 'can\'t go on', 'hopeless']
        if any(keyword in text_lower for keyword in crisis_keywords):
            factors.append('crisis_risk')
        
        # Relationship context
        relationship_keywords = ['partner', 'family', 'friend', 'work', 'boss', 'colleague']
        if any(keyword in text_lower for keyword in relationship_keywords):
            factors.append('interpersonal_context')
        
        # Work/school stress
        work_keywords = ['work', 'job', 'school', 'exam', 'deadline', 'presentation']
        if any(keyword in text_lower for keyword in work_keywords):
            factors.append('performance_stress')
        
        # Physical symptoms
        physical_keywords = ['tired', 'exhausted', 'pain', 'headache', 'sick', 'sleep']
        if any(keyword in text_lower for keyword in physical_keywords):
            factors.append('physical_symptoms')
        
        # Cognitive patterns
        cognitive_keywords = ['always', 'never', 'everyone', 'nobody', 'should', 'must']
        if any(keyword in text_lower for keyword in cognitive_keywords):
            factors.append('cognitive_distortions')
        
        return factors
    
    def _get_user_therapeutic_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user's therapeutic history and preferences"""
        profile = {
            'preferred_approach': 'balanced',  # dbt, cbt, or balanced
            'skill_effectiveness': {},
            'recent_emotions': [],
            'therapeutic_goals': [],
            'crisis_history': False
        }
        
        try:
            # Get recent DBT skill usage
            recent_dbt = db.session.query(DBTSkillLog)\
                .filter(DBTSkillLog.user_id == user_id)\
                .filter(DBTSkillLog.timestamp >= datetime.now() - timedelta(days=30))\
                .all()
            
            # Get recent CBT skill usage
            recent_cbt = db.session.query(CBTSkillUsage)\
                .filter(CBTSkillUsage.user_id == user_id)\
                .filter(CBTSkillUsage.timestamp >= datetime.now() - timedelta(days=30))\
                .all()
            
            # Get recent mood logs
            recent_moods = db.session.query(CBTMoodLog)\
                .filter(CBTMoodLog.user_id == user_id)\
                .filter(CBTMoodLog.timestamp >= datetime.now() - timedelta(days=7))\
                .order_by(desc(CBTMoodLog.timestamp))\
                .limit(10)\
                .all()
            
            # Analyze effectiveness
            for skill_log in recent_dbt:
                if skill_log.effectiveness:
                    skill_name = skill_log.skill_name
                    if skill_name not in profile['skill_effectiveness']:
                        profile['skill_effectiveness'][skill_name] = []
                    profile['skill_effectiveness'][skill_name].append(skill_log.effectiveness)
            
            # Determine preferred approach
            dbt_usage = len(recent_dbt)
            cbt_usage = len(recent_cbt)
            
            if dbt_usage > cbt_usage * 1.5:
                profile['preferred_approach'] = 'dbt'
            elif cbt_usage > dbt_usage * 1.5:
                profile['preferred_approach'] = 'cbt'
            
            # Recent emotional patterns
            profile['recent_emotions'] = [
                {'emotion': mood.mood, 'intensity': mood.intensity, 'date': mood.timestamp}
                for mood in recent_moods
            ]
            
        except Exception as e:
            logger.error(f"Error getting user therapeutic profile: {str(e)}")
        
        return profile
    
    def _select_therapeutic_approach(self, emotion_analysis: Dict, 
                                   user_profile: Dict, context: Dict = None) -> str:
        """Select most appropriate therapeutic approach based on context"""
        primary_emotion = emotion_analysis['primary_emotion']
        intensity = emotion_analysis['emotional_intensity']
        context_factors = emotion_analysis['context_factors']
        
        # Crisis situations need immediate DBT distress tolerance
        if 'crisis_risk' in context_factors:
            return 'dbt_crisis'
        
        # High intensity emotions often benefit from DBT
        if intensity == 'high' and primary_emotion in ['angry', 'distressed', 'overwhelmed']:
            return 'dbt_focused'
        
        # Cognitive distortions suggest CBT approach
        if 'cognitive_distortions' in context_factors:
            return 'cbt_focused'
        
        # Use user preference if available
        preferred = user_profile.get('preferred_approach', 'balanced')
        if preferred in ['dbt', 'cbt']:
            return f"{preferred}_focused"
        
        return 'integrated'
    
    def _get_contextual_skill_recommendations(self, emotion: str, user_profile: Dict, 
                                            approach: str) -> Dict[str, List[str]]:
        """Get skill recommendations based on emotion and therapeutic approach"""
        recommendations = {'dbt': [], 'cbt': [], 'priority': []}
        
        # Get base skills for emotion
        if emotion in self.emotion_skill_mapping:
            emotion_skills = self.emotion_skill_mapping[emotion]
            recommendations['dbt'] = emotion_skills.get('dbt', [])
            recommendations['cbt'] = emotion_skills.get('cbt', [])
        
        # Filter based on user effectiveness
        skill_effectiveness = user_profile.get('skill_effectiveness', {})
        
        # Prioritize skills that have worked well for the user
        effective_skills = []
        for skill, effectiveness_scores in skill_effectiveness.items():
            avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores)
            if avg_effectiveness >= 4:  # Good effectiveness (1-5 scale)
                effective_skills.append(skill)
        
        # Adjust recommendations based on approach
        if approach == 'dbt_focused' or approach == 'dbt_crisis':
            recommendations['priority'] = recommendations['dbt'][:3]
        elif approach == 'cbt_focused':
            recommendations['priority'] = recommendations['cbt'][:3]
        else:  # integrated
            # Mix the best from both
            recommendations['priority'] = (
                recommendations['dbt'][:2] + recommendations['cbt'][:2]
            )
        
        # Add effective skills to priority
        for skill in effective_skills:
            if skill not in recommendations['priority']:
                recommendations['priority'].insert(0, skill)
        
        return recommendations
    
    def _generate_adaptive_response(self, user_input: str, emotion_analysis: Dict,
                                  skill_recommendations: Dict, approach: str,
                                  user_profile: Dict) -> Dict[str, Any]:
        """Generate response adapted to user's emotional state and needs"""
        primary_emotion = emotion_analysis['primary_emotion']
        intensity = emotion_analysis['emotional_intensity']
        
        # Determine therapeutic tone
        tone = self.therapeutic_tones.get(primary_emotion, 'supportive and engaging')
        
        # Create AI prompt for therapeutic response
        ai_prompt = self._create_therapeutic_prompt(
            user_input, emotion_analysis, skill_recommendations, approach, tone
        )
        
        try:
            # Get AI response
            ai_response = self.ai_service.chat_completion([
                {"role": "system", "content": self._get_therapeutic_system_prompt()},
                {"role": "user", "content": ai_prompt}
            ])
            
            response_text = ai_response.get('content', 'I understand you\'re going through something difficult. How can I best support you right now?')
            
            # Add skill suggestions
            skill_suggestions = self._format_skill_suggestions(skill_recommendations)
            
            return {
                'text': response_text,
                'tone': tone,
                'approach': approach,
                'emotion_acknowledged': primary_emotion,
                'intensity_level': intensity,
                'skill_suggestions': skill_suggestions,
                'immediate_actions': self._get_immediate_actions(primary_emotion, intensity),
                'type': 'therapeutic_response'
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return self._generate_fallback_therapeutic_response(primary_emotion, tone)
    
    def _create_therapeutic_prompt(self, user_input: str, emotion_analysis: Dict,
                                 skill_recommendations: Dict, approach: str, tone: str) -> str:
        """Create therapeutic AI prompt"""
        primary_emotion = emotion_analysis['primary_emotion']
        context_factors = emotion_analysis.get('context_factors', [])
        
        prompt = f"""
        The user said: "{user_input}"
        
        Emotional Analysis:
        - Primary emotion: {primary_emotion}
        - Intensity: {emotion_analysis['emotional_intensity']}
        - Context factors: {', '.join(context_factors) if context_factors else 'None identified'}
        
        Therapeutic Approach: {approach}
        Response Tone: {tone}
        
        Recommended Skills:
        - Priority skills: {', '.join(skill_recommendations.get('priority', []))}
        - DBT options: {', '.join(skill_recommendations.get('dbt', []))}
        - CBT options: {', '.join(skill_recommendations.get('cbt', []))}
        
        Provide a therapeutic response that:
        1. Validates their emotional experience
        2. Uses a {tone} tone
        3. Gently suggests 1-2 most appropriate skills
        4. Offers specific, actionable guidance
        5. Maintains hope and empowerment
        
        Keep response concise but meaningful (2-3 sentences).
        """
        
        return prompt
    
    def _get_therapeutic_system_prompt(self) -> str:
        """Get system prompt for therapeutic AI responses"""
        return """
        You are an empathetic therapeutic assistant trained in DBT and CBT approaches.
        
        Guidelines:
        - Always validate emotions before offering suggestions
        - Use person-first, non-pathologizing language
        - Offer specific, actionable skills rather than generic advice
        - Match your tone to the user's emotional state
        - Encourage self-efficacy and hope
        - If crisis indicators are present, prioritize safety and professional help
        - Keep responses concise but warm
        
        Remember: You supplement, not replace, professional therapy.
        """
    
    def _format_skill_suggestions(self, recommendations: Dict) -> List[Dict[str, Any]]:
        """Format skill suggestions for user interface"""
        suggestions = []
        
        for skill in recommendations.get('priority', []):
            suggestions.append({
                'name': skill,
                'type': 'priority',
                'description': self._get_skill_description(skill),
                'quick_action': self._get_skill_quick_action(skill)
            })
        
        return suggestions
    
    def _get_skill_description(self, skill_name: str) -> str:
        """Get brief description of therapeutic skill"""
        descriptions = {
            'TIPP': 'Temperature, Intense exercise, Paced breathing, Progressive muscle relaxation',
            'Radical Acceptance': 'Accepting reality as it is, not as you wish it were',
            'STOP skill': 'Stop, Take a step back, Observe, Proceed mindfully',
            'Wise Mind': 'Balance between emotional mind and reasonable mind',
            'Opposite Action': 'Act opposite to your emotional urge',
            'Breathing Techniques': 'Controlled breathing to manage anxiety and stress',
            'Grounding Exercises': '5-4-3-2-1 technique to connect with present moment',
            'Thought Challenging': 'Examine and question negative thought patterns',
            'Progressive Muscle Relaxation': 'Systematically tense and relax muscle groups',
            'Behavioral Activation': 'Engage in meaningful activities to improve mood'
        }
        return descriptions.get(skill_name, 'Evidence-based therapeutic technique')
    
    def _get_skill_quick_action(self, skill_name: str) -> str:
        """Get quick action button text for skill"""
        actions = {
            'TIPP': 'Start TIPP sequence',
            'Breathing Techniques': 'Begin breathing exercise',
            'Grounding Exercises': 'Try 5-4-3-2-1',
            'Thought Challenging': 'Challenge thoughts',
            'STOP skill': 'Practice STOP',
            'Wise Mind': 'Find wise mind',
            'Radical Acceptance': 'Practice acceptance',
            'Progressive Muscle Relaxation': 'Start PMR'
        }
        return actions.get(skill_name, f'Practice {skill_name}')
    
    def _get_immediate_actions(self, emotion: str, intensity: str) -> List[str]:
        """Get immediate action suggestions based on emotion and intensity"""
        if intensity == 'high':
            if emotion in ['angry', 'frustrated']:
                return ['Take 5 deep breaths', 'Step away from situation', 'Count to 10']
            elif emotion in ['anxious', 'overwhelmed']:
                return ['Ground yourself (5-4-3-2-1)', 'Focus on breathing', 'Find safe space']
            elif emotion == 'sad':
                return ['Reach out to support', 'Practice self-compassion', 'Engage in self-care']
        
        return ['Take a moment to breathe', 'Notice your feelings', 'Be kind to yourself']
    
    def _generate_follow_up_suggestions(self, emotion: str, skills: Dict) -> List[str]:
        """Generate follow-up suggestions for continued support"""
        suggestions = []
        
        if skills.get('priority'):
            suggestions.append(f"Practice {skills['priority'][0]} for 5 minutes")
        
        suggestions.extend([
            "Log this experience in your mood tracker",
            "Reflect on what triggered this feeling",
            "Consider reaching out to your support network"
        ])
        
        if emotion in ['sad', 'anxious', 'overwhelmed']:
            suggestions.append("Schedule a pleasant activity for later today")
        
        return suggestions[:3]
    
    def _log_therapeutic_interaction(self, user_id: str, user_input: str,
                                   emotion_analysis: Dict, response: Dict,
                                   skills: Dict):
        """Log interaction for learning and tracking"""
        try:
            # Log mood if not already logged today
            today = datetime.now().date()
            existing_mood = db.session.query(CBTMoodLog)\
                .filter(CBTMoodLog.user_id == user_id)\
                .filter(func.date(CBTMoodLog.timestamp) == today)\
                .first()
            
            if not existing_mood:
                mood_log = CBTMoodLog(
                    user_id=user_id,
                    mood=emotion_analysis['primary_emotion'],
                    intensity=self._emotion_intensity_to_number(emotion_analysis['emotional_intensity']),
                    notes=f"Auto-logged from interaction: {user_input[:100]}...",
                    timestamp=datetime.now()
                )
                db.session.add(mood_log)
            
            # You could also log to a therapeutic interaction table if it exists
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error logging therapeutic interaction: {str(e)}")
            db.session.rollback()
    
    def _emotion_intensity_to_number(self, intensity: str) -> int:
        """Convert emotion intensity to number scale"""
        mapping = {'low': 2, 'moderate': 4, 'high': 6}
        return mapping.get(intensity, 4)
    
    def _generate_fallback_response(self, user_input: str) -> Dict[str, Any]:
        """Generate fallback response when main processing fails"""
        return {
            'response': {
                'text': "I can sense you're going through something. I'm here to listen and support you. What would be most helpful right now?",
                'tone': 'supportive and engaging',
                'type': 'fallback_response'
            },
            'emotion_analysis': {'primary_emotion': 'neutral', 'confidence': 0.5},
            'skills_recommended': {'priority': ['Breathing Techniques', 'Grounding Exercises']},
            'therapeutic_approach': 'supportive'
        }
    
    def _generate_fallback_therapeutic_response(self, emotion: str, tone: str) -> Dict[str, Any]:
        """Generate therapeutic fallback response"""
        responses = {
            'distressed': "I can see you're in distress right now. Take a deep breath with me. What do you need most in this moment?",
            'angry': "I hear that you're feeling angry. That's completely valid. Let's take a moment to breathe together.",
            'sad': "I can feel the sadness in your words. It's okay to feel this way. You don't have to go through this alone.",
            'anxious': "I notice you're feeling anxious. Let's ground ourselves together. Can you tell me 5 things you can see right now?",
            'neutral': "I'm here to support you however you need. What's on your mind today?"
        }
        
        return {
            'text': responses.get(emotion, responses['neutral']),
            'tone': tone,
            'approach': 'supportive',
            'emotion_acknowledged': emotion,
            'skill_suggestions': [{'name': 'Breathing Techniques', 'type': 'priority'}],
            'type': 'fallback_therapeutic_response'
        }

# Global instance for easy access
therapeutic_assistant = EmotionAwareTherapeuticAssistant()