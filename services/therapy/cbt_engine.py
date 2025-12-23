"""
CBT Engine

Implements the Cognitive Behavioral Therapy logic, specifically the
Thought Record state machine and Behavioral Activation.
"""

import logging
from typing import Dict, Any, Optional
from services.content_service import get_content_service

logger = logging.getLogger(__name__)

class CBTEngine:
    def __init__(self):
        self.content_service = get_content_service()

    def process_thought_record(self, session_state: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """
        Advances the 5-step Thought Record flow based on user input.
        session_state: The 'variables' dict from TherapySession model
        """
        current_step_id = session_state.get('step', 'identify_situation')

        # Load script
        thought_record = self.content_service.get_intervention('cbt', 'thought_record')
        if not thought_record:
            return {'error': 'Content not found', 'message': "I'm having trouble retrieving the exercise."}

        steps = {s['id']: s for s in thought_record['steps']}
        current_step_data = steps.get(current_step_id)

        # Store user input for the *current* step (which they just answered)
        # Note: If this is the very first call, user_input might be the command to start
        if session_state.get('started'):
             session_state[current_step_id] = user_input

             # Move to next
             next_step_id = current_step_data.get('next')
             if next_step_id == 'complete':
                 return self._complete_thought_record(session_state)

             session_state['step'] = next_step_id
             next_prompt = steps[next_step_id]['prompt']

             return {
                 'message': next_prompt,
                 'state_update': session_state,
                 'is_complete': False
             }
        else:
            # Start the flow
            session_state['started'] = True
            session_state['step'] = 'identify_situation'
            return {
                'message': steps['identify_situation']['prompt'],
                'state_update': session_state,
                'is_complete': False
            }

    def _complete_thought_record(self, session_state: Dict[str, Any]) -> Dict[str, Any]:
        """Finalizes the exercise and generates a summary"""

        # Calculate mood shift (if numeric)
        try:
            initial = int(re.search(r'\d+', session_state.get('identify_emotion', '0')).group())
            final = int(re.search(r'\d+', session_state.get('check_emotion', '0')).group())
            improvement = initial - final
        except:
            improvement = None

        summary = (
            f"Great job. You identified that the situation '{session_state.get('identify_situation')}' "
            f"led to the thought '{session_state.get('automatic_thought')}'. "
            f"By examining the evidence, you reframed it to: '{session_state.get('reframe')}'."
        )

        return {
            'message': summary + "\n\nI've saved this thought record to your journal. How are you feeling now?",
            'state_update': session_state,
            'is_complete': True,
            'artifact': {
                'type': 'thought_record',
                'data': session_state
            }
        }

    def get_behavioral_activation_suggestion(self, energy_level: int) -> str:
        """Suggests activities based on energy (1-10)"""
        if energy_level <= 3:
            return "How about something small? Stretching for 2 minutes or drinking a glass of water?"
        elif energy_level <= 6:
            return "Maybe a 10-minute walk or tidying up one small area?"
        else:
            return "You seem to have some energy! How about a workout or tackling a hobby project?"

import re
