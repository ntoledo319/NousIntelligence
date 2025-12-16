from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from flask import current_app

# Core runtime
from services.runtime_service import init_runtime

# Existing systems (already in repo)
try:
    from core.chat.dispatcher import ChatDispatcher
except Exception:
    ChatDispatcher = None  # type: ignore

try:
    from utils.plugin_registry import PluginRegistry
except Exception:
    PluginRegistry = None  # type: ignore

from nous_core.quality import score as quality_score


@dataclass
class NexusResult:
    ok: bool
    response: str
    meta: Dict[str, Any]


def _safe_str(x: Any) -> str:
    try:
        return str(x)
    except Exception:
        return repr(x)


def _policy_check(rt: Dict[str, Any], payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    try:
        res = rt["policy"].evaluate(payload)
        return bool(res.get("allowed", True)), res
    except Exception as e:
        return True, {"allowed": True, "warning": _safe_str(e)}


def _store_memory(rt: Dict[str, Any], kind: str, text: str, meta: Dict[str, Any]) -> None:
    ts = time.time()
    rt["store"].append(f"nexus.{kind}", {"text": text, "meta": meta, "ts": ts})
    # Semantic upsert for retrieval
    try:
        rt["semantic"].upsert(f"nexus:{kind}:{ts}", text, {"kind": kind, **meta})
    except Exception:
        pass


def run_nexus(message: str, context: Optional[Dict[str, Any]] = None) -> NexusResult:
    """
    The unified execution pipeline:
    message -> policy -> router -> response -> quality gate -> memory
    """
    context = context or {}
    rt = init_runtime(current_app)

    # 1) Policy gate input
    allowed, pol = _policy_check(rt, {"action": "nexus_chat", "message": message})
    if not allowed:
        return NexusResult(ok=False, response="Denied by policy.", meta={"policy": pol})

    # 2) Route using existing ChatDispatcher if available
    routed = None
    if ChatDispatcher is not None:
        try:
            # ChatDispatcher is async; run in a tiny event loop if needed.
            import asyncio
            disp = ChatDispatcher()
            routed = asyncio.run(disp.dispatch(message, context))
        except Exception as e:
            routed = {"success": False, "error": _safe_str(e), "type": "dispatcher_error"}

    # 3) Tool/plugin assist (optional)
    plugins = None
    if PluginRegistry is not None:
        try:
            reg = PluginRegistry()
            plugins = {k: v.status.value for k, v in reg.plugins.items()}  # type: ignore[attr-defined]
        except Exception:
            plugins = None

    # 4) Compose response deterministically if routed isn't usable
    if isinstance(routed, dict) and routed.get("success") and routed.get("response"):
        resp_text = _safe_str(routed["response"])
        handler = routed.get("handler", "unknown")
    else:
        handler = "fallback"
        resp_text = f"✅ NOUS NEXUS heard you: {_safe_str(message).strip()}"

    # 5) Quality gate (score + issues)
    q = quality_score(resp_text)

    # 6) Store memory
    _store_memory(rt, "user", message, {"source": "nexus"})
    _store_memory(rt, "assistant", resp_text, {"source": "nexus", "handler": handler, "quality": q})

    return NexusResult(
        ok=True,
        response=resp_text,
        meta={
            "handler": handler,
            "quality": q,
            "policy": pol,
            "plugins": plugins,
            "routed": routed if isinstance(routed, dict) else None,
        },
    )
