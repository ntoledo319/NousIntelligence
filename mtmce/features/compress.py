"""
MTM-CE Compression Module
High-performance data compression using zstandard for optimized data transfer
"""

import logging
from typing import Union, Optional

logger = logging.getLogger(__name__)

# Try to import zstandard, gracefully degrade if not available
try:
    import zstandard as zstd
    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False
    logger.warning("zstandard not available - compression will use fallback")

def init_compression(app):
    """Initialize compression system with zstandard"""
    if not ZSTD_AVAILABLE:
        logger.warning("zstandard not available, using mock compression")
        app.compressor = MockCompressor()
        app.decompressor = MockDecompressor()
        return
        
    try:
        # Initialize zstandard compressor with optimal settings
        compression_level = app.config.get('COMPRESSION_LEVEL', 3)
        app.compressor = zstd.ZstdCompressor(
            level=compression_level,
            write_content_size=True,
            write_checksum=True
        )
        app.decompressor = zstd.ZstdDecompressor()
        
        logger.info(f"zstandard compression initialized with level {compression_level}")
        
    except Exception as e:
        logger.error(f"Failed to initialize compression: {e}")
        # Fallback to mock compression
        app.compressor = MockCompressor()
        app.decompressor = MockDecompressor()

def compress_data(data: Union[str, bytes]) -> bytes:
    """Compress data using zstandard"""
    try:
        from flask import current_app
        
        # Convert string to bytes if necessary
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        # Use the app's compressor
        compressed = current_app.compressor.compress(data)
        
        # Log compression ratio for monitoring
        original_size = len(data)
        compressed_size = len(compressed)
        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        logger.debug(f"Compressed {original_size} bytes to {compressed_size} bytes ({ratio:.1f}% reduction)")
        
        return compressed
        
    except Exception as e:
        logger.error(f"Compression failed: {e}")
        # Return original data if compression fails
        if isinstance(data, str):
            return data.encode('utf-8')
        return data

def decompress_data(blob: bytes) -> bytes:
    """Decompress data using zstandard"""
    try:
        from flask import current_app
        
        # Use the app's decompressor
        decompressed = current_app.decompressor.decompress(blob)
        
        logger.debug(f"Decompressed {len(blob)} bytes to {len(decompressed)} bytes")
        
        return decompressed
        
    except Exception as e:
        logger.error(f"Decompression failed: {e}")
        # Return original data if decompression fails
        return blob

def compress_json(data: dict) -> bytes:
    """Compress JSON data with optimal settings"""
    import json
    
    try:
        # Convert to JSON string
        json_string = json.dumps(data, separators=(',', ':'))
        
        # Compress the JSON string
        return compress_data(json_string)
        
    except Exception as e:
        logger.error(f"JSON compression failed: {e}")
        return json.dumps(data).encode('utf-8')

def decompress_json(blob: bytes) -> dict:
    """Decompress and parse JSON data"""
    import json
    
    try:
        # Decompress the data
        decompressed = decompress_data(blob)
        
        # Parse JSON
        return json.loads(decompressed.decode('utf-8'))
        
    except Exception as e:
        logger.error(f"JSON decompression failed: {e}")
        return {}

def get_compression_stats() -> dict:
    """Get compression statistics"""
    try:
        from flask import current_app
        
        if hasattr(current_app, 'compressor') and ZSTD_AVAILABLE:
            return {
                'compression_available': True,
                'compression_level': current_app.compressor.level if hasattr(current_app.compressor, 'level') else 'unknown',
                'algorithm': 'zstandard'
            }
        else:
            return {
                'compression_available': False,
                'algorithm': 'mock'
            }
            
    except Exception as e:
        logger.error(f"Failed to get compression stats: {e}")
        return {'compression_available': False, 'error': str(e)}

class MockCompressor:
    """Mock compressor for graceful degradation"""
    
    def __init__(self):
        self.level = 0
        
    def compress(self, data: bytes) -> bytes:
        """Mock compression - returns original data"""
        logger.debug("Mock compression: returning original data")
        return data

class MockDecompressor:
    """Mock decompressor for graceful degradation"""
    
    def decompress(self, blob: bytes) -> bytes:
        """Mock decompression - returns original data"""
        logger.debug("Mock decompression: returning original data")
        return blob

def smart_compress(data: Union[str, bytes, dict], threshold: int = 1024) -> tuple:
    """Smart compression that only compresses if data exceeds threshold"""
    original_data = data
    
    # Convert to bytes for size calculation
    if isinstance(data, dict):
        import json
        data_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
    elif isinstance(data, str):
        data_bytes = data.encode('utf-8')
    else:
        data_bytes = data
    
    # Only compress if data exceeds threshold
    if len(data_bytes) > threshold:
        compressed = compress_data(data_bytes)
        return compressed, True
    else:
        return data_bytes, False

def smart_decompress(data: bytes, was_compressed: bool) -> bytes:
    """Smart decompression that only decompresses if data was compressed"""
    if was_compressed:
        return decompress_data(data)
    else:
        return data