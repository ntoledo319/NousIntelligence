"""
API Documentation Generator

This module provides functionality to generate OpenAPI/Swagger documentation
for the API endpoints in the NOUS application. It scans the application's
route blueprints and generates corresponding OpenAPI specifications.

@module: api_documentation
@author: NOUS Development Team
"""
import re
import json
import inspect
from flask import Flask, Blueprint, jsonify, request, url_for, current_app
from typing import Dict, List, Any, Optional, Callable
import logging

# Configure logger
logger = logging.getLogger(__name__)

# OpenAPI metadata
OPENAPI_VERSION = "3.0.0"
API_VERSION = "1.0.0"
API_TITLE = "NOUS API"
API_DESCRIPTION = "API for the NOUS personal assistant application"

def generate_openapi_spec(app: Flask) -> Dict[str, Any]:
    """
    Generate OpenAPI specification by analyzing Flask routes
    
    Args:
        app: Flask application instance
        
    Returns:
        Dict containing the OpenAPI specification
    """
    # Base OpenAPI structure
    openapi_spec = {
        "openapi": OPENAPI_VERSION,
        "info": {
            "title": API_TITLE,
            "description": API_DESCRIPTION,
            "version": API_VERSION,
            "contact": {
                "name": "NOUS Development Team",
                "url": "https://mynous.replit.app"
            }
        },
        "servers": [
            {
                "url": "/",
                "description": "Current server"
            }
        ],
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {
                "sessionAuth": {
                    "type": "apiKey",
                    "in": "cookie",
                    "name": "session"
                }
            }
        }
    }
    
    # Process all routes in the application
    for rule in app.url_map.iter_rules():
        # Skip static files and non-API routes
        if "static" in rule.endpoint or not rule.endpoint.startswith(("api", "async_api")):
            continue
            
        # Get route function
        try:
            view_func = app.view_functions[rule.endpoint]
        except KeyError:
            continue
            
        # Extract path parameters from the route
        path = str(rule)
        path_params = []
        
        # Convert Flask route parameters to OpenAPI parameters
        # e.g., /user/<int:user_id> -> /user/{user_id}
        for match in re.finditer(r'<(?:[^:]+:)?([^>]+)>', path):
            param_name = match.group(1)
            path = path.replace(match.group(0), f"{{{param_name}}}")
            path_params.append({
                "name": param_name,
                "in": "path",
                "required": True,
                "schema": {"type": "string"}
            })
        
        # Extract documentation from docstring
        docstring = inspect.getdoc(view_func)
        route_info = parse_docstring(docstring) if docstring else {}
        
        # Initialize path if not already present
        if path not in openapi_spec["paths"]:
            openapi_spec["paths"][path] = {}
        
        # Add methods for this path
        for method in rule.methods:
            if method in ["HEAD", "OPTIONS"]:
                continue
                
            method_lower = method.lower()
            
            # Create method entry
            method_entry = {
                "summary": route_info.get("summary", view_func.__name__),
                "description": route_info.get("description", ""),
                "parameters": path_params.copy(),  # Add path parameters
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad request",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                        "message": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"},
                                        "message": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            # Add security if required
            if route_info.get("requires_auth", True):
                method_entry["security"] = [{"sessionAuth": []}]
            
            # Add request body for POST, PUT, PATCH methods
            if method in ["POST", "PUT", "PATCH"] and route_info.get("request_schema"):
                method_entry["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": route_info.get("request_schema")
                        }
                    }
                }
            
            # Add query parameters
            if "query_params" in route_info:
                for param in route_info["query_params"]:
                    method_entry["parameters"].append({
                        "name": param["name"],
                        "in": "query",
                        "description": param.get("description", ""),
                        "required": param.get("required", False),
                        "schema": param.get("schema", {"type": "string"})
                    })
            
            # Add to the path
            openapi_spec["paths"][path][method_lower] = method_entry
    
    # Add standard schemas to components
    openapi_spec["components"]["schemas"] = generate_standard_schemas()
    
    return openapi_spec

def parse_docstring(docstring: str) -> Dict[str, Any]:
    """
    Parse a docstring to extract API documentation
    
    Args:
        docstring: The function docstring
        
    Returns:
        Dict containing extracted documentation
    """
    info = {
        "summary": "",
        "description": "",
        "requires_auth": True,
        "query_params": []
    }
    
    # Extract summary (first line)
    lines = docstring.strip().split("\n")
    if lines:
        info["summary"] = lines[0].strip()
    
    # Extract description (all lines after summary until a directive)
    description_lines = []
    for line in lines[1:]:
        line = line.strip()
        if line and not line.startswith(("@", "Request", "Response")):
            description_lines.append(line)
        elif line.startswith(("Request", "Response")):
            break
    
    if description_lines:
        info["description"] = "\n".join(description_lines).strip()
    
    # Extract request schema
    request_schema_lines = []
    in_request = False
    for line in lines:
        if "Request JSON:" in line:
            in_request = True
            continue
        elif "Response:" in line:
            in_request = False
            continue
            
        if in_request and line.strip():
            request_schema_lines.append(line)
    
    # Try to parse request schema
    if request_schema_lines:
        # Remove code block markers
        if request_schema_lines[0].strip() == "{" and request_schema_lines[-1].strip() == "}":
            try:
                schema_str = "\n".join(request_schema_lines)
                schema = json.loads(schema_str)
                info["request_schema"] = schema_to_openapi(schema)
            except json.JSONDecodeError:
                # If we can't parse it, just use a generic object schema
                info["request_schema"] = {"type": "object"}
    
    return info

def schema_to_openapi(example: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert an example JSON object to an OpenAPI schema
    
    Args:
        example: Example JSON object
        
    Returns:
        OpenAPI schema
    """
    schema = {
        "type": "object",
        "properties": {}
    }
    
    for key, value in example.items():
        if isinstance(value, dict):
            schema["properties"][key] = schema_to_openapi(value)
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                schema["properties"][key] = {
                    "type": "array",
                    "items": schema_to_openapi(value[0])
                }
            else:
                schema["properties"][key] = {
                    "type": "array",
                    "items": {"type": get_type_name(value[0]) if value else "string"}
                }
        else:
            schema["properties"][key] = {"type": get_type_name(value)}
            
            # Add example value
            if value is not None:
                schema["properties"][key]["example"] = value
    
    return schema

def get_type_name(value: Any) -> str:
    """
    Get OpenAPI type name for a Python value
    
    Args:
        value: Python value
        
    Returns:
        OpenAPI type name
    """
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, (list, tuple)):
        return "array"
    elif isinstance(value, dict):
        return "object"
    else:
        return "string"

def generate_standard_schemas() -> Dict[str, Any]:
    """
    Generate standard schema components
    
    Returns:
        Dict of schema components
    """
    return {
        "Error": {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
                "message": {"type": "string"}
            },
            "required": ["error", "message"]
        },
        "TaskResponse": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "status": {"type": "string", "enum": ["pending", "running", "completed", "failed", "cancelled"]},
                "result": {"type": "object"},
                "error": {"type": "string", "nullable": True}
            },
            "required": ["task_id", "status"]
        },
        "AsyncTaskRequest": {
            "type": "object",
            "properties": {
                "n": {"type": "integer", "minimum": 0, "maximum": 35, "example": 30}
            },
            "required": ["n"]
        },
        "ApiSimulationRequest": {
            "type": "object",
            "properties": {
                "duration": {"type": "integer", "minimum": 1, "maximum": 60, "example": 5}
            },
            "required": ["duration"]
        },
        "DataProcessingRequest": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "example": "Sample text to process"},
                        "numbers": {"type": "array", "items": {"type": "integer"}, "example": [1, 2, 3, 4, 5]}
                    }
                }
            },
            "required": ["data"]
        }
    }

def register_openapi_blueprint(app: Flask) -> Blueprint:
    """
    Register a blueprint for OpenAPI documentation
    
    Args:
        app: Flask application instance
        
    Returns:
        Registered blueprint
    """
    api_docs = Blueprint('api_docs', __name__)
    
    @api_docs.route('/api/docs/openapi.json')
    def get_openapi_spec():
        """Get the OpenAPI specification as JSON"""
        try:
            spec = generate_openapi_spec(app)
            return jsonify(spec)
        except Exception as e:
            logger.exception("Error generating OpenAPI spec")
            return jsonify({"error": "Failed to generate OpenAPI spec", "message": str(e)}), 500
    
    @api_docs.route('/api/docs')
    def api_docs_ui():
        """Render Swagger UI for API documentation"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{API_TITLE} Documentation</title>
            <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.0.0/swagger-ui.css" />
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                }}
                #swagger-ui {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@5.0.0/swagger-ui-bundle.js"></script>
            <script>
                window.onload = function() {{
                    SwaggerUIBundle({{
                        url: "{url_for('api_docs.get_openapi_spec')}",
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIBundle.SwaggerUIStandalonePreset
                        ],
                        layout: "BaseLayout",
                        persistAuthorization: true
                    }});
                }};
            </script>
        </body>
        </html>
        """
    
    app.register_blueprint(api_docs)
    logger.info("Registered API documentation endpoints")
    
    return api_docs 