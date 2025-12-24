"""
Personalization Service
Lightweight preference and helpfulness tracker to recommend content/skills.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PersonalizationService:
    """Stores simple per-user helpfulness signals and preferences."""

    def __init__(self, cache_path: Optional[str] = None):
        self.cache_path = Path(cache_path or Path(__file__).resolve().parent.parent / "cache" / "personalization_feedback.json")
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.cache_path.exists():
            try:
                self._data = json.loads(self.cache_path.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.error(f"Failed to load personalization cache: {exc}")
                self._data = {}

    def _save(self) -> None:
        try:
            self.cache_path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.error(f"Failed to save personalization cache: {exc}")

    def get_preferences(self, user_id: Optional[str]) -> Dict[str, Any]:
        if not user_id:
            return {}
        return self._data.get(str(user_id), {}).get("preferences", {})

    def record_feedback(
        self,
        user_id: Optional[str],
        content_id: Optional[str],
        tags: List[str],
        helpful: Optional[bool] = None,
        locale: str = "en",
    ) -> None:
        if not user_id or not content_id:
            return

        user_key = str(user_id)
        self._data.setdefault(user_key, {"feedback": [], "preferences": {}})
        self._data[user_key]["feedback"].append({
            "content_id": content_id,
            "tags": tags,
            "helpful": helpful,
            "locale": locale
        })
        self._save()

    def recommend_tags(self, user_id: Optional[str], limit: int = 3) -> List[str]:
        if not user_id:
            return []
        feedback = self._data.get(str(user_id), {}).get("feedback", [])
        tag_counts: Dict[str, int] = {}
        for item in feedback:
            for tag in item.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        sorted_tags = sorted(tag_counts.items(), key=lambda kv: kv[1], reverse=True)
        return [tag for tag, _ in sorted_tags[:limit]]

    def set_preference(self, user_id: Optional[str], key: str, value: Any) -> None:
        if not user_id:
            return
        user_key = str(user_id)
        self._data.setdefault(user_key, {"feedback": [], "preferences": {}})
        self._data[user_key]["preferences"][key] = value
        self._save()


personalization_service = PersonalizationService()

__all__ = ["PersonalizationService", "personalization_service"]
