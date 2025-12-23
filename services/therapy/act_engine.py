"""
ACT Engine

Implements Acceptance and Commitment Therapy logic, focusing on
Defusion ("Leaves on a stream") and Mindfulness.
"""

import logging
from typing import Dict, Any
from services.content_service import get_content_service

logger = logging.getLogger(__name__)

class ACTEngine:
    def __init__(self):
        self.content_service = get_content_service()

    def process_mindfulness_exercise(self, exercise_type: str = 'leaves_on_stream') -> Dict[str, str]:
        """
        Returns the script for a mindfulness exercise.
        In a full implementation, this could be a multi-turn voice/text guide.
        """
        content = self.content_service.get_intervention('act', exercise_type)
        if not content:
            return {'error': 'Content not found', 'message': "I couldn't find that exercise."}

        return {
            'title': "Leaves on a Stream",
            'type': 'defusion',
            'script': content.get('text', ''),
            'instruction': "Read this slowly to yourself, or close your eyes and visualize it."
        }
