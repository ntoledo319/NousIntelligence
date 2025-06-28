"""
Schema Validation Utilities
Provides JSON schema validation for API endpoints and user input
"""

import logging
from functools import wraps
from flask import request, jsonify
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

# Common validation schemas
SCHEMAS = {
    'login': {
        'type': 'object',
        'properties': {
            'email': {
                'type': 'string',
                'format': 'email',
                'maxLength': 255
            },
            'password': {
                'type': 'string',
                'minLength': 6,
                'maxLength': 128
            }
        },
        'required': ['email', 'password'],
        'additionalProperties': False
    },
    
    'register': {
        'type': 'object',
        'properties': {
            'email': {
                'type': 'string',
                'format': 'email',
                'maxLength': 255
            },
            'password': {
                'type': 'string',
                'minLength': 8,
                'maxLength': 128
            },
            'name': {
                'type': 'string',
                'minLength': 1,
                'maxLength': 100
            }
        },
        'required': ['email', 'password', 'name'],
        'additionalProperties': False
    },
    
    'chat_message': {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string',
                'minLength': 1,
                'maxLength': 4000
            },
            'context': {
                'type': 'object'
            }
        },
        'required': ['message'],
        'additionalProperties': True
    },
    
    'feedback': {
        'type': 'object',
        'properties': {
            'rating': {
                'type': 'integer',
                'minimum': 1,
                'maximum': 5
            },
            'comment': {
                'type': 'string',
                'maxLength': 1000
            },
            'category': {
                'type': 'string',
                'enum': ['helpful', 'accurate', 'fast', 'friendly', 'other']
            }
        },
        'required': ['rating'],
        'additionalProperties': False
    }
}

def validate_data(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate data against schema
    
    Args:
        data: Data to validate
        schema: JSON schema
        
    Returns:
        Validation result with errors if any
    """
    errors = []
    
    # Check required fields
    required = schema.get('required', [])
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Check field types and constraints
    properties = schema.get('properties', {})
    for field, value in data.items():
        if field in properties:
            field_schema = properties[field]
            field_errors = _validate_field(field, value, field_schema)
            errors.extend(field_errors)
    
    # Check additional properties
    if not schema.get('additionalProperties', True):
        for field in data:
            if field not in properties:
                errors.append(f"Additional property not allowed: {field}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def _validate_field(field_name: str, value: Any, schema: Dict[str, Any]) -> list:
    """Validate individual field against its schema"""
    errors = []
    expected_type = schema.get('type')
    
    # Type validation
    if expected_type:
        if expected_type == 'string' and not isinstance(value, str):
            errors.append(f"{field_name} must be a string")
        elif expected_type == 'integer' and not isinstance(value, int):
            errors.append(f"{field_name} must be an integer")
        elif expected_type == 'number' and not isinstance(value, (int, float)):
            errors.append(f"{field_name} must be a number")
        elif expected_type == 'boolean' and not isinstance(value, bool):
            errors.append(f"{field_name} must be a boolean")
        elif expected_type == 'object' and not isinstance(value, dict):
            errors.append(f"{field_name} must be an object")
        elif expected_type == 'array' and not isinstance(value, list):
            errors.append(f"{field_name} must be an array")
    
    # String constraints
    if isinstance(value, str):
        min_length = schema.get('minLength')
        max_length = schema.get('maxLength')
        
        if min_length and len(value) < min_length:
            errors.append(f"{field_name} must be at least {min_length} characters")
        
        if max_length and len(value) > max_length:
            errors.append(f"{field_name} must not exceed {max_length} characters")
        
        # Email format validation
        if schema.get('format') == 'email':
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                errors.append(f"{field_name} must be a valid email address")
    
    # Number constraints
    if isinstance(value, (int, float)):
        minimum = schema.get('minimum')
        maximum = schema.get('maximum')
        
        if minimum is not None and value < minimum:
            errors.append(f"{field_name} must be at least {minimum}")
        
        if maximum is not None and value > maximum:
            errors.append(f"{field_name} must not exceed {maximum}")
    
    # Enum validation
    enum_values = schema.get('enum')
    if enum_values and value not in enum_values:
        errors.append(f"{field_name} must be one of: {', '.join(map(str, enum_values))}")
    
    return errors

def validate_with_schema(schema_name: str):
    """
    Decorator to validate request JSON against a predefined schema
    
    Args:
        schema_name: Name of schema in SCHEMAS dict
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body must contain valid JSON'}), 400
            
            schema = SCHEMAS.get(schema_name)
            if not schema:
                logger.error(f"Schema '{schema_name}' not found")
                return jsonify({'error': 'Internal validation error'}), 500
            
            validation_result = validate_data(data, schema)
            if not validation_result['valid']:
                return jsonify({
                    'error': 'Validation failed',
                    'details': validation_result['errors']
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_query_params(param_schema: Dict[str, Dict[str, Any]]):
    """
    Decorator to validate query parameters
    
    Args:
        param_schema: Schema for query parameters
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            errors = []
            
            for param_name, param_config in param_schema.items():
                value = request.args.get(param_name)
                
                # Check required parameters
                if param_config.get('required', False) and not value:
                    errors.append(f"Missing required parameter: {param_name}")
                    continue
                
                if value:
                    # Type conversion and validation
                    param_type = param_config.get('type', 'string')
                    
                    try:
                        if param_type == 'integer':
                            value = int(value)
                        elif param_type == 'number':
                            value = float(value)
                        elif param_type == 'boolean':
                            value = value.lower() in ('true', '1', 'yes', 'on')
                    except ValueError:
                        errors.append(f"Parameter {param_name} must be {param_type}")
                        continue
                    
                    # Validate constraints
                    field_errors = _validate_field(param_name, value, param_config)
                    errors.extend(field_errors)
            
            if errors:
                return jsonify({
                    'error': 'Parameter validation failed',
                    'details': errors
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_and_validate(data: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
    """
    Sanitize and validate data
    
    Args:
        data: Data to validate
        schema_name: Name of schema to use
        
    Returns:
        Result with sanitized data and validation status
    """
    from utils.security_helper import sanitize_input
    
    # Sanitize string fields
    sanitized_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized_data[key] = sanitize_input(value)
        else:
            sanitized_data[key] = value
    
    # Validate
    schema = SCHEMAS.get(schema_name, {})
    validation_result = validate_data(sanitized_data, schema)
    
    return {
        'data': sanitized_data,
        'valid': validation_result['valid'],
        'errors': validation_result['errors']
    }