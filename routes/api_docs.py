"""
API Documentation Routes
Provides OpenAPI/Swagger documentation for all API endpoints
"""

from flask import Blueprint, render_template, jsonify
from flask_smorest import Api, Blueprint as SmorestBlueprint
from marshmallow import Schema, fields, validate
import json
import os

# Create Flask-Smorest API instance
api_docs_bp = Blueprint('api_docs', __name__, url_prefix='/api/docs')

# Marshmallow schemas for API documentation
class UserSchema(Schema):
    """User model schema for API documentation."""
    id = fields.Str(required=True, description="Unique user identifier")
    email = fields.Email(required=True, description="User email address")
    name = fields.Str(description="User display name")
    is_active = fields.Bool(description="Whether user account is active")
    created_at = fields.DateTime(description="Account creation timestamp")
    last_login = fields.DateTime(description="Last login timestamp")

class ChatMessageSchema(Schema):
    """Chat message schema for API requests."""
    message = fields.Str(required=True, validate=validate.Length(min=1, max=2000),
                         description="User message content")
    context = fields.Dict(description="Optional conversation context")

class ChatResponseSchema(Schema):
    """Chat response schema for API responses."""
    response = fields.Str(required=True, description="AI-generated response")
    context = fields.Dict(description="Updated conversation context")
    metadata = fields.Dict(description="Response metadata (model, tokens, etc.)")
    status = fields.Str(required=True, description="Response status")

class FeedbackSchema(Schema):
    """User feedback schema."""
    type = fields.Str(validate=validate.OneOf(['bug_report', 'feature_request', 'general']),
                      description="Type of feedback")
    message = fields.Str(required=True, validate=validate.Length(min=1, max=1000),
                         description="Feedback message")
    rating = fields.Int(validate=validate.Range(min=1, max=5),
                        description="User rating (1-5)")
    metadata = fields.Dict(description="Additional feedback metadata")

class HealthCheckSchema(Schema):
    """Health check response schema."""
    status = fields.Str(required=True, description="Overall system status")
    timestamp = fields.DateTime(required=True, description="Health check timestamp")
    database = fields.Dict(description="Database connectivity status")
    external_services = fields.Dict(description="External service status")
    system = fields.Dict(description="System resource metrics")

class FeatureFlagSchema(Schema):
    """Feature flag schema."""
    id = fields.Str(required=True, description="Feature flag identifier")
    name = fields.Str(required=True, description="Feature flag name")
    description = fields.Str(description="Feature flag description")
    enabled = fields.Bool(required=True, description="Whether flag is enabled")
    rollout_percentage = fields.Int(validate=validate.Range(min=0, max=100),
                                   description="Rollout percentage (0-100)")
    target_users = fields.List(fields.Str(), description="Targeted user IDs")

class ErrorSchema(Schema):
    """Standard error response schema."""
    error = fields.Dict(required=True, description="Error details")
    status = fields.Str(required=True, description="Error status")
    timestamp = fields.DateTime(required=True, description="Error timestamp")

# OpenAPI specification
OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "NOUS Personal Assistant API",
        "description": """
# NOUS Personal Assistant API

A comprehensive API for the NOUS Personal Assistant platform, providing AI-powered 
chat functionality, user management, health monitoring, and beta testing features.

## Authentication

Most endpoints require Google OAuth authentication. Include session cookies or 
authorization headers as appropriate.

## Rate Limiting

- Chat API: 100 requests per hour per user
- Health endpoints: 1000 requests per hour per IP
- Admin APIs: 50 requests per hour per admin user

## Error Handling

All endpoints return standardized error responses with appropriate HTTP status codes.
        """,
        "version": "1.0.0",
        "contact": {
            "name": "NOUS Development Team",
            "url": "https://github.com/your-repo/nous-personal-assistant"
        },
        "license": {
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "servers": [
        {
            "url": "/api",
            "description": "API base path"
        }
    ],
    "paths": {
        "/chat": {
            "post": {
                "summary": "Send chat message",
                "description": "Send a message to the AI chat system and receive a response",
                "tags": ["Chat"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ChatMessage"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful chat response",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ChatResponse"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid request",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        }
                    },
                    "429": {
                        "description": "Rate limit exceeded",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        }
                    }
                }
            }
        },
        "/user": {
            "get": {
                "summary": "Get current user",
                "description": "Retrieve information about the currently authenticated user",
                "tags": ["User Management"],
                "responses": {
                    "200": {
                        "description": "User information",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {"$ref": "#/components/schemas/User"},
                                        "status": {"type": "string", "example": "success"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Not authenticated",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        }
                    }
                }
            }
        },
        "/health": {
            "get": {
                "summary": "Basic health check",
                "description": "Check basic application health status",
                "tags": ["Health Monitoring"],
                "responses": {
                    "200": {
                        "description": "Health status",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealthCheck"}
                            }
                        }
                    }
                }
            }
        },
        "/healthz": {
            "get": {
                "summary": "Comprehensive health check",
                "description": "Detailed system health including database and external services",
                "tags": ["Health Monitoring"],
                "responses": {
                    "200": {
                        "description": "Detailed health status",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealthCheck"}
                            }
                        }
                    },
                    "503": {
                        "description": "System unhealthy",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealthCheck"}
                            }
                        }
                    }
                }
            }
        },
        "/feedback": {
            "post": {
                "summary": "Submit feedback",
                "description": "Submit user feedback for analysis and improvement",
                "tags": ["User Feedback"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Feedback"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Feedback submitted successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string", "description": "Feedback ID"}
                                            }
                                        },
                                        "status": {"type": "string", "example": "success"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid feedback data",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        }
                    }
                }
            }
        },
        "/beta/flags": {
            "get": {
                "summary": "List feature flags",
                "description": "Get all feature flags (admin only)",
                "tags": ["Beta Management"],
                "security": [{"AdminAuth": []}],
                "responses": {
                    "200": {
                        "description": "Feature flags list",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/FeatureFlag"}
                                        },
                                        "status": {"type": "string", "example": "success"}
                                    }
                                }
                            }
                        }
                    },
                    "403": {
                        "description": "Insufficient permissions",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "schemas": {
            "User": UserSchema().fields,
            "ChatMessage": ChatMessageSchema().fields,
            "ChatResponse": ChatResponseSchema().fields,
            "Feedback": FeedbackSchema().fields,
            "HealthCheck": HealthCheckSchema().fields,
            "FeatureFlag": FeatureFlagSchema().fields,
            "Error": ErrorSchema().fields
        },
        "securitySchemes": {
            "AdminAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "Admin authentication required"
            }
        }
    },
    "tags": [
        {
            "name": "Chat",
            "description": "AI chat functionality"
        },
        {
            "name": "User Management",
            "description": "User account management"
        },
        {
            "name": "Health Monitoring",
            "description": "System health and monitoring"
        },
        {
            "name": "User Feedback",
            "description": "User feedback collection"
        },
        {
            "name": "Beta Management",
            "description": "Beta testing and feature flags"
        }
    ]
}

@api_docs_bp.route('/')
def swagger_ui():
    """Render Swagger UI documentation page."""
    return render_template('api_docs/swagger.html')

@api_docs_bp.route('/openapi.json')
def openapi_spec():
    """Serve OpenAPI specification as JSON."""
    return jsonify(OPENAPI_SPEC)

@api_docs_bp.route('/redoc')
def redoc_ui():
    """Render ReDoc documentation page."""
    return render_template('api_docs/redoc.html')

@api_docs_bp.route('/postman')
def postman_collection():
    """Generate Postman collection from OpenAPI spec."""
    
    # Convert OpenAPI to Postman collection format
    collection = {
        "info": {
            "name": "NOUS Personal Assistant API",
            "description": "API collection for NOUS Personal Assistant",
            "version": "1.0.0",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {
            "type": "bearer"
        },
        "item": []
    }
    
    # Convert paths to Postman requests
    for path, methods in OPENAPI_SPEC["paths"].items():
        for method, spec in methods.items():
            request_item = {
                "name": spec.get("summary", f"{method.upper()} {path}"),
                "request": {
                    "method": method.upper(),
                    "header": [
                        {
                            "key": "Content-Type",
                            "value": "application/json"
                        }
                    ],
                    "url": {
                        "raw": "{{base_url}}/api" + path,
                        "host": ["{{base_url}}"],
                        "path": ["api"] + path.strip("/").split("/")
                    }
                }
            }
            
            # Add request body if present
            if "requestBody" in spec:
                request_item["request"]["body"] = {
                    "mode": "raw",
                    "raw": json.dumps({
                        "example": "Add your request data here"
                    }, indent=2)
                }
            
            collection["item"].append(request_item)
    
    return jsonify(collection)

@api_docs_bp.route('/schemas')
def api_schemas():
    """List all available API schemas."""
    schemas = {}
    
    schema_classes = {
        'User': UserSchema,
        'ChatMessage': ChatMessageSchema,
        'ChatResponse': ChatResponseSchema,
        'Feedback': FeedbackSchema,
        'HealthCheck': HealthCheckSchema,
        'FeatureFlag': FeatureFlagSchema,
        'Error': ErrorSchema
    }
    
    for name, schema_class in schema_classes.items():
        schema_instance = schema_class()
        schemas[name] = {
            'fields': {
                field_name: {
                    'type': str(field.data_type) if hasattr(field, 'data_type') else 'string',
                    'required': field.required,
                    'description': getattr(field, 'metadata', {}).get('description', '')
                }
                for field_name, field in schema_instance.fields.items()
            }
        }
    
    return jsonify({
        'schemas': schemas,
        'total_count': len(schemas)
    })

@api_docs_bp.route('/endpoints')
def api_endpoints():
    """List all available API endpoints with metadata."""
    endpoints = []
    
    for path, methods in OPENAPI_SPEC["paths"].items():
        for method, spec in methods.items():
            endpoint = {
                'path': f"/api{path}",
                'method': method.upper(),
                'summary': spec.get('summary', ''),
                'description': spec.get('description', ''),
                'tags': spec.get('tags', []),
                'requires_auth': 'security' in spec,
                'parameters': [],
                'responses': list(spec.get('responses', {}).keys())
            }
            
            # Extract parameters
            if 'requestBody' in spec:
                endpoint['has_request_body'] = True
            
            endpoints.append(endpoint)
    
    return jsonify({
        'endpoints': endpoints,
        'total_count': len(endpoints),
        'by_tag': {
            tag['name']: [ep for ep in endpoints if tag['name'] in ep['tags']]
            for tag in OPENAPI_SPEC.get('tags', [])
        }
    })

def register_api_docs(app):
    """Register API documentation routes with Flask app."""
    app.register_blueprint(api_docs_bp)
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(app.root_path, 'templates', 'api_docs')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create Swagger UI template
    swagger_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>NOUS API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin:0; background: #fafafa; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '/api/docs/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            });
        };
    </script>
</body>
</html>
    '''
    
    # Create ReDoc template
    redoc_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>NOUS API Documentation - ReDoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body { margin: 0; padding: 0; }
    </style>
</head>
<body>
    <redoc spec-url='/api/docs/openapi.json'></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
</body>
</html>
    '''
    
    # Write template files
    with open(os.path.join(templates_dir, 'swagger.html'), 'w') as f:
        f.write(swagger_template)
    
    with open(os.path.join(templates_dir, 'redoc.html'), 'w') as f:
        f.write(redoc_template)
    
    return api_docs_bp