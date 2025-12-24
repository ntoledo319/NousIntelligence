"""
Therapeutic Content Service
Structured retrieval layer for clinically-reviewed content (EN/ES) with tags, metadata, and safety fallbacks.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TherapeuticContentService:
    """Loads and serves therapeutic content entries with locale-aware fallbacks."""

    def __init__(self, base_path: Optional[str] = None, default_locale: str = "en"):
        self.base_path = Path(base_path or Path(__file__).resolve().parent.parent / "content" / "therapeutic")
        self.default_locale = default_locale
        self.cache: Dict[str, List[Dict[str, Any]]] = {}
        self.metadata_index: Dict[str, Dict[str, Any]] = {}
        self.refresh()

    def refresh(self) -> None:
        """Reload content from disk."""
        self.cache = {}
        self.metadata_index = {}
        if not self.base_path.exists():
            logger.warning(f"Therapeutic content path missing: {self.base_path}")
            return

        for path in self.base_path.rglob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                entries = data if isinstance(data, list) else data.get("items", [])
                for entry in entries:
                    locale = entry.get("locale", self.default_locale)
                    self.cache.setdefault(locale, []).append(entry)
                    self.metadata_index[entry.get("id", str(path))] = entry.get("metadata", {})
            except Exception as exc:
                logger.error(f"Failed loading therapeutic content from {path}: {exc}")

        # Ensure default locale key exists
        self.cache.setdefault(self.default_locale, [])

    def list_content(self, locale: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return all content entries for a locale."""
        locale_key = locale or self.default_locale
        return self.cache.get(locale_key, [])

    def get_content(
        self,
        tags: Optional[List[str]] = None,
        locale: Optional[str] = None,
        intent: Optional[str] = None,
        emotion: Optional[str] = None,
        limit: int = 3,
        crisis_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Retrieve ranked content for the given tags/intent/emotion."""
        locale_key = locale or self.default_locale
        entries = self.cache.get(locale_key, [])

        # Fallback to default locale if requested locale is empty
        if not entries and locale_key != self.default_locale:
            entries = self.cache.get(self.default_locale, [])

        scored: List[Dict[str, Any]] = []
        tag_set = set(t.lower() for t in (tags or []) if t)
        for entry in entries:
            if crisis_only and not entry.get("safety", {}).get("crisis"):
                continue
            entry_tags = set(t.lower() for t in entry.get("tags", []))
            score = self._score_entry(entry_tags, tag_set, intent, emotion, entry)
            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [entry for _, entry in scored[:limit]]

    def get_by_id(self, content_id: str, locale: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Lookup content entry by id with locale fallback"""
        locale_key = locale or self.default_locale
        candidates = self.cache.get(locale_key, []) + self.cache.get(self.default_locale, [])
        for entry in candidates:
            if entry.get("id") == content_id:
                return entry
        return None

    def get_best_content(
        self,
        tags: Optional[List[str]] = None,
        locale: Optional[str] = None,
        intent: Optional[str] = None,
        emotion: Optional[str] = None,
        crisis_only: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Convenience helper to fetch the top ranked entry."""
        results = self.get_content(tags=tags, locale=locale, intent=intent, emotion=emotion, crisis_only=crisis_only, limit=1)
        return results[0] if results else None

    def get_fallback_template(self, locale: Optional[str] = None) -> Dict[str, Any]:
        """Provide a safe fallback template when no entry matches."""
        locale_key = locale or self.default_locale
        boundary = "No soy terapeuta, pero puedo apoyar con pasos de autocuidado." if locale_key.startswith("es") else "I'm not a therapist, but I can support with self-care steps."
        return {
            "title": "Supportive check-in",
            "summary": boundary,
            "steps": [
                "Take one slow breath: in for 4, out for 6.",
                "Name what you are feeling right now.",
                "Would you like grounding, problem solving, or to save this for later?"
            ],
            "quick_replies": ["Guide grounding", "Offer coping ideas", "Save for later"],
            "safety": {"crisis": False, "not_medical": True},
        }

    def _score_entry(
        self,
        entry_tags: set,
        requested_tags: set,
        intent: Optional[str],
        emotion: Optional[str],
        entry: Dict[str, Any],
    ) -> int:
        """Score an entry against requested metadata."""
        score = 0
        if requested_tags:
            overlap = entry_tags.intersection(requested_tags)
            score += len(overlap) * 10
        if intent and intent.lower() in entry_tags:
            score += 8
        if emotion and emotion.lower() in entry_tags:
            score += 5
        if entry.get("safety", {}).get("crisis"):
            score += 1  # keep crisis items ranked but still allow other sorting
        return score


# Shared instance for reuse
therapeutic_content_service = TherapeuticContentService()

__all__ = ["TherapeuticContentService", "therapeutic_content_service"]
