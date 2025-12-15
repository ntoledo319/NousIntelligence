from __future__ import annotations
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple
from .event_store import EventStore

Subscriber = Callable[[str, Dict[str, Any]], None]

def _match(pattern: str, topic: str) -> bool:
    pattern = (pattern or "").strip()
    topic = (topic or "").strip()
    if pattern == "*" or pattern == "":
        return True
    if pattern.endswith(".*"):
        base = pattern[:-2]
        return topic == base or topic.startswith(base + ".")
    return pattern == topic

class EventBus:
    """Thread-safe in-process pub/sub bus with optional persistence."""
    def __init__(self, store: Optional[EventStore] = None):
        self.store = store
        self._subs: Dict[str, List[Subscriber]] = {}
        self._lock = threading.RLock()

    def subscribe(self, pattern: str, fn: Subscriber) -> None:
        with self._lock:
            self._subs.setdefault(pattern, []).append(fn)

    def unsubscribe(self, pattern: str, fn: Subscriber) -> None:
        with self._lock:
            if pattern in self._subs and fn in self._subs[pattern]:
                self._subs[pattern].remove(fn)
                if not self._subs[pattern]:
                    del self._subs[pattern]

    def publish(self, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        event_id: Optional[int] = None
        if self.store is not None:
            event_id = self.store.append(topic, payload)

        with self._lock:
            snapshot: List[Tuple[str, List[Subscriber]]] = [
                (pat, list(fns)) for pat, fns in self._subs.items()
            ]

        delivered = 0
        errors: List[Dict[str, Any]] = []
        for pat, fns in snapshot:
            if not _match(pat, topic):
                continue
            for fn in fns:
                try:
                    fn(topic, payload)
                    delivered += 1
                except Exception as e:
                    errors.append({
                        "subscriber": getattr(fn, "__name__", "anonymous"),
                        "error": str(e),
                    })

        return {"ok": True, "event_id": event_id, "delivered": delivered, "errors": errors}

