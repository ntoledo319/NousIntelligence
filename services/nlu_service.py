"""
NLU Service
Lightweight intent, emotion, language, and crisis detection for chat and therapeutic routing.
"""

import logging
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    from utils.emotion_detection import detect_emotion_from_text
except ImportError:
    detect_emotion_from_text = None


@dataclass
class NLUResult:
    language: str = "en"
    intents: List[str] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)
    emotion: str = "neutral"
    confidence: float = 0.5
    crisis: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    risk_level: str = "low"

    @property
    def primary_intent(self) -> Optional[str]:
        return self.intents[0] if self.intents else None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["primary_intent"] = self.primary_intent
        return data


class NLUService:
    """Simple, fast NLU layer with rule-based fallbacks."""

    def __init__(self):
        self.intent_keywords: Dict[str, List[str]] = {
            "crisis": ["suicide", "kill myself", "self harm", "overdose", "cant go on", "abuso", "violencia", "911", "988", "741741"],
            "cbt": ["thought", "distortion", "cbt", "challenge", "reframe"],
            "dbt": ["dbt", "tipp", "wise mind", "stop skill", "opposite action"],
            "act": ["defusion", "values", "aceptacion", "aceptar", "mindfulness"],
            "grounding": ["ground", "anclaje", "panic", "panico", "ansiedad", "anxiety", "present moment"],
            "behavioral_activation": ["activate", "activation", "motivation", "tarea", "task", "walk", "exercise"],
            "motivational_interviewing": ["motivation", "ambivalence", "confidence", "importancia", "confianza", "cambio"],
            "productivity": ["calendar", "schedule", "reminder", "task", "organize", "agenda"],
            "gratitude": ["gratitude", "gracias", "agradecido"],
        }
        self.spanish_markers = {"que", "como", "estoy", "gracias", "necesito", "quiero", "hola", "usted", "tengo", "siento"}
        self.crisis_keywords = ["suicide", "kill myself", "self harm", "harm myself", "end it", "cant go on", "overdose", "abuse", "assault", "rape", "violence", "hurt myself", "last goodbye"]

    def analyze(self, text: str, user_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> NLUResult:
        """Run intent, language, emotion, and crisis checks."""
        context = context or {}
        lowered = text.lower().strip()

        language = self._detect_language(lowered)
        intents = self._detect_intents(lowered)
        crisis = self._detect_crisis(lowered)
        emotion, confidence = self._detect_emotion(lowered)

        tags = intents.copy()
        if crisis:
            tags.append("crisis")
        if emotion:
            tags.append(emotion)

        risk_level = "high" if crisis else ("medium" if confidence >= 0.65 else "low")
        return NLUResult(
            language=language,
            intents=intents,
            emotion=emotion,
            confidence=confidence,
            crisis=crisis,
            tags=list(dict.fromkeys(tags)),  # dedupe while preserving order
            risk_level=risk_level,
        )

    def _detect_language(self, lowered: str) -> str:
        """Naive language detection for EN/ES."""
        if re.search(r"[ñáéíóú]", lowered):
            return "es"
        tokens = re.findall(r"\b\w+\b", lowered)
        spanish_hits = sum(1 for token in tokens if token in self.spanish_markers)
        return "es" if spanish_hits >= 2 else "en"

    def _detect_intents(self, lowered: str) -> List[str]:
        intents: List[str] = []
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in lowered for keyword in keywords):
                intents.append(intent)
        return intents

    def _detect_crisis(self, lowered: str) -> Optional[Dict[str, Any]]:
        if any(keyword in lowered for keyword in self.crisis_keywords):
            return {"detected": True, "reason": "keyword_match"}
        return None

    def _detect_emotion(self, lowered: str) -> Tuple[str, float]:
        if detect_emotion_from_text:
            try:
                result = detect_emotion_from_text(lowered)
                return result.get("emotion", "neutral"), result.get("confidence", 0.5)
            except Exception as exc:
                logger.error(f"Emotion detection failed, using fallback: {exc}")

        # Fallback heuristic
        emotion_map = {
            "anxious": ["anxious", "nervous", "worried", "panico", "ansioso"],
            "sad": ["sad", "down", "depressed", "triste"],
            "angry": ["angry", "furious", "mad", "enojo"],
            "overwhelmed": ["overwhelmed", "too much", "agotado"],
            "distressed": ["hopeless", "cant go on", "sufrir"],
        }
        for emotion, keywords in emotion_map.items():
            if any(keyword in lowered for keyword in keywords):
                return emotion, 0.6
        return "neutral", 0.5


# Shared singleton
nlu_service = NLUService()

__all__ = ["NLUService", "NLUResult", "nlu_service"]
