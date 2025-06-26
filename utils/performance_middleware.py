"""
Performance Middleware

This module provides middleware for optimizing request processing and response time.
It includes request timing, response compression, and caching headers.

@module utils.performance_middleware
@description Performance optimization middleware
"""

import time
import logging
import gzip
import io
from typing import Callable, Dict, List, Optional, Any
from flask import Flask, request, Response, g
from werkzeug.middleware.proxy_fix import ProxyFix

logger = logging.getLogger(__name__)

# List of content types to compress
COMPRESSIBLE_TYPES = [
    'text/html',
    'text/css',
    'text/javascript',
    'application/javascript',
    'application/json',
    'application/xml',
    'text/xml',
    'text/plain'
]

# Cache configuration by content type
CACHE_CONFIG = {
    'text/html': 0,  # No caching for HTML
    'text/css': 86400,  # 1 day for CSS
    'text/javascript': 86400,  # 1 day for JS
    'application/javascript': 86400,  # 1 day for JS
    'image/': 604800,  # 1 week for images
    'font/': 604800,  # 1 week for fonts
    'application/font': 604800,  # 1 week for fonts
}

def setup_performance_middleware(app: Flask) -> None:
    """
    Set up performance middleware for the Flask application

    Args:
        app: Flask application instance
    """
    # Apply ProxyFix for proper URL generation with HTTPS
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Add before_request handler for request timing
    @app.before_request
    def start_timer() -> None:
        """Start request timer"""
        g.start_time = time.time()

    # Add after_request handler for response optimization
    @app.after_request
    def optimize_response(response: Response) -> Response:
        """
        Optimize response with compression and cache headers

        Args:
            response: Flask response object

        Returns:
            Optimized response
        """
        # Skip if no start time (rare edge case)
        if not hasattr(g, 'start_time'):
            return response

        # Calculate processing time
        processing_time = time.time() - g.start_time

        # Log slow requests
        if processing_time > 0.5:  # More than 500ms
            logger.warning(f"Slow request: {request.path} took {processing_time:.3f}s")

        # Add processing time header
        response.headers['X-Processing-Time'] = f"{processing_time:.3f}s"

        # Apply compression if appropriate
        if should_compress(request, response):
            response = compress_response(response)

        # Apply cache headers if not already set
        if 'Cache-Control' not in response.headers:
            add_cache_headers(response)

        return response

    logger.info("Performance middleware initialized")

def should_compress(request, response: Response) -> bool:
    """
    Determine if a response should be compressed

    Args:
        request: Flask request object
        response: Flask response object

    Returns:
        True if should compress, False otherwise
    """
    # Skip if response is already compressed
    if 'Content-Encoding' in response.headers:
        return False

    # Check if client accepts gzip
    if 'gzip' not in request.headers.get('Accept-Encoding', ''):
        return False

    # Check response size (don't compress small responses)
    if response.content_length is not None and response.content_length < 500:
        return False

    # Check content type
    content_type = response.headers.get('Content-Type', '')
    return any(ct in content_type for ct in COMPRESSIBLE_TYPES)

def compress_response(response: Response) -> Response:
    """
    Compress response with gzip

    Args:
        response: Flask response object

    Returns:
        Compressed response
    """
    # Skip if no direct_passthrough (e.g., file responses)
    if not response.direct_passthrough:
        try:
            gzip_buffer = io.BytesIO()
            gzip_file = gzip.GzipFile(mode='wb', fileobj=gzip_buffer)
            gzip_file.write(response.get_data())
            gzip_file.close()

            response.set_data(gzip_buffer.getvalue())
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response.get_data())
            response.headers.add('Vary', 'Accept-Encoding')
        except Exception as e:
            logger.error(f"Compression error: {str(e)}")

    return response

def add_cache_headers(response: Response) -> None:
    """
    Add appropriate cache headers based on content type

    Args:
        response: Flask response object
    """
    content_type = response.headers.get('Content-Type', '')

    # Default: no caching
    max_age = 0

    # Check for cache config match
    for type_prefix, cache_age in CACHE_CONFIG.items():
        if type_prefix in content_type:
            max_age = cache_age
            break

    # Set cache headers
    if max_age > 0:
        response.headers['Cache-Control'] = f'public, max-age={max_age}'
    else:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'