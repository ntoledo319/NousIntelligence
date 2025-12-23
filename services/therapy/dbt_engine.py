"""
DBT Engine

Implements Dialectical Behavior Therapy logic, focusing on TIPP skills
and empathic validation.
"""

import logging
import random
from typing import Any, Dict

from services.content_service import get_content_service

logger = logging.getLogger(__name__)

class DBTEngine:
    def __init__(self):
        self.content_service = get_content_service()

    def process_tipp_skill(self, session_state: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """
        Guides user through TIPP distress tolerance skills.
        """
        current_step_id = session_state.get('step', 'temperature')

        tipp_content = self.content_service.get_intervention('dbt', 'tipp')
        if not tipp_content:
             return {'error': 'Content missing', 'message': "Content unavailable."}

        steps = {s['id']: s for s in tipp_content['steps']}
        current_step_data = steps.get(current_step_id)

        if session_state.get('started'):
             # User confirmed they did the previous step
             next_step_id = current_step_data.get('next')

             if next_step_id == 'complete':
                 return {
                     'message': "Well done. Take a moment to notice if your distress has come down. I'm here if you need more support.",
                     'is_complete': True,
                     'state_update': session_state
                 }

             session_state['step'] = next_step_id
             return {
                 'message': steps[next_step_id]['prompt'],
                 'state_update': session_state,
                 'is_complete': False
             }
        else:
            session_state['started'] = True
            session_state['step'] = 'temperature'
            return {
                'message': steps['temperature']['prompt'],
                'state_update': session_state,
                'is_complete': False
            }

    def get_validation_response(self, emotion: str) -> str:
        """
        Returns a validation statement based on the detected emotion.
        Validation is Level 1-3 in DBT: Paying attention, reflecting back, articulating the unverbalized.
        """
        emotion = emotion.lower()
        templates = {
            'anxiety': [
                "It makes sense that you're feeling anxious given what you're facing.",
                "It sounds like a really overwhelming moment for you.",
                "I hear how tight your chest feels right now. That is a heavy feeling to carry."
            ],
            'sadness': [
                "I'm so sorry you're hurting. It is completely understandable to feel this way.",
                "It sounds like you're carrying a lot of heaviness right now.",
                "Your feelings are valid. This is a tough loss/situation."
            ],
            'anger': [
                "It makes sense to be angry about that. It sounds unfair.",
                "I can hear the frustration in your words. You have a right to feel that way.",
                "It sounds like your boundaries were crossed, and anger is a natural response."
            ],
            'default': [
                "I hear you, and what you're feeling matters.",
                "Thank you for sharing that with me. It sounds difficult.",
                "It's okay to feel this way. I'm here with you."
            ]
        }

        # Simple keyword matching for now (Mocking NLU classification)
        key = 'default'
        if 'anx' in emotion or 'worry' in emotion or 'panic' in emotion:
            key = 'anxiety'
        elif 'sad' in emotion or 'depress' in emotion or 'cry' in emotion:
            key = 'sadness'
        elif 'ang' in emotion or 'mad' in emotion or 'furious' in emotion:
            key = 'anger'

        return random.choice(templates[key])
