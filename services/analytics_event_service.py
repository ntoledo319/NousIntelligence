"""
Analytics Event Service
Simple logger-based event capture for chat, NLU tags, and safety signals.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional


class AnalyticsEventService:
    def __init__(self, log_path: Optional[str] = None):
        self.log_path = Path(log_path or Path(__file__).resolve().parent.parent / "logs" / "analytics_events.log")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def log_chat_event(self, user_id: Optional[str], payload: Dict[str, Any]) -> None:
        try:
            entry = {
                "user_id": user_id,
                **payload
            }
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as exc:
            self.logger.error(f"Failed to log chat event: {exc}")


analytics_event_service = AnalyticsEventService()

__all__ = ["analytics_event_service", "AnalyticsEventService"]
