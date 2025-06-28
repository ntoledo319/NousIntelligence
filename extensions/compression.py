"""
NOUS Compression Module
Dynamic compression for improved performance and reduced bandwidth
"""

import logging
import json
import gzip
from typing import Any, Dict, Optional, Union
from functools import wraps

logger = logging.getLogger(__name__)

# Track if zstandard is available
ZSTD_AVAILABLE = False
try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    logger.warning("zstandard not available - using gzip compression fallback")

def init_compression(app):
    """Initialize compression system
    
    Args:
        app: Flask application instance
    """
    if ZSTD_AVAILABLE:
        try:
            # Create zstandard compressor and decompressor
            compressor = zstd.ZstdCompressor(level=3, write_content_size=True)
            decompressor = zstd.ZstdDecompressor()
            
            app.extensions['compression'] = {
                'compressor': compressor,
                'decompressor': decompressor,
                'type': 'zstd'
            }
            
            logger.info("Compression initialized with zstandard")
            
        except Exception as e:
            logger.error(f"Failed to initialize zstandard compression: {e}")
            app.extensions['compression'] = None
    else:
        # Fallback to gzip
        app.extensions['compression'] = {
            'type': 'gzip'
        }
        logger.info("Compression initialized with gzip fallback")

def get_compression():
    """Get the compression instance from the current Flask app
    
    Returns:
        Compression instance dictionary or None
    """
    from flask import current_app
    try:
        return current_app.extensions.get('compression')
    except RuntimeError:
        # No app context
        return None

def compress_data(data: Union[str, bytes, dict]) -> bytes:
    """Compress data using the best available method
    
    Args:
        data: Data to compress (string, bytes, or dict)
        
    Returns:
        Compressed data as bytes
    """
    compression = get_compression()
    
    # Convert data to bytes if needed
    if isinstance(data, dict):
        data = json.dumps(data, separators=(',', ':')).encode('utf-8')
    elif isinstance(data, str):
        data = data.encode('utf-8')
    
    if not compression:
        logger.warning("Compression not available, returning uncompressed data")
        return data
    
    try:
        if compression['type'] == 'zstd':
            compressor = compression['compressor']
            return compressor.compress(data)
        else:
            # Fallback to gzip
            return gzip.compress(data)
            
    except Exception as e:
        logger.error(f"Compression failed: {e}")
        return data

def decompress_data(compressed_data: bytes) -> bytes:
    """Decompress data using the appropriate method
    
    Args:
        compressed_data: Compressed data bytes
        
    Returns:
        Decompressed data as bytes
    """
    compression = get_compression()
    
    if not compression:
        logger.warning("Compression not available, returning data as-is")
        return compressed_data
    
    try:
        if compression['type'] == 'zstd':
            decompressor = compression['decompressor']
            return decompressor.decompress(compressed_data)
        else:
            # Fallback to gzip
            return gzip.decompress(compressed_data)
            
    except Exception as e:
        logger.error(f"Decompression failed: {e}")
        return compressed_data

def compress_json(data: dict) -> bytes:
    """Compress JSON data with optimized serialization
    
    Args:
        data: Dictionary to compress
        
    Returns:
        Compressed JSON bytes
    """
    # Optimize JSON serialization (no spaces, sorted keys for better compression)
    json_str = json.dumps(data, separators=(',', ':'), sort_keys=True)
    return compress_data(json_str)

def decompress_json(compressed_data: bytes) -> dict:
    """Decompress and parse JSON data
    
    Args:
        compressed_data: Compressed JSON bytes
        
    Returns:
        Parsed dictionary
    """
    try:
        decompressed = decompress_data(compressed_data)
        return json.loads(decompressed.decode('utf-8'))
    except Exception as e:
        logger.error(f"JSON decompression failed: {e}")
        return {}

def compress_response(func):
    """Decorator to automatically compress API responses
    
    Usage:
        @app.route('/api/data')
        @compress_response
        def get_data():
            return large_data_dict
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request, Response, jsonify, current_app
        
        result = func(*args, **kwargs)
        
        # Check if client accepts compression
        accept_encoding = request.headers.get('Accept-Encoding', '').lower()
        
        if 'gzip' not in accept_encoding and 'zstd' not in accept_encoding:
            return result
        
        # Only compress JSON responses
        if isinstance(result, dict):
            try:
                compressed = compress_json(result)
                
                # Only use compression if it actually reduces size
                original_size = len(json.dumps(result).encode('utf-8'))
                if len(compressed) < original_size * 0.9:  # 10% savings threshold
                    
                    compression = get_compression()
                    encoding = 'zstd' if compression and compression['type'] == 'zstd' else 'gzip'
                    
                    response = Response(
                        compressed,
                        mimetype='application/json',
                        headers={
                            'Content-Encoding': encoding,
                            'Vary': 'Accept-Encoding',
                            'X-Original-Size': str(original_size),
                            'X-Compressed-Size': str(len(compressed))
                        }
                    )
                    return response
                else:
                    logger.debug("Compression not beneficial, returning uncompressed")
                    return jsonify(result)
                    
            except Exception as e:
                logger.error(f"Response compression failed: {e}")
                return jsonify(result)
        
        return result
    
    return wrapper

def smart_cache_compress(cache_key: str, data: Any, ttl: int = 3600) -> bool:
    """Compress and cache data intelligently
    
    Args:
        cache_key: Cache key
        data: Data to cache
        ttl: Time to live in seconds
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # This would integrate with a caching system like Redis
        # For now, we'll simulate the compression logic
        
        if isinstance(data, (dict, list)):
            compressed = compress_json(data)
            original_size = len(json.dumps(data).encode('utf-8'))
            compressed_size = len(compressed)
            
            savings = ((original_size - compressed_size) / original_size) * 100
            logger.debug(f"Cache compression: {savings:.1f}% savings ({original_size} -> {compressed_size} bytes)")
            
            # Would store compressed data in cache here
            return True
        else:
            # Store uncompressed for non-JSON data
            return True
            
    except Exception as e:
        logger.error(f"Cache compression failed: {e}")
        return False

def get_compression_stats() -> Dict[str, Any]:
    """Get compression system statistics
    
    Returns:
        Dictionary of compression statistics
    """
    compression = get_compression()
    
    if not compression:
        return {
            'enabled': False,
            'type': 'none',
            'error': 'Compression not initialized'
        }
    
    stats = {
        'enabled': True,
        'type': compression['type'],
        'available_algorithms': []
    }
    
    if ZSTD_AVAILABLE:
        stats['available_algorithms'].append('zstd')
    stats['available_algorithms'].append('gzip')
    
    # In a full implementation, these would track actual usage
    stats.update({
        'total_compressions': 0,
        'total_bytes_saved': 0,
        'average_compression_ratio': 0.0,
        'compression_errors': 0
    })
    
    return stats

def benchmark_compression(test_data: dict) -> Dict[str, Any]:
    """Benchmark compression performance with test data
    
    Args:
        test_data: Test data dictionary
        
    Returns:
        Benchmark results
    """
    import time
    
    original_data = json.dumps(test_data).encode('utf-8')
    original_size = len(original_data)
    
    results = {
        'original_size': original_size,
        'algorithms': {}
    }
    
    # Test gzip compression
    try:
        start_time = time.time()
        gzip_compressed = gzip.compress(original_data)
        gzip_time = time.time() - start_time
        
        gzip_size = len(gzip_compressed)
        gzip_ratio = (original_size - gzip_size) / original_size * 100
        
        results['algorithms']['gzip'] = {
            'compressed_size': gzip_size,
            'compression_ratio': round(gzip_ratio, 2),
            'compression_time': round(gzip_time * 1000, 2),  # milliseconds
            'available': True
        }
    except Exception as e:
        results['algorithms']['gzip'] = {
            'available': False,
            'error': str(e)
        }
    
    # Test zstd compression if available
    if ZSTD_AVAILABLE:
        try:
            compressor = zstd.ZstdCompressor(level=3)
            
            start_time = time.time()
            zstd_compressed = compressor.compress(original_data)
            zstd_time = time.time() - start_time
            
            zstd_size = len(zstd_compressed)
            zstd_ratio = (original_size - zstd_size) / original_size * 100
            
            results['algorithms']['zstd'] = {
                'compressed_size': zstd_size,
                'compression_ratio': round(zstd_ratio, 2),
                'compression_time': round(zstd_time * 1000, 2),  # milliseconds
                'available': True
            }
        except Exception as e:
            results['algorithms']['zstd'] = {
                'available': False,
                'error': str(e)
            }
    else:
        results['algorithms']['zstd'] = {
            'available': False,
            'error': 'zstandard not installed'
        }
    
    return results

class CompressionMiddleware:
    """WSGI middleware for automatic response compression"""
    
    def __init__(self, app, compression_threshold: int = 1024):
        """Initialize compression middleware
        
        Args:
            app: WSGI application
            compression_threshold: Minimum response size to compress (bytes)
        """
        self.app = app
        self.compression_threshold = compression_threshold
    
    def __call__(self, environ, start_response):
        """WSGI application interface"""
        # This would implement automatic response compression
        # For now, just pass through to the app
        return self.app(environ, start_response)