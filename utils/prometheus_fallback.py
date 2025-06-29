
"""Prometheus Client Fallback"""
import logging
import time

logger = logging.getLogger(__name__)

class Counter:
    def __init__(self, name, documentation, **kwargs):
        self.name = name
        self._value = 0
        logger.debug(f"Mock counter created: {name}")
    
    def inc(self, amount=1):
        self._value += amount
    
    def labels(self, **kwargs):
        return self

class Histogram:
    def __init__(self, name, documentation, **kwargs):
        self.name = name
        self._observations = []
        logger.debug(f"Mock histogram created: {name}")
    
    def observe(self, amount):
        self._observations.append(amount)
    
    def time(self):
        return MockTimer()
    
    def labels(self, **kwargs):
        return self

class MockTimer:
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        pass

def generate_latest(registry=None):
    return "# Mock Prometheus metrics\n"

def start_http_server(port, addr=''):
    logger.warning(f"Mock Prometheus server would start on {addr}:{port}")

# Make available as prometheus_client
import sys
current_module = sys.modules[__name__]
sys.modules['prometheus_client'] = current_module
