from __future__ import annotations
import time
import requests
from flask import Blueprint, jsonify, request, current_app

from utils.unified_auth import require_auth
from services.nexus.pipeline import run_nexus
from services.runtime_service import init_runtime

nexus_bp = Blueprint("nexus", __name__)

@nexus_bp.post("/nexus/chat")
@require_auth(allow_demo=True)
def nexus_chat():
    d = request.get_json(force=True, silent=False) or {}
    msg = (d.get("message") or "").strip()
    if not msg:
        return jsonify({"ok": False, "error": "message required"}), 400

    res = run_nexus(msg, context={"ip": request.remote_addr})
    return jsonify({"ok": res.ok, "response": res.response, "meta": res.meta})

@nexus_bp.post("/nexus/ingest")
@require_auth(allow_demo=True)
def nexus_ingest():
    d = request.get_json(force=True, silent=False) or {}
    doc_id = (d.get("doc_id") or "").strip()
    text = (d.get("text") or "").strip()
    if not doc_id or not text:
        return jsonify({"ok": False, "error": "doc_id and text required"}), 400

    rt = init_runtime(current_app)
    out = rt["graph"].ingest_text(doc_id, text, meta={"source": "api"})
    # Also store semantically
    try:
        rt["semantic"].upsert(doc_id, text, {"kind": "ingested"})
    except Exception:
        pass
    return jsonify({"ok": True, "graph": out})

@nexus_bp.get("/nexus/graph")
@require_auth(allow_demo=True)
def nexus_graph():
    node = (request.args.get("node") or "").strip()
    if not node:
        return jsonify({"ok": False, "error": "node required"}), 400
    rt = init_runtime(current_app)
    return jsonify({"ok": True, "data": rt["graph"].neighborhood(node, limit=int(request.args.get("limit", "50")))})

# ── Free Integration #1: Crossref ─────────────────────────────────────
@nexus_bp.get("/research/crossref")
@require_auth(allow_demo=True)
def research_crossref():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"ok": True, "items": []})
    url = "https://api.crossref.org/works"
    r = requests.get(url, params={"query": q, "rows": 5}, timeout=12)
    r.raise_for_status()
    j = r.json()
    items = (j.get("message") or {}).get("items") or []

    # store into semantic memory (best-effort)
    rt = init_runtime(current_app)
    for it in items[:5]:
        title = (it.get("title") or [""])[0]
        doi = it.get("DOI") or ""
        text = f"{title}\nDOI: {doi}\n"
        rt["semantic"].upsert(f"crossref:{doi or time.time()}", text, {"kind": "crossref", "q": q})
    return jsonify({"ok": True, "items": items})

# ── Free Integration #2: OpenLibrary ──────────────────────────────────
@nexus_bp.get("/library/search")
@require_auth(allow_demo=True)
def library_search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify({"ok": True, "docs": []})
    url = "https://openlibrary.org/search.json"
    r = requests.get(url, params={"q": q, "limit": 5}, timeout=12)
    r.raise_for_status()
    j = r.json()
    docs = j.get("docs") or []

    rt = init_runtime(current_app)
    for d in docs[:5]:
        title = d.get("title") or ""
        author = (d.get("author_name") or [""])[0] if isinstance(d.get("author_name"), list) else ""
        key = d.get("key") or str(time.time())
        rt["semantic"].upsert(f"openlibrary:{key}", f"{title}\n{author}", {"kind": "openlibrary", "q": q})
    return jsonify({"ok": True, "docs": docs})

@nexus_bp.post("/workflows/daily_reset")
@require_auth(allow_demo=True)
def workflows_daily_reset():
    from services.workflows.daily import run_daily_workflow
    return jsonify({"ok": True, "result": run_daily_workflow()})
