from __future__ import annotations
from typing import Any, Dict
from flask import Blueprint, jsonify, request, current_app
from utils.unified_auth import require_auth

search_bp = Blueprint("search", __name__)

@search_bp.get("/search")
@require_auth(allow_demo=True)
def search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"ok": True, "results": []})

    # Prefer nous_core semantic index if available
    try:
        from services.runtime_service import init_runtime
        rt = init_runtime(current_app)
        results = rt["semantic"].search(q, top_k=10)
        return jsonify({"ok": True, "results": results})
    except Exception:
        # Fallback keyword result
        return jsonify({"ok": True, "results": [{"doc_id": "fallback", "score": 1.0, "text": q, "meta": {"mode": "keyword"}}]})
