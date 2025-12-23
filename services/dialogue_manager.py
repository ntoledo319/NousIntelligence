"""
Dialogue Manager

The central orchestrator of the system.
Routes messages between Safety, Therapy Engines, Task Tools, and Generative Chat.
Manages persistent state across requests.
"""

import logging
from typing import Any, Dict

from models.database import db
from models.therapeutic import TherapySession
from models.user import User
from services.content_service import get_content_service
from services.llm_service import LLMService
from services.personalization_service import PersonalizationService
from services.safety_service import SafetyService
from services.therapy.act_engine import ACTEngine
from services.therapy.cbt_engine import CBTEngine
from services.therapy.dbt_engine import DBTEngine

logger = logging.getLogger(__name__)

class DialogueManager:
    def __init__(self):
        self.safety = SafetyService()
        self.personalization = PersonalizationService()
        self.llm = LLMService()
        self.content = get_content_service()

        # Engines
        self.cbt = CBTEngine()
        self.dbt = DBTEngine()
        self.act = ACTEngine()

    def process_message(self, user_id: int, message: str) -> Dict[str, Any]:
        """
        Main entry point for processing user messages.
        Returns a structured response object.
        """
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}

        # 1. Safety Check (High Priority)
        risk_level = self.safety.analyze_risk_level(message)
        if risk_level != 'safe':
            logger.warning(f"Crisis detected: {risk_level} for user {user_id}")
            protocol = self.safety.get_safety_protocol(risk_level, user)
            return {
                'type': 'crisis',
                'text': protocol['message'],
                'resources': protocol['resources'],
                'suggested_actions': [{'label': r['name'], 'action': 'call', 'value': r.get('phone')} for r in protocol['resources']]
            }

        # 2. State Check (Is user in an active exercise?)
        active_session = TherapySession.query.filter_by(user_id=user_id, is_active=True).first()
        if active_session:
            return self._continue_session(active_session, message)

        # 3. Intent Classification (Simple Rule-based for now, extensible to NLU)
        intent = self._classify_intent(message)

        # 4. Routing
        if intent == 'therapy_cbt':
            return self._start_session(user_id, 'cbt_thought_record')
        elif intent == 'therapy_dbt':
            return self._start_session(user_id, 'dbt_tipp')
        elif intent == 'task_calendar':
            return self._handle_task(user_id, 'calendar')
        elif intent == 'task_weather':
            return self._handle_task(user_id, 'weather')
        else:
            # Default: Generative Chat / Empathy
            context = self.personalization.get_user_context(user_id)
            response_text = self.llm.generate_response(message, context)

            # Analyze sentiment for tracking
            sentiment = self.personalization.detect_sentiment(message)
            # If negative sentiment, maybe suggest an exercise?
            actions = []
            if sentiment['polarity'] < -0.3:
                 actions.append({'label': 'Try a Thought Record', 'action': 'start_cbt'})
                 actions.append({'label': 'Calm Down (TIPP)', 'action': 'start_dbt'})

            return {
                'type': 'chat',
                'text': response_text,
                'suggested_actions': actions
            }

    def _classify_intent(self, message: str) -> str:
        """Determines user intent from text"""
        m = message.lower()
        if 'thought record' in m or 'challenge thought' in m:
            return 'therapy_cbt'
        if 'tipp' in m or 'panic' in m or 'calm down' in m:
            return 'therapy_dbt'
        if 'calendar' in m or 'schedule' in m:
            return 'task_calendar'
        if 'weather' in m:
            return 'task_weather'
        return 'chat'

    def _start_session(self, user_id: int, module_id: str) -> Dict[str, Any]:
        """Initializes a new therapy session"""
        # Deactivate any old sessions
        existing = TherapySession.query.filter_by(user_id=user_id, is_active=True).all()
        for s in existing:
            s.is_active = False

        # Create new
        session = TherapySession(user_id=user_id, module_id=module_id, is_active=True)
        session.variables = {'started': False} # Initialize state
        db.session.add(session)
        db.session.commit()

        # Immediate first step
        return self._continue_session(session, "START")

    def _continue_session(self, session: TherapySession, user_input: str) -> Dict[str, Any]:
        """Advances an active session"""
        from sqlalchemy.orm.attributes import flag_modified

        # Route to appropriate engine
        response = {}
        # Pass a copy to avoid in-place mutation issues before reassignment
        current_vars = dict(session.variables) if session.variables else {}

        if session.module_id == 'cbt_thought_record':
            response = self.cbt.process_thought_record(current_vars, user_input)
        elif session.module_id == 'dbt_tipp':
            response = self.dbt.process_tipp_skill(current_vars, user_input)
        else:
            # Fallback error
            session.is_active = False
            db.session.commit()
            return {'type': 'error', 'text': "Unknown therapy module."}

        if response.get('error'):
             return {'type': 'error', 'text': response['message']}

        # Update DB State
        session.variables = response.get('state_update', session.variables)
        flag_modified(session, "variables") # Ensure SQLAlchemy tracks the JSON change

        if response.get('is_complete'):
            session.is_active = False
            # Log completion?

        db.session.commit()

        return {
            'type': 'therapy_interaction',
            'text': response['message'],
            'module': session.module_id,
            'step': session.variables.get('step'),
            'suggested_actions': [] if response.get('is_complete') else [{'label': 'Next', 'action': 'reply'}]
        }

    def _handle_task(self, user_id: int, task_type: str) -> Dict[str, Any]:
        """Mock Task Handler"""
        if task_type == 'calendar':
             return {
                 'type': 'task_result',
                 'text': "I checked your calendar. You have 'Doctor Appointment' at 3 PM and 'Team Meeting' at 10 AM tomorrow."
             }
        elif task_type == 'weather':
             return {
                 'type': 'task_result',
                 'text': "It's currently 72°F and sunny. A great day for a walk!"
             }
        return {'type': 'chat', 'text': "I'm not sure how to help with that task yet."}
