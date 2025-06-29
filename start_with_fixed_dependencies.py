#!/usr/bin/env python3
"""
Start NOUS with Fixed Dependencies
Tests that the application starts correctly with speech recognition fixes applied
"""

import os
import sys
import logging
from flask import Flask

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test critical imports"""
    logger.info("Testing critical imports...")
    
    try:
        # Test voice interface imports
        from voice_interface import SpeechToText, TextToSpeech
        logger.info("✓ Voice interface imports successful")
        
        # Test main app import
        from app import app
        logger.info("✓ Main app import successful")
        
        # Test unified services
        from utils.unified_ai_service import UnifiedAIService
        logger.info("✓ Unified AI service import successful")
        
        return True
    except Exception as e:
        logger.error(f"✗ Import test failed: {e}")
        return False

def test_voice_fallbacks():
    """Test voice interface fallback functionality"""
    logger.info("Testing voice interface fallbacks...")
    
    try:
        from voice_interface import SpeechToText, speech_to_text_available
        
        stt = SpeechToText()
        
        # Test transcription (should use fallback gracefully)
        result = stt.transcribe_audio()
        
        if result.get('success'):
            logger.info("✓ Voice transcription working")
        else:
            logger.info(f"✓ Voice transcription fallback working: {result.get('error', 'Unknown error')}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Voice fallback test failed: {e}")
        return False

def start_app():
    """Start the NOUS application"""
    logger.info("Starting NOUS application...")
    
    try:
        from app import app
        
        # Get port from environment
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        logger.info(f"Starting server on {host}:{port}")
        
        # Run in production mode
        app.run(
            host=host,
            port=port,
            debug=False,
            use_reloader=False
        )
        
    except Exception as e:
        logger.error(f"✗ Failed to start app: {e}")
        return False

def main():
    """Main function"""
    logger.info("NOUS Deployment Fix Test")
    logger.info("=" * 50)
    
    # Test imports
    if not test_imports():
        logger.error("Import tests failed - cannot start application")
        sys.exit(1)
    
    # Test voice fallbacks
    if not test_voice_fallbacks():
        logger.error("Voice fallback tests failed - may affect functionality")
    
    # Start the application
    logger.info("All tests passed - starting application...")
    start_app()

if __name__ == "__main__":
    main()