"""
Schema Validation Module

This module provides utilities for validating input data against JSON schemas,
ensuring that all API endpoints receive properly formatted data.

@module: schema_validation
@author: NOUS Development Team
"""
import jsonschema
import logging
from typing import Dict, Any, Optional, Callable, Union
from functools import wraps
from flask import request, jsonify, Request

# Configure logger
logger = logging.getLogger(__name__)

# Schema repository - stores all registered schemas
SCHEMA_REGISTRY = {}

def register_schema(name: str, schema: Dict[str, Any]) -> None:
    """
    Register a schema in the schema registry
    
    Args:
        name: Unique name for the schema
        schema: JSON Schema definition
    """
    if name in SCHEMA_REGISTRY:
        logger.warning(f"Overwriting existing schema: {name}")
    
    SCHEMA_REGISTRY[name] = schema
    logger.debug(f"Registered schema: {name}")

def get_schema(name: str) -> Optional[Dict[str, Any]]:
    """
    Get a schema from the registry by name
    
    Args:
        name: Name of the schema to retrieve
        
    Returns:
        Schema definition or None if not found
    """
    return SCHEMA_REGISTRY.get(name)

def validate_data(data: Any, schema: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate data against a JSON schema
    
    Args:
        data: Data to validate
        schema: JSON Schema to validate against
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        return False, str(e)

def validate_request(request_obj: Request, schema: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate a Flask request against a schema
    
    Args:
        request_obj: Flask request object
        schema: JSON Schema to validate against
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Handle different content types
    if request_obj.is_json:
        try:
            data = request_obj.get_json()
            return validate_data(data, schema)
        except Exception as e:
            return False, f"Invalid JSON: {str(e)}"
    elif request_obj.form:
        # Convert form data to dict
        form_data = {key: request_obj.form.get(key) for key in request_obj.form.keys()}
        return validate_data(form_data, schema)
    else:
        return False, "Unsupported content type"

def validate_with_schema(schema_name: str) -> Callable:
    """
    Decorator to validate request data against a JSON schema
    
    Args:
        schema_name: Name of the schema in the registry
        
    Returns:
        Decorator function that validates request data
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            schema = get_schema(schema_name)
            if not schema:
                logger.error(f"Schema not found: {schema_name}")
                return jsonify({
                    "error": "Server configuration error",
                    "message": f"Validation schema not found: {schema_name}"
                }), 500
            
            # Validate request data
            is_valid, error = validate_request(request, schema)
            if not is_valid:
                logger.warning(f"Validation failed for {request.path}: {error}")
                return jsonify({
                    "error": "Validation error",
                    "message": error
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Common schema patterns
def string_schema(min_length: int = 1, max_length: Optional[int] = None, pattern: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a schema for string validation
    
    Args:
        min_length: Minimum string length
        max_length: Maximum string length
        pattern: Regex pattern
        
    Returns:
        String schema definition
    """
    schema = {
        "type": "string",
        "minLength": min_length
    }
    
    if max_length is not None:
        schema["maxLength"] = max_length
    
    if pattern is not None:
        schema["pattern"] = pattern
    
    return schema

def email_schema() -> Dict[str, Any]:
    """
    Generate a schema for email validation
    
    Returns:
        Email schema definition
    """
    return {
        "type": "string",
        "format": "email",
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    }

def number_schema(minimum: Optional[Union[int, float]] = None, 
                 maximum: Optional[Union[int, float]] = None,
                 integer_only: bool = False) -> Dict[str, Any]:
    """
    Generate a schema for number validation
    
    Args:
        minimum: Minimum value
        maximum: Maximum value
        integer_only: Whether to require integers
        
    Returns:
        Number schema definition
    """
    schema = {
        "type": "integer" if integer_only else "number"
    }
    
    if minimum is not None:
        schema["minimum"] = minimum
    
    if maximum is not None:
        schema["maximum"] = maximum
    
    return schema

def boolean_schema() -> Dict[str, Any]:
    """
    Generate a schema for boolean validation
    
    Returns:
        Boolean schema definition
    """
    return {"type": "boolean"}

def array_schema(items_schema: Dict[str, Any], min_items: int = 0, max_items: Optional[int] = None) -> Dict[str, Any]:
    """
    Generate a schema for array validation
    
    Args:
        items_schema: Schema for array items
        min_items: Minimum number of items
        max_items: Maximum number of items
        
    Returns:
        Array schema definition
    """
    schema = {
        "type": "array",
        "items": items_schema,
        "minItems": min_items
    }
    
    if max_items is not None:
        schema["maxItems"] = max_items
    
    return schema

def object_schema(properties: Dict[str, Dict[str, Any]], required: Optional[list[str]] = None) -> Dict[str, Any]:
    """
    Generate a schema for object validation
    
    Args:
        properties: Object properties and their schemas
        required: List of required property names
        
    Returns:
        Object schema definition
    """
    schema = {
        "type": "object",
        "properties": properties
    }
    
    if required:
        schema["required"] = required
    
    return schema

# Register common schemas
register_schema("login", object_schema(
    properties={
        "email": email_schema(),
        "password": string_schema(min_length=8, max_length=128)
    },
    required=["email", "password"]
))

register_schema("refresh_token", object_schema(
    properties={
        "token": string_schema(min_length=10)
    },
    required=[]  # Token can also come from Authorization header
))

register_schema("fibonacci", object_schema(
    properties={
        "n": number_schema(minimum=0, maximum=35, integer_only=True)
    },
    required=["n"]
))

register_schema("api_simulation", object_schema(
    properties={
        "duration": number_schema(minimum=1, maximum=60, integer_only=True)
    },
    required=["duration"]
))

register_schema("process_data", object_schema(
    properties={
        "data": object_schema(
            properties={
                "text": string_schema(),
                "numbers": array_schema(number_schema())
            }
        )
    },
    required=["data"]
)) 