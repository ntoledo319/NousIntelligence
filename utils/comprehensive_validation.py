"""
Comprehensive Input Validation System
Provides enterprise-grade input validation for all API endpoints
"""

import re
from typing import Any, Dict, List, Optional, Union
from functools import wraps
from flask import request, jsonify

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)

class InputValidator:
    """Comprehensive input validation with security focus"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format with security considerations"""
        if not email or len(email) > 254:  # RFC 5321 limit
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_string(text: str, min_length: int = 1, max_length: int = 1000, 
                       allow_html: bool = False) -> str:
        """Validate and sanitize string input"""
        if not isinstance(text, str):
            raise ValidationError("Input must be a string")
        
        # Length validation
        if len(text) < min_length:
            raise ValidationError(f"Input too short (minimum {min_length} characters)")
        
        if len(text) > max_length:
            raise ValidationError(f"Input too long (maximum {max_length} characters)")
        
        # Security sanitization
        if not allow_html:
            # Remove potentially dangerous characters
            dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'data:', 'vbscript:']
            for char in dangerous_chars:
                if char.lower() in text.lower():
                    raise ValidationError("Input contains potentially dangerous content")
        
        return text.strip()
    
    @staticmethod
    def validate_integer(value: Any, min_value: int = None, max_value: int = None) -> int:
        """Validate integer input with bounds checking"""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError("Input must be a valid integer")
        
        if min_value is not None and int_value < min_value:
            raise ValidationError(f"Value must be at least {min_value}")
        
        if max_value is not None and int_value > max_value:
            raise ValidationError(f"Value must be at most {max_value}")
        
        return int_value
    
    @staticmethod
    def validate_json_object(data: Any, required_fields: List[str] = None) -> Dict:
        """Validate JSON object structure"""
        if not isinstance(data, dict):
            raise ValidationError("Input must be a JSON object")
        
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
        return data

def validate_request(schema: Dict[str, Any] = None, max_content_length: int = 1024*1024):
    """
    Decorator for comprehensive request validation
    
    schema example:
    {
        'name': {'type': 'string', 'min_length': 2, 'max_length': 100},
        'email': {'type': 'email'},
        'age': {'type': 'integer', 'min_value': 0, 'max_value': 150}
    }
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Content length check
            if request.content_length and request.content_length > max_content_length:
                return jsonify({
                    'error': 'Request too large',
                    'max_size': f'{max_content_length} bytes'
                }), 413
            
            # Get and validate JSON data
            try:
                if request.is_json:
                    data = request.get_json()
                else:
                    data = request.form.to_dict()
            except Exception:
                return jsonify({'error': 'Invalid request format'}), 400
            
            if not data:
                data = {}
            
            # Apply schema validation if provided
            if schema:
                try:
                    validated_data = {}
                    
                    for field, rules in schema.items():
                        if field in data:
                            value = data[field]
                            field_type = rules.get('type', 'string')
                            
                            if field_type == 'string':
                                validated_data[field] = InputValidator.validate_string(
                                    value,
                                    min_length=rules.get('min_length', 1),
                                    max_length=rules.get('max_length', 1000),
                                    allow_html=rules.get('allow_html', False)
                                )
                            elif field_type == 'email':
                                if not InputValidator.validate_email(value):
                                    raise ValidationError(f"Invalid email format", field)
                                validated_data[field] = value
                            elif field_type == 'integer':
                                validated_data[field] = InputValidator.validate_integer(
                                    value,
                                    min_value=rules.get('min_value'),
                                    max_value=rules.get('max_value')
                                )
                        elif rules.get('required', False):
                            raise ValidationError(f"Required field missing", field)
                    
                    # Add validated data to request object
                    request.validated_data = validated_data
                    
                except ValidationError as e:
                    return jsonify({
                        'error': e.message,
                        'field': e.field
                    }), 400
            else:
                request.validated_data = data
            
            return f(*args, **kwargs)
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator
