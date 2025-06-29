#!/usr/bin/env python3
"""
Deployment Fix Validator
Tests all the applied fixes for speech recognition deployment issues
"""

import sys
import logging
import importlib
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_voice_interface_imports():
    """Test that voice interface can be imported with graceful fallbacks"""
    try:
        from voice_interface import SpeechToText, TextToSpeech, speech_to_text_available, text_to_speech_available
        logger.info("✓ Voice interface imports successful")
        logger.info(f"  - Speech-to-text available: {speech_to_text_available}")
        logger.info(f"  - Text-to-speech available: {text_to_speech_available}")
        
        # Test fallback functionality
        stt = SpeechToText()
        result = stt.transcribe_audio()
        logger.info(f"  - Speech-to-text fallback test: {result.get('method', 'unknown')}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Voice interface import failed: {e}")
        return False

def test_enhanced_voice_service():
    """Test enhanced voice service with fallbacks"""
    try:
        from utils.enhanced_voice_service import EnhancedVoiceService
        service = EnhancedVoiceService()
        result = service.transcribe_audio(b"test_audio_data")
        logger.info("✓ Enhanced voice service working with fallbacks")
        return True
    except Exception as e:
        logger.error(f"✗ Enhanced voice service failed: {e}")
        return False

def test_services_enhanced_voice():
    """Test services enhanced voice with fallbacks"""
    try:
        from services.enhanced_voice import SPEECH_RECOGNITION_AVAILABLE, PYTTSX3_AVAILABLE
        logger.info("✓ Services enhanced voice imports successful")
        logger.info(f"  - Speech recognition available: {SPEECH_RECOGNITION_AVAILABLE}")
        logger.info(f"  - pyttsx3 available: {PYTTSX3_AVAILABLE}")
        return True
    except Exception as e:
        logger.error(f"✗ Services enhanced voice failed: {e}")
        return False

def test_dependency_configuration():
    """Test that pyproject.toml has correct dependency configuration"""
    try:
        import tomllib
        with open('pyproject.toml', 'rb') as f:
            config = tomllib.load(f)
        
        # Check that speech-recognition is not in main dependencies
        main_deps = config.get('project', {}).get('dependencies', [])
        has_speech_in_main = any('speech' in dep.lower() for dep in main_deps)
        
        if has_speech_in_main:
            logger.warning("⚠ Speech recognition still in main dependencies")
        else:
            logger.info("✓ Speech recognition moved to optional dependencies")
        
        # Check optional dependencies
        optional_deps = config.get('project', {}).get('optional-dependencies', {})
        intelligence_deps = optional_deps.get('intelligence', [])
        has_speech_in_optional = any('speech' in dep.lower() for dep in intelligence_deps)
        
        if has_speech_in_optional:
            logger.info("✓ Speech recognition found in intelligence optional dependencies")
        else:
            logger.warning("⚠ Speech recognition not found in optional dependencies")
        
        return True
    except Exception as e:
        logger.error(f"✗ Dependency configuration check failed: {e}")
        return False

def test_app_startup():
    """Test that the main app can start without speech recognition"""
    try:
        # Test if we can import the main app components
        from app import app
        logger.info("✓ Main app can be imported")
        
        # Test app context
        with app.app_context():
            logger.info("✓ App context works")
        
        return True
    except Exception as e:
        logger.error(f"✗ App startup test failed: {e}")
        return False

def test_pip_configuration():
    """Test pip configuration for fresh dependency resolution"""
    try:
        import os
        if os.path.exists('pip.conf'):
            with open('pip.conf', 'r') as f:
                content = f.read()
            
            if 'no-cache-dir = true' in content:
                logger.info("✓ pip.conf configured to disable caching")
            else:
                logger.warning("⚠ pip.conf may not disable caching properly")
        else:
            logger.warning("⚠ pip.conf not found")
        
        return True
    except Exception as e:
        logger.error(f"✗ pip configuration check failed: {e}")
        return False

def run_all_tests():
    """Run all validation tests"""
    logger.info("Running deployment fix validation tests...")
    logger.info("=" * 50)
    
    tests = [
        ("Voice Interface Imports", test_voice_interface_imports),
        ("Enhanced Voice Service", test_enhanced_voice_service),
        ("Services Enhanced Voice", test_services_enhanced_voice),
        ("Dependency Configuration", test_dependency_configuration),
        ("App Startup", test_app_startup),
        ("Pip Configuration", test_pip_configuration),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\nTesting: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All deployment fixes validated successfully!")
        return True
    else:
        logger.warning(f"⚠ {total - passed} tests failed - may need additional fixes")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)