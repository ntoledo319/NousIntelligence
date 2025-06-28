"""
Standardized API Response System
Implements consistent response formats, error handling, and status codes across all routes
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Union, List
from flask import jsonify, Response
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

class APIResponse:
    """Standardized API response class for consistent JSON responses"""
    
    def __init__(self, 
                 success: bool = True, 
                 data: Any = None, 
                 message: str = "", 
                 errors: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 status_code: int = 200):
        self.success = success
        self.data = data
        self.message = message
        self.errors = errors or []
        self.metadata = metadata or {}
        self.status_code = status_code
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format"""
        response = {
            "success": self.success,
            "timestamp": self.timestamp,
            "message": self.message
        }
        
        if self.data is not None:
            response["data"] = self.data
            
        if self.errors:
            response["errors"] = self.errors
            
        if self.metadata:
            response["metadata"] = self.metadata
            
        return response
    
    def to_json_response(self) -> tuple[Response, int]:
        """Convert to Flask JSON response"""
        return jsonify(self.to_dict()), self.status_code

# Standard response builders
def success_response(data: Any = None, 
                    message: str = "Success", 
                    metadata: Optional[Dict[str, Any]] = None,
                    status_code: int = 200) -> tuple[Response, int]:
    """Create standardized success response"""
    response = APIResponse(
        success=True,
        data=data,
        message=message,
        metadata=metadata,
        status_code=status_code
    )
    return response.to_json_response()

def error_response(message: str = "An error occurred",
                  errors: Optional[List[str]] = None,
                  data: Any = None,
                  status_code: int = 400,
                  metadata: Optional[Dict[str, Any]] = None) -> Response:
    """Create standardized error response"""
    response = APIResponse(
        success=False,
        data=data,
        message=message,
        errors=errors,
        metadata=metadata,
        status_code=status_code
    )
    
    # Log error for monitoring
    logger.error(f"API Error: {message}, Status: {status_code}, Errors: {errors}")
    
    return response.to_json_response()

def validation_error_response(errors: List[str], 
                            message: str = "Validation failed") -> Response:
    """Create validation error response"""
    return error_response(
        message=message,
        errors=errors,
        status_code=422
    )

def not_found_response(resource: str = "Resource") -> Response:
    """Create 404 not found response"""
    return error_response(
        message=f"{resource} not found",
        status_code=404
    )

def unauthorized_response(message: str = "Authentication required") -> Response:
    """Create 401 unauthorized response"""
    return error_response(
        message=message,
        status_code=401
    )

def forbidden_response(message: str = "Access forbidden") -> Response:
    """Create 403 forbidden response"""
    return error_response(
        message=message,
        status_code=403
    )

def server_error_response(message: str = "Internal server error") -> Response:
    """Create 500 server error response"""
    return error_response(
        message=message,
        status_code=500
    )

def rate_limit_response(message: str = "Rate limit exceeded") -> Response:
    """Create 429 rate limit response"""
    return error_response(
        message=message,
        status_code=429
    )

# Response decorators for common patterns
def handle_exceptions(func):
    """Decorator to handle common exceptions in routes"""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPException as e:
            return error_response(
                message=e.description or "HTTP error occurred",
                status_code=e.code or 500
            )
        except ValueError as e:
            return validation_error_response(
                errors=[str(e)],
                message="Invalid input provided"
            )
        except PermissionError as e:
            return forbidden_response(str(e))
        except FileNotFoundError as e:
            return not_found_response("File")
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
            return server_error_response(
                message="An unexpected error occurred"
            )
    
    return wrapper

def require_json(func):
    """Decorator to require JSON content type"""
    from functools import wraps
    from flask import request
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return error_response(
                message="Content-Type must be application/json",
                status_code=400
            )
        return func(*args, **kwargs)
    
    return wrapper

def paginated_response(data: List[Any], 
                      page: int, 
                      per_page: int, 
                      total: int,
                      message: str = "Data retrieved successfully") -> Response:
    """Create paginated response"""
    total_pages = (total + per_page - 1) // per_page
    
    metadata = {
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    
    return success_response(
        data=data,
        message=message,
        metadata=metadata
    )

# Health check response
def health_check_response(status: str = "healthy", 
                         checks: Optional[Dict[str, Any]] = None) -> Response:
    """Create health check response"""
    data = {
        "status": status,
        "checks": checks or {}
    }
    
    status_code = 200 if status == "healthy" else 503
    
    return success_response(
        data=data,
        message=f"Service is {status}",
        status_code=status_code
    )

# AI response formatting
def ai_response(content: str,
               provider: str = "openrouter",
               model: str = "unknown",
               tokens_used: Optional[int] = None,
               processing_time: Optional[float] = None) -> Response:
    """Create AI service response"""
    metadata = {
        "ai": {
            "provider": provider,
            "model": model,
            "tokens_used": tokens_used,
            "processing_time_seconds": processing_time
        }
    }
    
    return success_response(
        data={"content": content},
        message="AI response generated successfully",
        metadata=metadata
    )

# File upload response
def upload_response(file_info: Dict[str, Any]) -> Response:
    """Create file upload response"""
    return success_response(
        data=file_info,
        message="File uploaded successfully",
        status_code=201
    )

# Bulk operation response
def bulk_response(successful: int, 
                 failed: int, 
                 errors: Optional[List[str]] = None) -> Response:
    """Create bulk operation response"""
    total = successful + failed
    success = failed == 0
    
    data = {
        "total": total,
        "successful": successful,
        "failed": failed,
        "success_rate": (successful / total * 100) if total > 0 else 0
    }
    
    message = f"Bulk operation completed: {successful}/{total} successful"
    
    if success:
        return success_response(data=data, message=message)
    else:
        return error_response(
            data=data,
            message=message,
            errors=errors,
            status_code=207  # Multi-status
        )