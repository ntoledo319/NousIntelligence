from __future__ import annotations

from flask_wtf.csrf import CSRFProtect, generate_csrf

def init_csrf(app):
    csrf = CSRFProtect(app)

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    return csrf
