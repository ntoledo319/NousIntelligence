"""
Enhanced Voice Interface with Emotion Recognition and Context Awareness
Leverages existing voice interface + unified AI + emotion detection
for emotional state-aware responses and complete hands-free task management
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import re

from voice_interface.speech_to_text import SpeechToText
from voice_interface.text_to_speech import TextToSpeech
from utils.unified_ai_service import UnifiedAIService
from utils.emotion_detection import EmotionDetector
from services.predictive_analytics import predictive_engine

logger = logging.getLogger(__name__)

class EmotionAwareVoiceInterface:
    """Enhanced voice interface with emotion recognition and context awareness"""
    
    def __init__(self):
        """Initialize enhanced voice interface"""
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.ai_service = UnifiedAIService()
        self.emotion_detector = EmotionDetector()
        
        # Conversation context
        self.conversation_history = []
        self.user_emotional_state = {}
        self.context_memory = {}
        
        # Voice command patterns
        self.command_patterns = {
            'task_management': [
                r"(add|create|make) (?:a )?task (?:to )?(.+)",
                r"remind me to (.+)",
                r"schedule (.+) (?:for|at) (.+)",
                r"what (?:are )?(?:my )?tasks",
                r"mark (.+) (?:as )?(?:done|complete)"
            ],
            'calendar': [
                r"what's (?:on )?(?:my )?(?:calendar|schedule)",
                r"do I have (?:any )?(?:meetings|events)",
                r"schedule (?:a )?meeting (?:with )?(.+)",
                r"when is (.+)"
            ],
            'health': [
                r"how am I feeling",
                r"log (?:my )?(?:mood|pain|symptoms)",
                r"take (?:my )?medication",
                r"health (?:check|status)"
            ],
            'weather': [
                r"(?:what's )?(?:the )?weather",
                r"will it rain",
                r"should I (?:bring|take) (?:an )?umbrella"
            ],
            'music': [
                r"play (?:some )?music",
                r"play (.+)",
                r"(?:skip|next) (?:song|track)",
                r"(?:pause|stop) music"
            ],
            'general': [
                r"help",
                r"what can you do",
                r"how are you"
            ]
        }
        
        logger.info("Enhanced Voice Interface initialized")
    
    async def process_voice_input(self, audio_data: bytes, user_id: str) -> Dict[str, Any]:
        """Process voice input with emotion analysis and context awareness"""
        try:
            # Convert speech to text
            text = self.stt.speech_to_text(audio_data)
            if not text:
                return self._create_response("I didn't catch that. Could you repeat?", "neutral")
            
            # Analyze emotion from text and audio
            emotion_data = await self._analyze_emotion(text, audio_data)
            
            # Update user emotional state
            self._update_emotional_state(user_id, emotion_data)
            
            # Get predictions and context
            predictions = predictive_engine.get_active_predictions(user_id)
            context = self._build_context(user_id, text, predictions)
            
            # Process command with emotion and context awareness
            response = await self._process_emotional_command(text, user_id, emotion_data, context)
            
            # Store conversation in history
            self._store_conversation(user_id, text, response, emotion_data)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            return self._create_response("I'm having trouble processing that right now.", "apologetic")
    
    async def _analyze_emotion(self, text: str, audio_data: bytes) -> Dict[str, Any]:
        """Analyze emotion from text and audio features"""
        try:
            # Text-based emotion analysis
            text_emotion = self.emotion_detector.analyze_text_emotion(text)
            
            # Audio-based emotion analysis (simplified)
            audio_emotion = self._analyze_audio_emotion(audio_data)
            
            # Combine text and audio emotion analysis
            combined_emotion = self._combine_emotion_analysis(text_emotion, audio_emotion)
            
            return {
                'primary_emotion': combined_emotion.get('emotion', 'neutral'),
                'confidence': combined_emotion.get('confidence', 0.5),
                'valence': combined_emotion.get('valence', 0.0),  # -1 to 1
                'arousal': combined_emotion.get('arousal', 0.0),  # -1 to 1
                'text_emotion': text_emotion,
                'audio_emotion': audio_emotion
            }
            
        except Exception as e:
            logger.error(f"Error analyzing emotion: {e}")
            return {'primary_emotion': 'neutral', 'confidence': 0.5, 'valence': 0.0, 'arousal': 0.0}
    
    def _analyze_audio_emotion(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze emotion from audio features (simplified implementation)"""
        # This is a simplified implementation
        # In production, you'd use audio signal processing libraries
        # to extract features like pitch, tempo, energy, etc.
        
        audio_length = len(audio_data)
        
        # Simple heuristics based on audio characteristics
        if audio_length > 50000:  # Longer speech might indicate more detail/concern
            return {'emotion': 'engaged', 'confidence': 0.6}
        elif audio_length < 10000:  # Very short might indicate urgency or frustration
            return {'emotion': 'urgent', 'confidence': 0.5}
        else:
            return {'emotion': 'neutral', 'confidence': 0.4}
    
    def _combine_emotion_analysis(self, text_emotion: Dict, audio_emotion: Dict) -> Dict[str, Any]:
        """Combine text and audio emotion analysis"""
        # Weighted combination favoring text analysis
        text_weight = 0.7
        audio_weight = 0.3
        
        # Map emotions to valence/arousal space
        emotion_mapping = {
            'happy': {'valence': 0.8, 'arousal': 0.6},
            'sad': {'valence': -0.6, 'arousal': -0.4},
            'angry': {'valence': -0.7, 'arousal': 0.8},
            'frustrated': {'valence': -0.5, 'arousal': 0.6},
            'excited': {'valence': 0.7, 'arousal': 0.8},
            'calm': {'valence': 0.3, 'arousal': -0.5},
            'neutral': {'valence': 0.0, 'arousal': 0.0},
            'engaged': {'valence': 0.4, 'arousal': 0.3},
            'urgent': {'valence': -0.2, 'arousal': 0.7}
        }
        
        text_emo = text_emotion.get('emotion', 'neutral')
        audio_emo = audio_emotion.get('emotion', 'neutral')
        
        text_vals = emotion_mapping.get(text_emo, {'valence': 0.0, 'arousal': 0.0})
        audio_vals = emotion_mapping.get(audio_emo, {'valence': 0.0, 'arousal': 0.0})
        
        combined_valence = (text_vals['valence'] * text_weight + 
                           audio_vals['valence'] * audio_weight)
        combined_arousal = (text_vals['arousal'] * text_weight + 
                           audio_vals['arousal'] * audio_weight)
        
        # Determine primary emotion from combined values
        if combined_valence > 0.5 and combined_arousal > 0.3:
            primary_emotion = 'excited'
        elif combined_valence > 0.3:
            primary_emotion = 'happy'
        elif combined_valence < -0.5:
            primary_emotion = 'sad' if combined_arousal < 0.0 else 'angry'
        elif combined_arousal > 0.5:
            primary_emotion = 'engaged'
        else:
            primary_emotion = 'neutral'
        
        confidence = (text_emotion.get('confidence', 0.5) * text_weight + 
                     audio_emotion.get('confidence', 0.5) * audio_weight)
        
        return {
            'emotion': primary_emotion,
            'confidence': confidence,
            'valence': combined_valence,
            'arousal': combined_arousal
        }
    
    def _update_emotional_state(self, user_id: str, emotion_data: Dict[str, Any]):
        """Update user's emotional state history"""
        if user_id not in self.user_emotional_state:
            self.user_emotional_state[user_id] = []
        
        emotion_entry = {
            'timestamp': datetime.now().isoformat(),
            'emotion': emotion_data['primary_emotion'],
            'confidence': emotion_data['confidence'],
            'valence': emotion_data['valence'],
            'arousal': emotion_data['arousal']
        }
        
        # Keep last 10 emotional states
        self.user_emotional_state[user_id].append(emotion_entry)
        if len(self.user_emotional_state[user_id]) > 10:
            self.user_emotional_state[user_id].pop(0)
    
    def _build_context(self, user_id: str, text: str, predictions: List[Dict]) -> Dict[str, Any]:
        """Build conversation context"""
        context = {
            'user_id': user_id,
            'current_time': datetime.now().isoformat(),
            'recent_conversations': self.conversation_history[-5:] if self.conversation_history else [],
            'emotional_history': self.user_emotional_state.get(user_id, []),
            'predictions': predictions,
            'user_intent': self._detect_intent(text)
        }
        
        return context
    
    def _detect_intent(self, text: str) -> Dict[str, Any]:
        """Detect user intent from speech"""
        text_lower = text.lower()
        
        for intent_category, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    return {
                        'category': intent_category,
                        'pattern': pattern,
                        'matches': match.groups(),
                        'confidence': 0.8
                    }
        
        return {'category': 'general', 'pattern': None, 'matches': [], 'confidence': 0.3}
    
    async def _process_emotional_command(self, text: str, user_id: str, 
                                       emotion_data: Dict, context: Dict) -> Dict[str, Any]:
        """Process command with emotional awareness"""
        try:
            intent = context['user_intent']
            emotion = emotion_data['primary_emotion']
            
            # Adjust response based on emotional state
            response_tone = self._determine_response_tone(emotion_data, context)
            
            # Route to appropriate handler
            if intent['category'] == 'task_management':
                response = await self._handle_task_command(text, user_id, context, response_tone)
            elif intent['category'] == 'calendar':
                response = await self._handle_calendar_command(text, user_id, context, response_tone)
            elif intent['category'] == 'health':
                response = await self._handle_health_command(text, user_id, context, response_tone)
            elif intent['category'] == 'weather':
                response = await self._handle_weather_command(text, user_id, context, response_tone)
            elif intent['category'] == 'music':
                response = await self._handle_music_command(text, user_id, context, response_tone)
            else:
                response = await self._handle_general_command(text, user_id, context, response_tone)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing emotional command: {e}")
            return self._create_response("I'm having trouble with that request.", "apologetic")
    
    def _determine_response_tone(self, emotion_data: Dict, context: Dict) -> str:
        """Determine appropriate response tone based on user emotion"""
        emotion = emotion_data['primary_emotion']
        valence = emotion_data['valence']
        arousal = emotion_data['arousal']
        
        if emotion in ['sad', 'frustrated', 'angry']:
            return 'supportive'
        elif emotion == 'excited':
            return 'enthusiastic'
        elif emotion == 'urgent':
            return 'efficient'
        elif valence < -0.3:
            return 'gentle'
        elif arousal > 0.5:
            return 'energetic'
        else:
            return 'friendly'
    
    async def _handle_task_command(self, text: str, user_id: str, 
                                 context: Dict, tone: str) -> Dict[str, Any]:
        """Handle task management commands"""
        intent = context['user_intent']
        
        if intent['matches']:
            task_content = intent['matches'][0] if intent['matches'] else text
            
            # Create task using AI service
            ai_prompt = f"""
            User wants to create a task: "{task_content}"
            Emotional tone: {tone}
            
            Generate a well-structured task with:
            1. Clear title
            2. Brief description
            3. Suggested priority
            4. Estimated completion time
            
            Respond in a {tone} manner.
            """
            
            ai_response = self.ai_service.chat_completion([
                {"role": "user", "content": ai_prompt}
            ])
            
            response_text = f"I've created that task for you. {ai_response.get('content', '')}"
            
        else:
            response_text = "What task would you like me to help you with?"
        
        return self._create_response(response_text, tone)
    
    async def _handle_health_command(self, text: str, user_id: str, 
                                   context: Dict, tone: str) -> Dict[str, Any]:
        """Handle health-related commands"""
        emotional_history = context.get('emotional_history', [])
        
        if 'feeling' in text.lower():
            # Analyze recent emotional patterns
            recent_emotions = [e['emotion'] for e in emotional_history[-3:]]
            
            if 'sad' in recent_emotions or 'frustrated' in recent_emotions:
                response_text = "I notice you might be having a tough time. Would you like to talk about it or do something to help you feel better?"
            elif 'excited' in recent_emotions or 'happy' in recent_emotions:
                response_text = "You seem to be in a great mood! That's wonderful to see."
            else:
                response_text = "How are you feeling right now? I'm here to listen and help."
        else:
            response_text = "I can help you track your health. What would you like to log or check?"
        
        return self._create_response(response_text, tone)
    
    async def _handle_calendar_command(self, text: str, user_id: str, 
                                     context: Dict, tone: str) -> Dict[str, Any]:
        """Handle calendar commands"""
        predictions = context.get('predictions', [])
        
        # Check for relevant predictions
        schedule_predictions = [p for p in predictions if 'routine' in p.get('type', '')]
        
        response_text = "Let me check your calendar. "
        if schedule_predictions:
            response_text += f"I notice you usually have activities around this time. "
        
        response_text += "What would you like to know about your schedule?"
        
        return self._create_response(response_text, tone)
    
    async def _handle_weather_command(self, text: str, user_id: str, 
                                    context: Dict, tone: str) -> Dict[str, Any]:
        """Handle weather commands"""
        # Integrate with existing weather service
        response_text = "Let me check the weather for you. "
        
        if 'umbrella' in text.lower():
            response_text += "I'll let you know if you need an umbrella today."
        
        return self._create_response(response_text, tone)
    
    async def _handle_music_command(self, text: str, user_id: str, 
                                  context: Dict, tone: str) -> Dict[str, Any]:
        """Handle music commands"""
        emotion = context.get('emotional_history', [])
        current_emotion = emotion[-1]['emotion'] if emotion else 'neutral'
        
        # Suggest music based on emotion
        if current_emotion == 'sad':
            response_text = "I'll play something uplifting to help brighten your mood."
        elif current_emotion == 'excited':
            response_text = "Great energy! I'll play something that matches your vibe."
        elif current_emotion == 'angry':
            response_text = "Let me play something to help you relax and unwind."
        else:
            response_text = "What kind of music would you like to hear?"
        
        return self._create_response(response_text, tone)
    
    async def _handle_general_command(self, text: str, user_id: str, 
                                    context: Dict, tone: str) -> Dict[str, Any]:
        """Handle general commands and conversation"""
        # Use AI for general conversation with emotional awareness
        emotion_context = f"User seems {context.get('emotional_history', [{}])[-1].get('emotion', 'neutral')}"
        
        ai_prompt = f"""
        User said: "{text}"
        Context: {emotion_context}
        Response tone: {tone}
        
        Respond helpfully as a personal assistant with emotional awareness.
        Be {tone} in your response.
        """
        
        ai_response = self.ai_service.chat_completion([
            {"role": "user", "content": ai_prompt}
        ])
        
        return self._create_response(ai_response.get('content', 'How can I help you?'), tone)
    
    def _create_response(self, text: str, tone: str) -> Dict[str, Any]:
        """Create standardized response"""
        return {
            'text': text,
            'tone': tone,
            'timestamp': datetime.now().isoformat(),
            'audio': self.tts.text_to_speech(text),
            'type': 'voice_response'
        }
    
    def _store_conversation(self, user_id: str, user_input: str, 
                          response: Dict, emotion_data: Dict):
        """Store conversation in history"""
        conversation_entry = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'user_emotion': emotion_data,
            'response': response,
            'response_tone': response.get('tone', 'neutral')
        }
        
        self.conversation_history.append(conversation_entry)
        
        # Keep last 50 conversations
        if len(self.conversation_history) > 50:
            self.conversation_history.pop(0)
    
    def get_emotional_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about user's emotional patterns"""
        if user_id not in self.user_emotional_state:
            return {'insights': 'No emotional data available yet.'}
        
        emotions = self.user_emotional_state[user_id]
        
        # Analyze patterns
        emotion_counts = {}
        for emotion_entry in emotions:
            emotion = emotion_entry['emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        
        avg_valence = sum(e['valence'] for e in emotions) / len(emotions)
        avg_arousal = sum(e['arousal'] for e in emotions) / len(emotions)
        
        insights = {
            'most_common_emotion': most_common_emotion,
            'average_mood': 'positive' if avg_valence > 0 else 'negative',
            'energy_level': 'high' if avg_arousal > 0 else 'low',
            'emotional_stability': 'stable' if len(set(e['emotion'] for e in emotions)) < 4 else 'variable',
            'total_interactions': len(emotions)
        }
        
        return insights

# Global instance
enhanced_voice = EmotionAwareVoiceInterface()