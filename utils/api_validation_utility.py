"""
API Validation Utility
Provides validation and None type checking for API endpoints
"""

import logging
from typing import Any, Optional, Dict, Union
from functools import wraps

logger = logging.getLogger(__name__)

class APIValidationUtility:
    """Utility for API input validation and None type checking"""
    
    @staticmethod
    def validate_not_none(value: Any, field_name: str) -> Any:
        """Validate that a value is not None"""
        if value is None:
            raise ValueError(f"Field '{field_name}' cannot be None")
        return value
    
    @staticmethod
    def validate_string_not_empty(value: Optional[str], field_name: str) -> str:
        """Validate that a string value is not None or empty"""
        if value is None:
            raise ValueError(f"Field '{field_name}' cannot be None")
        if not isinstance(value, str):
            raise ValueError(f"Field '{field_name}' must be a string")
        if not value.strip():
            raise ValueError(f"Field '{field_name}' cannot be empty")
        return value.strip()
    
    @staticmethod
    def validate_bytes_not_empty(value: Optional[bytes], field_name: str) -> bytes:
        """Validate that bytes value is not None or empty"""
        if value is None:
            raise ValueError(f"Field '{field_name}' cannot be None")
        if not isinstance(value, bytes):
            raise ValueError(f"Field '{field_name}' must be bytes")
        if len(value) == 0:
            raise ValueError(f"Field '{field_name}' cannot be empty")
        return value
    
    @staticmethod
    def safe_get(data: Optional[Dict], key: str, default: Any = None) -> Any:
        """Safely get value from dictionary with None checking"""
        if data is None:
            return default
        return data.get(key, default)
    
    @staticmethod
    def validate_request_data(required_fields: list):
        """Decorator to validate required fields in request data"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # This would extract request data and validate
                # For now, we return the original function
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Global validation utility
api_validator = APIValidationUtility()

# Convenience functions
def validate_not_none(value: Any, field_name: str) -> Any:
    """Validate value is not None"""
    return api_validator.validate_not_none(value, field_name)

def validate_string(value: Optional[str], field_name: str) -> str:
    """Validate string value"""
    return api_validator.validate_string_not_empty(value, field_name)

def validate_bytes(value: Optional[bytes], field_name: str) -> bytes:
    """Validate bytes value"""
    return api_validator.validate_bytes_not_empty(value, field_name)

def safe_get(data: Optional[Dict], key: str, default: Any = None) -> Any:
    """Safely get value from dict"""
    return api_validator.safe_get(data, key, default)
