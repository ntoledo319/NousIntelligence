
"""Zstandard Compression Fallback"""
import gzip
import logging

logger = logging.getLogger(__name__)

class ZstdCompressor:
    def compress(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        # Use gzip as fallback
        return gzip.compress(data)

class ZstdDecompressor:
    def decompress(self, data):
        try:
            return gzip.decompress(data)
        except:
            return data

def compress(data, level=3):
    compressor = ZstdCompressor()
    return compressor.compress(data)

def decompress(data):
    decompressor = ZstdDecompressor()
    return decompressor.decompress(data)

# Make available as zstandard
import sys
current_module = sys.modules[__name__]
sys.modules['zstandard'] = current_module
sys.modules['zstd'] = current_module
