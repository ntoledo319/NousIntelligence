"""
Error Handling Module

This module provides custom exceptions and error handling utilities
for the NOUS application infrastructure layer.

@ai_prompt For error handling, use custom exceptions from this module
# AI-GENERATED 2025-07-11
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """
    Exception raised for validation errors.
    
    Used when input data fails validation rules.
    """
    
    def __init__(self, message: str, field: Optional[str] = None, code: Optional[str] = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message describing the validation failure
            field: Optional field name that failed validation
            code: Optional error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.field = field
        self.code = code or "validation_error"
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary format.
        
        Returns:
            Dictionary representation of the error
        """
        return {
            "error": "validation_error",
            "message": self.message,
            "field": self.field,
            "code": self.code
        }


class NotFoundError(Exception):
    """
    Exception raised when a requested resource is not found.
    
    Used when database queries return no results for a specific ID.
    """
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None):
        """
        Initialize not found error.
        
        Args:
            message: Error message describing what was not found
            resource_type: Optional type of resource that was not found
            resource_id: Optional ID of the resource that was not found
        """
        super().__init__(message)
        self.message = message
        self.resource_type = resource_type
        self.resource_id = resource_id
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary format.
        
        Returns:
            Dictionary representation of the error
        """
        return {
            "error": "not_found",
            "message": self.message,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id
        }


class AuthorizationError(Exception):
    """
    Exception raised when a user is not authorized to perform an action.
    
    Used when access control checks fail.
    """
    
    def __init__(self, message: str, action: Optional[str] = None, resource: Optional[str] = None):
        """
        Initialize authorization error.
        
        Args:
            message: Error message describing the authorization failure
            action: Optional action that was attempted
            resource: Optional resource that was accessed
        """
        super().__init__(message)
        self.message = message
        self.action = action
        self.resource = resource
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary format.
        
        Returns:
            Dictionary representation of the error
        """
        return {
            "error": "authorization_error",
            "message": self.message,
            "action": self.action,
            "resource": self.resource
        }


class ServiceError(Exception):
    """
    Exception raised for service-layer errors.
    
    Used for business logic errors that don't fit other categories.
    """
    
    def __init__(self, message: str, service: Optional[str] = None, operation: Optional[str] = None):
        """
        Initialize service error.
        
        Args:
            message: Error message describing the service error
            service: Optional service name where error occurred
            operation: Optional operation that failed
        """
        super().__init__(message)
        self.message = message
        self.service = service
        self.operation = operation
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary format.
        
        Returns:
            Dictionary representation of the error
        """
        return {
            "error": "service_error",
            "message": self.message,
            "service": self.service,
            "operation": self.operation
        }


def handle_error(error: Exception) -> Dict[str, Any]:
    """
    Handle and format errors for API responses.
    
    Args:
        error: The exception to handle
        
    Returns:
        Dictionary containing error information
    """
    if isinstance(error, (ValidationError, NotFoundError, AuthorizationError, ServiceError)):
        return error.to_dict()
    
    # Log unexpected errors
    logger.error(f"Unexpected error: {error}", exc_info=True)
    
    # Return generic error for unknown exceptions
    return {
        "error": "internal_error",
        "message": "An unexpected error occurred",
        "code": "internal_error"
    }


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of field names that are required
        
    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            field=missing_fields[0] if len(missing_fields) == 1 else None,
            code="missing_fields"
        )


def validate_field_type(data: Dict[str, Any], field: str, expected_type: type) -> None:
    """
    Validate that a field has the expected type.
    
    Args:
        data: Data dictionary to validate
        field: Field name to validate
        expected_type: Expected type of the field
        
    Raises:
        ValidationError: If field type doesn't match expected type
    """
    if field in data and data[field] is not None:
        if not isinstance(data[field], expected_type):
            raise ValidationError(
                f"Field '{field}' must be of type {expected_type.__name__}",
                field=field,
                code="invalid_type"
            )


def validate_field_range(data: Dict[str, Any], field: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> None:
    """
    Validate that a numeric field is within a specified range.
    
    Args:
        data: Data dictionary to validate
        field: Field name to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        
    Raises:
        ValidationError: If field value is outside the allowed range
    """
    if field in data and data[field] is not None:
        value = data[field]
        
        if min_val is not None and value < min_val:
            raise ValidationError(
                f"Field '{field}' must be at least {min_val}",
                field=field,
                code="value_too_low"
            )
            
        if max_val is not None and value > max_val:
            raise ValidationError(
                f"Field '{field}' must be at most {max_val}",
                field=field,
                code="value_too_high"
            )
