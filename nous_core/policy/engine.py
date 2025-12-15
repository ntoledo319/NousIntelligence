from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class Rule:
    id: str
    field: str
    equals: Optional[Any] = None
    contains: Optional[str] = None
    effect: str = "allow"   # "allow" or "deny"
    reason: str = ""

DEFAULT_RULES: List[Rule] = [
    Rule(id="deny_delete_all", field="action", equals="delete_all", effect="deny",
         reason="Hard stop: destructive global action."),
    Rule(id="deny_export_secrets", field="action", contains="export_secret", effect="deny",
         reason="Hard stop: exfiltration patterns."),
]

class PolicyEngine:
    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules = rules or list(DEFAULT_RULES)

    def evaluate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        hits = []
        for r in self.rules:
            v = payload.get(r.field)
            if r.equals is not None and v == r.equals:
                hits.append(r)
            elif r.contains is not None and isinstance(v, str) and r.contains in v:
                hits.append(r)

        denies = [h for h in hits if h.effect == "deny"]
        if denies:
            return {
                "allowed": False,
                "reasons": [{"id": d.id, "reason": d.reason} for d in denies],
            }

        return {"allowed": True, "reasons": [{"id": h.id, "reason": h.reason} for h in hits]}

