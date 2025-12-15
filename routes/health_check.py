from __future__ import annotations
import time
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.get("/health")
def health():
    return jsonify({"ok": True, "status": "healthy", "ts": time.time()})

@health_bp.get("/healthz")
def healthz():
    return jsonify({"ok": True, "status": "ready", "ts": time.time()})
