
"""Google Generative AI Fallback"""
import logging

logger = logging.getLogger(__name__)

class GenerativeModel:
    def __init__(self, model_name="gemini-pro"):
        self.model_name = model_name
        logger.warning("Using fallback Gemini API - responses will be mock")
    
    def generate_content(self, prompt):
        return MockResponse("I'm currently unavailable. Please check your API configuration.")

class MockResponse:
    def __init__(self, text):
        self.text = text
        self.candidates = [MockCandidate(text)]

class MockCandidate:
    def __init__(self, text):
        self.content = MockContent(text)

class MockContent:
    def __init__(self, text):
        self.parts = [MockPart(text)]

class MockPart:
    def __init__(self, text):
        self.text = text

def configure(api_key=None):
    logger.warning("Gemini API configuration - using fallback mode")
    pass

# Make available as google.generativeai
import sys
if 'google' not in sys.modules:
    sys.modules['google'] = type('MockModule', (), {})()
if 'google.generativeai' not in sys.modules:
    current_module = sys.modules[__name__]
    sys.modules['google.generativeai'] = current_module
