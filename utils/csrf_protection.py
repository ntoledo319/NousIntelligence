from flask_wtf.csrf import CSRFProtect

def init_csrf(app):
    """Initialize CSRF protection"""
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)
