"""
LLM Service

Handles interactions with Large Language Models (Generative AI).
Implements the "Therapist Persona" constraints and Safety Guardrails.
Supports fallback to a Mock LLM if external APIs are unavailable.
"""

import logging
import os
import json
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# System Prompt enforcing the persona defined in the PDF
SYSTEM_PROMPT = """
You are a supportive, therapeutically-informed AI assistant named NOUS.
You are NOT a licensed therapist and cannot diagnose or treat medical conditions.
Your goal is to provide empathetic support, coaching, and evidence-based tools (CBT, DBT, ACT).

Key Guidelines:
1. Empathy First: Always validate the user's feelings before problem-solving.
2. Boundaries: If a user asks for medical advice, clarify your role and suggest a professional.
3. Style: Warm, non-judgmental, collaborative. Use open-ended questions.
4. Safety: If you detect self-harm or abuse, stop and provide crisis resources immediately.

Context about the user:
{user_context}
"""

class LLMService:
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.model = None
        self._init_model()

    def _init_model(self):
        """Initialize Google Gemini or other models if available"""
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Generative AI model initialized (Gemini)")
            except Exception as e:
                logger.error(f"Failed to init Gemini: {e}")
                self.model = None
        else:
            logger.warning("No GOOGLE_API_KEY found. Using Mock LLM.")

    def generate_response(self, user_input: str, user_context: Dict[str, Any]) -> str:
        """
        Generates a response using the LLM or Mock fallback.
        """
        # Format context string
        context_str = json.dumps(user_context, indent=2)
        full_prompt = SYSTEM_PROMPT.format(user_context=context_str)

        if self.model:
            try:
                # ChatSession could be maintained here for multi-turn history
                # For now, we do single-turn with context injection
                chat = self.model.start_chat(history=[])
                # Send system prompt implicit instruction + user input
                combined_input = f"{full_prompt}\n\nUser: {user_input}"
                response = chat.send_message(combined_input)
                return response.text
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                return self._mock_response(user_input)
        else:
            return self._mock_response(user_input)

    def _mock_response(self, user_input: str) -> str:
        """Fallback responses for testing/offline mode"""
        input_lower = user_input.lower()

        if "sad" in input_lower or "depressed" in input_lower:
            return "I'm sorry to hear you're feeling down. It sounds like a heavy weight to carry. Would you like to try a small coping exercise?"
        elif "anxious" in input_lower or "worry" in input_lower:
            return "It makes sense that you're feeling anxious. Uncertainty is really hard. Shall we take a few deep breaths together?"
        elif "thank" in input_lower:
            return "You're very welcome. I'm here whenever you need support."
        else:
            return "I hear you. Could you tell me a bit more about what's on your mind?"
