"""
API Documentation Routes
Provides simplified OpenAPI/Swagger documentation for all API endpoints
"""

from flask import Blueprint, render_template, jsonify, current_app
import json
import os

# Create simplified API docs blueprint
api_docs_bp = Blueprint('api_docs', __name__, url_prefix='/api/docs')

# OpenAPI specification template
OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "NOUS Personal Assistant API",
        "description": "Comprehensive API for the NOUS Personal Assistant application",
        "version": "1.0.0",
        "contact": {
            "email": "support@nous-assistant.com"
        }
    },
    "servers": [
        {
            "url": "/api/v1",
            "description": "Primary API server"
        }
    ],
    "paths": {
        "/api/v1/chat": {
            "post": {
                "summary": "Chat with AI Assistant",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "message": {
                                        "type": "string", 
                                        "description": "User message"
                                    }
                                },
                                "required": ["message"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "response": {"type": "string"},
                                        "status": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/v1/user": {
            "get": {
                "summary": "Get current user information",
                "responses": {
                    "200": {
                        "description": "User information",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "email": {"type": "string"},
                                        "name": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/v1/health": {
            "get": {
                "summary": "Health check endpoint",
                "responses": {
                    "200": {
                        "description": "System health status",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "timestamp": {"type": "string"},
                                        "database": {"type": "object"},
                                        "services": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "schemas": {
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Unique user identifier"},
                    "email": {"type": "string", "format": "email"},
                    "name": {"type": "string"},
                    "is_active": {"type": "boolean"},
                    "created_at": {"type": "string", "format": "date-time"}
                }
            },
            "ChatMessage": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "minLength": 1, "maxLength": 2000},
                    "context": {"type": "object"}
                },
                "required": ["message"]
            },
            "ChatResponse": {
                "type": "object", 
                "properties": {
                    "response": {"type": "string"},
                    "context": {"type": "object"},
                    "metadata": {"type": "object"},
                    "status": {"type": "string"}
                }
            }
        }
    }
}

@api_docs_bp.route('/')
def api_docs_index():
    """API Documentation index page with Swagger UI."""
    return render_template('api_docs/index.html', spec_url='/api/docs/openapi.json')

@api_docs_bp.route('/openapi.json')
def openapi_spec():
    """Return OpenAPI specification as JSON."""
    return jsonify(OPENAPI_SPEC)

@api_docs_bp.route('/endpoints')
def list_endpoints():
    """List all available API endpoints."""
    endpoints = []
    
    if current_app:
        for rule in current_app.url_map.iter_rules():
            if rule.rule.startswith('/api/'):
                endpoints.append({
                    'endpoint': rule.rule,
                    'methods': list((rule.methods or set()) - {'HEAD', 'OPTIONS'}),
                    'function': rule.endpoint
                })
    
    return jsonify({
        'endpoints': endpoints,
        'total_count': len(endpoints)
    })

@api_docs_bp.route('/health')
def docs_health():
    """API documentation health check."""
    return jsonify({
        'status': 'healthy',
        'documentation': 'available',
        'endpoints_documented': len(OPENAPI_SPEC['paths']),
        'schemas_defined': len(OPENAPI_SPEC['components']['schemas'])
    })