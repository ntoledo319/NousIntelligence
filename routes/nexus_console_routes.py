from __future__ import annotations
from flask import Blueprint, render_template
from utils.unified_auth import require_auth

nexus_console_bp = Blueprint("nexus_console", __name__)

@nexus_console_bp.get("/nexus")
@require_auth(allow_demo=True)
def console():
    return render_template("nexus_console.html")
