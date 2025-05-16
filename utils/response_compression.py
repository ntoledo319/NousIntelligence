"""
@module response_compression
@description Response compression middleware to reduce bandwidth usage and improve API performance
@author AI Assistant
"""

import gzip
import brotli
import zlib
import logging
from typing import Dict, Any, Callable, Optional, Union, List
from functools import wraps
from io import BytesIO
from flask import request, Response, after_this_request

# Configure logger
logger = logging.getLogger(__name__)

# Constants
DEFAULT_COMPRESSION = 'gzip'
DEFAULT_COMPRESSION_LEVEL = 6  # Medium compression (range is 1-9)
DEFAULT_MIN_SIZE = 500  # Minimum response size in bytes to compress
COMPRESSION_TYPES = ['gzip', 'deflate', 'br']  # Supported compression algorithms

class ResponseCompression:
    """Response compression handler for Flask applications"""
    
    def __init__(self, 
                app=None, 
                compression_level: int = DEFAULT_COMPRESSION_LEVEL,
                min_size: int = DEFAULT_MIN_SIZE,
                excluded_paths: Optional[List[str]] = None):
        """
        Initialize the response compression handler
        
        Args:
            app: Optional Flask application
            compression_level: Compression level (1-9, 9 being highest)
            min_size: Minimum response size to compress
            excluded_paths: List of URL paths to exclude from compression
        """
        self.compression_level = compression_level
        self.min_size = min_size
        self.excluded_paths = excluded_paths or []
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize the compression handler with a Flask application
        
        Args:
            app: Flask application
        """
        # Register the middleware
        app.after_request(self.compress_response)
        
        # Log configuration
        logger.info(f"Response compression initialized: level={self.compression_level}, min_size={self.min_size} bytes")
    
    def should_compress(self, response: Response) -> bool:
        """
        Determine if a response should be compressed
        
        Args:
            response: Flask response object
            
        Returns:
            True if the response should be compressed, False otherwise
        """
        # Don't compress if client doesn't support it
        accept_encoding = request.headers.get('Accept-Encoding', '')
        if not any(enc in accept_encoding for enc in COMPRESSION_TYPES):
            return False
        
        # Skip if response is already compressed
        if response.headers.get('Content-Encoding'):
            return False
            
        # Skip excluded paths
        if any(path in request.path for path in self.excluded_paths):
            return False
            
        # Skip if response is too small
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) < self.min_size:
            return False
            
        # Skip streaming responses
        if response.direct_passthrough:
            return False
            
        # Skip if not compressible content type
        content_type = response.headers.get('Content-Type', '')
        compressible_types = [
            'text/', 'application/json', 'application/xml', 'application/javascript',
            'application/xhtml+xml', 'image/svg+xml', 'application/atom+xml'
        ]
        
        if not any(ctype in content_type for ctype in compressible_types):
            return False
            
        return True
    
    def compress_response(self, response: Response) -> Response:
        """
        Compress a Flask response if appropriate
        
        Args:
            response: Flask response
            
        Returns:
            Compressed or original response
        """
        if not self.should_compress(response):
            return response
            
        # Determine best compression method based on Accept-Encoding header
        accept_encoding = request.headers.get('Accept-Encoding', '')
        compression_method = self._get_best_compression(accept_encoding)
        
        # Get original data
        data = response.get_data()
        
        # Skip if already compressed or empty
        if not data:
            return response
            
        # Compress the data
        compressed_data = self._compress_data(data, compression_method)
        
        # If compression didn't help, return original
        if len(compressed_data) >= len(data):
            return response
            
        # Update response with compressed data
        response.set_data(compressed_data)
        response.headers['Content-Encoding'] = compression_method
        response.headers['Content-Length'] = str(len(compressed_data))
        
        # Add Vary header to help caching
        if 'Vary' in response.headers:
            response.headers['Vary'] = response.headers['Vary'] + ', Accept-Encoding'
        else:
            response.headers['Vary'] = 'Accept-Encoding'
            
        # Log compression stats
        compression_ratio = round((1 - len(compressed_data) / len(data)) * 100, 2)
        logger.debug(f"Compressed response: {len(data)} → {len(compressed_data)} bytes ({compression_ratio}% reduction)")
        
        return response
    
    def _get_best_compression(self, accept_encoding: str) -> str:
        """
        Determine the best compression method based on Accept-Encoding header
        
        Args:
            accept_encoding: Accept-Encoding header value
            
        Returns:
            Best compression method name
        """
        # Check for Brotli support first (best compression)
        if 'br' in accept_encoding:
            return 'br'
            
        # Then gzip (most widely supported)
        if 'gzip' in accept_encoding:
            return 'gzip'
            
        # Finally deflate
        if 'deflate' in accept_encoding:
            return 'deflate'
            
        # Default to gzip
        return DEFAULT_COMPRESSION
    
    def _compress_data(self, data: bytes, method: str) -> bytes:
        """
        Compress data using the specified method
        
        Args:
            data: Raw response data
            method: Compression method (gzip, deflate, br)
            
        Returns:
            Compressed data
        """
        if method == 'gzip':
            buffer = BytesIO()
            with gzip.GzipFile(mode='wb', compresslevel=self.compression_level, fileobj=buffer) as f:
                f.write(data)
            return buffer.getvalue()
            
        elif method == 'deflate':
            return zlib.compress(data, self.compression_level)
            
        elif method == 'br':
            return brotli.compress(data, quality=self.compression_level)
            
        # Fallback to gzip
        buffer = BytesIO()
        with gzip.GzipFile(mode='wb', compresslevel=self.compression_level, fileobj=buffer) as f:
            f.write(data)
        return buffer.getvalue()

def compress_response(app=None):
    """
    Decorator to compress API responses for a Flask application
    
    Args:
        app: Flask application
        
    Returns:
        Decorated function
    """
    return ResponseCompression(app)

def compress_endpoint(min_size: int = DEFAULT_MIN_SIZE, 
                     compression_level: int = DEFAULT_COMPRESSION_LEVEL):
    """
    Decorator for compressing individual Flask endpoints
    
    Args:
        min_size: Minimum size in bytes to compress
        compression_level: Compression level (1-9)
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            @after_this_request
            def compress_response(response):
                accept_encoding = request.headers.get('Accept-Encoding', '')
                
                # Skip if client doesn't support compression
                if not any(enc in accept_encoding for enc in COMPRESSION_TYPES):
                    return response
                
                # Skip if response is already compressed
                if response.headers.get('Content-Encoding'):
                    return response
                
                # Get data
                data = response.get_data()
                
                # Skip if too small or empty
                if not data or len(data) < min_size:
                    return response
                
                # Determine compression method
                if 'br' in accept_encoding:
                    compressed_data = brotli.compress(data, quality=compression_level)
                    encoding = 'br'
                elif 'gzip' in accept_encoding:
                    buffer = BytesIO()
                    with gzip.GzipFile(mode='wb', compresslevel=compression_level, fileobj=buffer) as f:
                        f.write(data)
                    compressed_data = buffer.getvalue()
                    encoding = 'gzip'
                elif 'deflate' in accept_encoding:
                    compressed_data = zlib.compress(data, compression_level)
                    encoding = 'deflate'
                else:
                    return response
                
                # Skip if compression didn't help
                if len(compressed_data) >= len(data):
                    return response
                
                # Update response
                response.set_data(compressed_data)
                response.headers['Content-Encoding'] = encoding
                response.headers['Content-Length'] = str(len(compressed_data))
                
                # Add Vary header
                if 'Vary' in response.headers:
                    response.headers['Vary'] = response.headers['Vary'] + ', Accept-Encoding'
                else:
                    response.headers['Vary'] = 'Accept-Encoding'
                
                return response
            
            # Call the original function
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

def json_compress(data: Dict[str, Any], pretty: bool = False) -> Dict[str, Any]:
    """
    Compress values within a JSON object
    
    This can be used for large text fields to reduce payload size
    
    Args:
        data: JSON data to compress
        pretty: Whether to preserve pretty formatting
        
    Returns:
        JSON with compressed values
    """
    result = {}
    
    # Process all keys
    for key, value in data.items():
        # Skip small values
        if isinstance(value, str) and len(value) > DEFAULT_MIN_SIZE:
            # Special marker to indicate compressed value
            result[key] = {
                "_compressed": "gzip",
                "data": compress_string(value)
            }
        elif isinstance(value, dict):
            # Recursively process dictionaries
            result[key] = json_compress(value, pretty)
        elif isinstance(value, list):
            # Process lists
            result[key] = [
                json_compress(item, pretty) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            # Keep other values as-is
            result[key] = value
            
    return result

def json_decompress(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decompress values in a compressed JSON object
    
    Args:
        data: Compressed JSON data
        
    Returns:
        Decompressed JSON
    """
    result = {}
    
    # Process all keys
    for key, value in data.items():
        if isinstance(value, dict):
            if "_compressed" in value and "data" in value:
                # Decompress the value
                if value["_compressed"] == "gzip":
                    result[key] = decompress_string(value["data"])
                else:
                    # Unsupported compression method, keep as-is
                    result[key] = value
            else:
                # Recursively process dictionaries
                result[key] = json_decompress(value)
        elif isinstance(value, list):
            # Process lists
            result[key] = [
                json_decompress(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            # Keep other values as-is
            result[key] = value
            
    return result

def compress_string(text: str, method: str = 'gzip', level: int = DEFAULT_COMPRESSION_LEVEL) -> str:
    """
    Compress a string and return a base64 encoded string
    
    Args:
        text: String to compress
        method: Compression method (gzip, deflate, br)
        level: Compression level
        
    Returns:
        Base64 encoded compressed string
    """
    import base64
    data = text.encode('utf-8')
    
    if method == 'gzip':
        buffer = BytesIO()
        with gzip.GzipFile(mode='wb', compresslevel=level, fileobj=buffer) as f:
            f.write(data)
        compressed = buffer.getvalue()
    elif method == 'deflate':
        compressed = zlib.compress(data, level)
    elif method == 'br':
        compressed = brotli.compress(data, quality=level)
    else:
        raise ValueError(f"Unsupported compression method: {method}")
        
    return base64.b64encode(compressed).decode('ascii')

def decompress_string(compressed_data: str, method: str = 'gzip') -> str:
    """
    Decompress a base64 encoded compressed string
    
    Args:
        compressed_data: Base64 encoded compressed data
        method: Compression method (gzip, deflate, br)
        
    Returns:
        Decompressed string
    """
    import base64
    data = base64.b64decode(compressed_data)
    
    if method == 'gzip':
        buffer = BytesIO(data)
        with gzip.GzipFile(fileobj=buffer, mode='rb') as f:
            decompressed = f.read()
    elif method == 'deflate':
        decompressed = zlib.decompress(data)
    elif method == 'br':
        decompressed = brotli.decompress(data)
    else:
        raise ValueError(f"Unsupported compression method: {method}")
        
    return decompressed.decode('utf-8') 