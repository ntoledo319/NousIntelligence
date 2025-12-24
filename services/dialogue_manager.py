"""
Dialogue Manager
Lightweight state/mode tracker to bridge wellness, task, and crisis flows.
"""

from typing import Dict, List
from services.nlu_service import NLUResult


class DialogueManager:
    """Determines dialogue mode and offers quick replies aligned to state."""

    def determine_mode(self, nlu: NLUResult, context: Dict) -> str:
        if nlu.crisis:
            return "crisis"
        if "task" in nlu.tags or "productivity" in nlu.intents or context.get("mode") == "task":
            return "task"
        return "wellness"

    def quick_replies_for_mode(self, mode: str, locale: str = "en") -> List[str]:
        if mode == "crisis":
            return ["Show crisis numbers", "Ground with me", "Invite someone you trust"]
        if mode == "task":
            return ["Add to my tasks", "Schedule a reminder", "Defer to later"]
        return ["Share how you feel", "Offer a coping skill", "Switch topic"]


dialogue_manager = DialogueManager()

__all__ = ["DialogueManager", "dialogue_manager"]
