"""
Request Validation Middleware - Phase 5.1 Security
Validates incoming requests for security threats
"""
from flask import Flask, request, jsonify, abort
from typing import List, Pattern
import re
import logging

logger = logging.getLogger(__name__)

# Suspicious patterns that might indicate attacks
SUSPICIOUS_PATTERNS: List[Pattern] = [
    re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),  # XSS
    re.compile(r'javascript:', re.IGNORECASE),  # JavaScript protocol
    re.compile(r'on\w+\s*=', re.IGNORECASE),  # Event handlers
    re.compile(r'SELECT.*FROM', re.IGNORECASE),  # SQL injection
    re.compile(r'UNION.*SELECT', re.IGNORECASE),  # SQL injection
    re.compile(r'DROP\s+TABLE', re.IGNORECASE),  # SQL injection
    re.compile(r'\.\./'),  # Path traversal
    re.compile(r'\\x[0-9a-f]{2}', re.IGNORECASE),  # Hex encoding
]

def validate_request_size(app: Flask, max_content_length: int = 10 * 1024 * 1024) -> None:
    """
    Validate request size
    Default: 10MB max
    """
    app.config['MAX_CONTENT_LENGTH'] = max_content_length
    
    @app.before_request
    def check_content_length():
        if request.content_length and request.content_length > max_content_length:
            abort(413, description="Request too large")

def validate_json_requests(app: Flask) -> None:
    """Validate JSON request format"""
    
    @app.before_request
    def validate_json():
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.path.startswith('/api/'):
                if not request.is_json:
                    return jsonify({"error": "Content-Type must be application/json"}), 400

def scan_for_attacks(app: Flask) -> None:
    """Scan requests for common attack patterns"""
    
    @app.before_request
    def scan_request():
        # Skip static files
        if request.path.startswith('/static/'):
            return
        
        # Check query parameters
        for key, value in request.args.items():
            for pattern in SUSPICIOUS_PATTERNS:
                if pattern.search(str(value)):
                    logger.warning(
                        f"Suspicious pattern detected in query param {key}: {value[:50]}"
                    )
                    abort(400, description="Invalid request parameters")
        
        # Check JSON body
        if request.is_json:
            try:
                data = request.get_json()
                if data and isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, str):
                            for pattern in SUSPICIOUS_PATTERNS:
                                if pattern.search(value):
                                    logger.warning(
                                        f"Suspicious pattern detected in JSON field {key}"
                                    )
                                    abort(400, description="Invalid request content")
            except Exception:
                pass

def add_request_validation(app: Flask) -> Flask:
    """Apply all request validation middleware"""
    validate_request_size(app)
    validate_json_requests(app)
    scan_for_attacks(app)
    return app
