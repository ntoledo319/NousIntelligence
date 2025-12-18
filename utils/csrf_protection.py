from __future__ import annotations

from flask_wtf.csrf import CSRFProtect, generate_csrf


def init_csrf(app):
    """
    Initialize CSRF protection.

    In testing mode we keep the context processor for templates but
    skip attaching the CSRF middleware so API tests can exercise JSON
    endpoints (like /api/auth/login) without needing tokens.
    """
    if app.config.get("TESTING"):
        @app.context_processor
        def inject_csrf_token_testing():
            return dict(csrf_token=lambda: "")

        return None

    csrf = CSRFProtect(app)

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    return csrf
