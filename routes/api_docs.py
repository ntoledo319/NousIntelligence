"""
API Documentation Routes with Flask-Smorest and OpenAPI 3.1
Comprehensive API documentation and Swagger UI integration
"""

from flask import Flask, Blueprint, jsonify, request, render_template_string
from flask_smorest import Api, Blueprint as SmorestBlueprint
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec.ext.flask import FlaskPlugin
import json
import os

# Create API documentation blueprint
api_docs_bp = Blueprint('api_docs', __name__, url_prefix='/docs')

def create_api_spec():
    """Create OpenAPI 3.1 specification"""
    spec = APISpec(
        title="NOUS Personal Assistant API",
        version="1.0.0",
        openapi_version="3.1.0",
        info=dict(
            description="Comprehensive API for NOUS Personal Assistant - an AI-powered personal assistant platform",
            contact=dict(name="NOUS Team", email="support@nous.ai"),
            license=dict(name="MIT", url="https://opensource.org/licenses/MIT")
        ),
        servers=[
            {"url": "https://nous-personal-assistant.replit.app", "description": "Production server"},
            {"url": "http://localhost:5000", "description": "Development server"}
        ],
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
        tags=[
            {"name": "Authentication", "description": "User authentication and session management"},
            {"name": "Chat", "description": "AI chat interface and conversation handling"},
            {"name": "Health", "description": "System health monitoring and status checks"},
            {"name": "Beta", "description": "Beta testing and feature flag management"},
            {"name": "User", "description": "User profile and settings management"}
        ]
    )
    return spec

def init_api_docs(app):
    """Initialize API documentation with Flask-Smorest"""
    
    # Configure Flask-Smorest
    app.config['API_TITLE'] = 'NOUS Personal Assistant API'
    app.config['API_VERSION'] = 'v1'
    app.config['OPENAPI_VERSION'] = '3.1.0'
    app.config['OPENAPI_URL_PREFIX'] = '/docs'
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/api'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    app.config['OPENAPI_REDOC_PATH'] = '/redoc'
    app.config['OPENAPI_REDOC_URL'] = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'
    
    # Initialize Flask-Smorest API
    api = Api(app)
    
    # Register API documentation blueprint
    app.register_blueprint(api_docs_bp)
    
    return api

@api_docs_bp.route('/')
def docs_index():
    """API Documentation Index"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOUS API Documentation</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 2rem; background: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 0.5rem; }
        .docs-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
        .doc-card { border: 1px solid #e1e8ed; border-radius: 8px; padding: 1.5rem; transition: transform 0.2s, box-shadow 0.2s; }
        .doc-card:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .doc-card h3 { color: #2c3e50; margin-top: 0; }
        .doc-card p { color: #7f8c8d; line-height: 1.6; }
        .btn { display: inline-block; padding: 0.75rem 1.5rem; background: #3498db; color: white; text-decoration: none; border-radius: 4px; transition: background 0.2s; }
        .btn:hover { background: #2980b9; }
        .btn-secondary { background: #95a5a6; }
        .btn-secondary:hover { background: #7f8c8d; }
        .endpoints { margin-top: 2rem; }
        .endpoint { background: #f8f9fa; border-left: 4px solid #3498db; padding: 1rem; margin: 0.5rem 0; border-radius: 0 4px 4px 0; }
        .method { padding: 0.25rem 0.5rem; border-radius: 3px; color: white; font-size: 0.8rem; font-weight: bold; }
        .GET { background: #27ae60; }
        .POST { background: #f39c12; }
        .PUT { background: #8e44ad; }
        .DELETE { background: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 NOUS Personal Assistant API Documentation</h1>
        <p>Welcome to the comprehensive API documentation for NOUS Personal Assistant. This documentation provides detailed information about all available endpoints, request/response formats, and authentication requirements.</p>
        
        <div class="docs-grid">
            <div class="doc-card">
                <h3>📋 Interactive API Explorer</h3>
                <p>Explore and test all API endpoints with our interactive Swagger UI interface. Send real requests and see live responses.</p>
                <a href="/docs/api" class="btn">Open Swagger UI</a>
            </div>
            
            <div class="doc-card">
                <h3>📖 ReDoc Documentation</h3>
                <p>Clean, responsive API documentation with detailed descriptions, examples, and schema information.</p>
                <a href="/docs/redoc" class="btn btn-secondary">View ReDoc</a>
            </div>
            
            <div class="doc-card">
                <h3>🔧 OpenAPI Specification</h3>
                <p>Download the complete OpenAPI 3.1 specification in JSON format for integration with your tools.</p>
                <a href="/docs/openapi.json" class="btn btn-secondary">Download OpenAPI JSON</a>
            </div>
            
            <div class="doc-card">
                <h3>💡 Getting Started Guide</h3>
                <p>Step-by-step guide to authenticate and make your first API calls to the NOUS platform.</p>
                <a href="/docs/getting-started" class="btn btn-secondary">Read Guide</a>
            </div>
        </div>
        
        <div class="endpoints">
            <h2>🔗 Quick Endpoint Reference</h2>
            
            <div class="endpoint">
                <span class="method GET">GET</span> <strong>/api/health</strong> - System health check
            </div>
            
            <div class="endpoint">
                <span class="method POST">POST</span> <strong>/api/chat</strong> - Send chat message to AI assistant
            </div>
            
            <div class="endpoint">
                <span class="method GET">GET</span> <strong>/api/user</strong> - Get current user information
            </div>
            
            <div class="endpoint">
                <span class="method GET">GET</span> <strong>/api/beta/features</strong> - List available beta features
            </div>
            
            <div class="endpoint">
                <span class="method POST">POST</span> <strong>/api/feedback</strong> - Submit user feedback
            </div>
            
            <div class="endpoint">
                <span class="method GET">GET</span> <strong>/healthz</strong> - Kubernetes-style health check
            </div>
        </div>
        
        <div style="margin-top: 2rem; padding: 1rem; background: #e8f4fd; border-radius: 4px;">
            <h3>🔐 Authentication</h3>
            <p>Most endpoints require authentication via Google OAuth. Include your session cookie or OAuth token in requests to protected endpoints.</p>
        </div>
    </div>
</body>
</html>
    """)

@api_docs_bp.route('/getting-started')
def getting_started():
    """Getting Started Guide"""
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Getting Started - NOUS API</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 2rem; background: #f8f9fa; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #2c3e50; }
        pre { background: #f8f9fa; padding: 1rem; border-radius: 4px; overflow-x: auto; border-left: 4px solid #3498db; }
        code { background: #f1f2f6; padding: 0.2rem 0.4rem; border-radius: 3px; font-family: 'Monaco', 'Menlo', monospace; }
        .step { background: #e8f4fd; padding: 1rem; margin: 1rem 0; border-radius: 4px; }
        .note { background: #fff3cd; border: 1px solid #ffeaa7; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Getting Started with NOUS API</h1>
        
        <h2>1. Authentication</h2>
        <p>NOUS uses Google OAuth 2.0 for authentication. You have two options:</p>
        
        <div class="step">
            <h3>Option A: Web Application Flow</h3>
            <p>For web applications, redirect users to:</p>
            <pre>GET /login</pre>
            <p>Users will be redirected to Google OAuth and then back to your application with a session cookie.</p>
        </div>
        
        <div class="step">
            <h3>Option B: Session-based Authentication</h3>
            <p>If you already have a session, include the session cookie in your requests:</p>
            <pre>Cookie: session=your_session_cookie_here</pre>
        </div>
        
        <h2>2. Making Your First Request</h2>
        <p>Test the API with a simple health check:</p>
        
        <pre>curl -X GET "https://nous-personal-assistant.replit.app/api/health" \\
     -H "Accept: application/json"</pre>
        
        <p>Expected response:</p>
        <pre>{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "version": "1.0.0"
}</pre>
        
        <h2>3. Chat with the AI Assistant</h2>
        <p>Send a message to the AI assistant:</p>
        
        <pre>curl -X POST "https://nous-personal-assistant.replit.app/api/chat" \\
     -H "Content-Type: application/json" \\
     -H "Cookie: session=your_session_cookie" \\
     -d '{
       "message": "Hello, what can you help me with?",
       "context": {}
     }'</pre>
        
        <p>Expected response:</p>
        <pre>{
  "success": true,
  "response": "Hello! I'm NOUS, your AI assistant. I can help you with...",
  "intent": "greeting",
  "timestamp": "2025-01-01T12:00:00Z"
}</pre>
        
        <h2>4. Get User Information</h2>
        <p>Retrieve information about the authenticated user:</p>
        
        <pre>curl -X GET "https://nous-personal-assistant.replit.app/api/user" \\
     -H "Accept: application/json" \\
     -H "Cookie: session=your_session_cookie"</pre>
        
        <h2>5. Error Handling</h2>
        <p>The API uses standard HTTP status codes:</p>
        <ul>
            <li><code>200</code> - Success</li>
            <li><code>400</code> - Bad Request</li>
            <li><code>401</code> - Unauthorized</li>
            <li><code>403</code> - Forbidden</li>
            <li><code>404</code> - Not Found</li>
            <li><code>500</code> - Internal Server Error</li>
        </ul>
        
        <p>Error responses include details:</p>
        <pre>{
  "error": "Authentication required",
  "code": "AUTH_REQUIRED",
  "timestamp": "2025-01-01T12:00:00Z"
}</pre>
        
        <div class="note">
            <strong>💡 Pro Tip:</strong> Use the interactive Swagger UI at <a href="/docs/api">/docs/api</a> to test endpoints and see real responses without writing code!
        </div>
        
        <h2>6. Rate Limits</h2>
        <p>API requests are rate-limited to ensure fair usage:</p>
        <ul>
            <li>Chat endpoints: 60 requests per minute</li>
            <li>Other endpoints: 100 requests per minute</li>
        </ul>
        
        <p>Rate limit headers are included in responses:</p>
        <pre>X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200</pre>
        
        <h2>7. Next Steps</h2>
        <ul>
            <li>📋 Explore the <a href="/docs/api">Interactive API Documentation</a></li>
            <li>📖 Read the <a href="/docs/redoc">detailed ReDoc documentation</a></li>
            <li>🔧 Download the <a href="/docs/openapi.json">OpenAPI specification</a></li>
            <li>🏠 Return to the <a href="/docs">main documentation</a></li>
        </ul>
    </div>
</body>
</html>
    """)

@api_docs_bp.route('/openapi.json')
def openapi_spec():
    """Serve OpenAPI specification as JSON"""
    spec = create_api_spec()
    
    # Add paths manually since we can't use decorators in this simple setup
    paths = {
        "/api/health": {
            "get": {
                "tags": ["Health"],
                "summary": "System health check",
                "description": "Check the overall health and status of the NOUS system",
                "responses": {
                    "200": {
                        "description": "System is healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "healthy"},
                                        "timestamp": {"type": "string", "format": "date-time"},
                                        "version": {"type": "string", "example": "1.0.0"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/chat": {
            "post": {
                "tags": ["Chat"],
                "summary": "Send message to AI assistant",
                "description": "Send a message to the NOUS AI assistant and receive an intelligent response",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["message"],
                                "properties": {
                                    "message": {"type": "string", "description": "The message to send to the AI assistant"},
                                    "context": {"type": "object", "description": "Additional context for the conversation"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful response from AI assistant",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "response": {"type": "string"},
                                        "intent": {"type": "string"},
                                        "timestamp": {"type": "string", "format": "date-time"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Authentication required"
                    }
                },
                "security": [{"cookieAuth": []}]
            }
        },
        "/api/user": {
            "get": {
                "tags": ["User"],
                "summary": "Get current user information",
                "description": "Retrieve information about the currently authenticated user",
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
                                        "name": {"type": "string"},
                                        "authenticated": {"type": "boolean"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Authentication required"
                    }
                },
                "security": [{"cookieAuth": []}]
            }
        },
        "/healthz": {
            "get": {
                "tags": ["Health"],
                "summary": "Kubernetes-style health check",
                "description": "Simple health check endpoint for Kubernetes and load balancers",
                "responses": {
                    "200": {
                        "description": "Service is healthy",
                        "content": {
                            "text/plain": {
                                "schema": {"type": "string", "example": "OK"}
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Add security schemes
    components = {
        "securitySchemes": {
            "cookieAuth": {
                "type": "apiKey",
                "in": "cookie",
                "name": "session",
                "description": "Session cookie from Google OAuth authentication"
            }
        }
    }
    
    spec_dict = spec.to_dict()
    spec_dict['paths'] = paths
    spec_dict['components'] = components
    
    return jsonify(spec_dict)