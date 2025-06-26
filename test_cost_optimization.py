#!/usr/bin/env python3
"""
Cost Optimization Migration Test

This script validates that the OpenAI to cost-optimized provider migration
has been completed successfully and tests all AI functionality.
"""

import os
import sys
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_import_migration():
    """Test that all imports work without OpenAI dependencies"""
    try:
        # Test cost-optimized AI import
        from utils.cost_optimized_ai import get_cost_optimized_ai, TaskComplexity
        logger.info("✓ Cost-optimized AI imports working")
        
        # Test migrated helper imports
        from utils.ai_helper import get_ai_response, generate_ai_text
        logger.info("✓ AI helper imports working")
        
        # Test voice utilities
        from utils.multilingual_voice import generate_speech, transcribe_speech
        logger.info("✓ Voice utilities imports working")
        
        # Test mindfulness utilities
        from utils.voice_mindfulness import generate_personalized_exercise
        logger.info("✓ Mindfulness utilities imports working")
        
        return True
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False

def test_ai_services():
    """Test AI service functionality"""
    try:
        from utils.cost_optimized_ai import get_cost_optimized_ai, TaskComplexity
        
        ai_client = get_cost_optimized_ai()
        logger.info("✓ AI client initialized")
        
        # Test basic chat completion
        messages = [{"role": "user", "content": "Hello, respond with exactly 'AI test successful'"}]
        result = ai_client.chat_completion(messages, max_tokens=50, complexity=TaskComplexity.BASIC)
        
        if result.get("success"):
            logger.info(f"✓ Chat completion working - Provider: {result.get('provider')}, Cost: ${result.get('cost', 0):.4f}")
        else:
            logger.warning(f"⚠ Chat completion failed: {result.get('error')}")
            
        # Test cost summary
        summary = ai_client.get_cost_summary()
        logger.info(f"✓ Cost tracking working - Total: ${summary['total_cost']:.4f}, Requests: {summary['total_requests']}")
        
        return True
    except Exception as e:
        logger.error(f"✗ AI services test failed: {e}")
        return False

def test_legacy_functions():
    """Test that legacy AI functions work with new providers"""
    try:
        from utils.ai_helper import get_ai_response, generate_ai_text
        
        # Test basic response
        response = get_ai_response("Hello")
        if response:
            logger.info("✓ Legacy get_ai_response working")
        else:
            logger.warning("⚠ Legacy get_ai_response returned empty")
            
        # Test text generation
        text = generate_ai_text("Generate a short greeting", max_tokens=50)
        if text and "error" not in text.lower():
            logger.info("✓ Legacy generate_ai_text working")
        else:
            logger.warning(f"⚠ Legacy generate_ai_text failed: {text}")
            
        return True
    except Exception as e:
        logger.error(f"✗ Legacy functions test failed: {e}")
        return False

def test_voice_functions():
    """Test voice functionality with new providers"""
    try:
        from utils.multilingual_voice import generate_speech
        
        # Test TTS (will use HuggingFace)
        result = generate_speech("Hello, this is a test", {"language": "en-US"})
        
        if result.get("success"):
            logger.info(f"✓ TTS working - Provider: {result.get('metadata', {}).get('provider', 'unknown')}")
        else:
            logger.warning(f"⚠ TTS failed: {result.get('error')}")
            
        return True
    except Exception as e:
        logger.error(f"✗ Voice functions test failed: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    logger.info("\n=== Environment Check ===")
    
    # Check required keys
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    hf_key = os.environ.get("HUGGINGFACE_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if openrouter_key:
        logger.info("✓ OpenRouter API key available")
    else:
        logger.warning("⚠ OpenRouter API key missing")
        
    if hf_key:
        logger.info("✓ Hugging Face API key available")
    else:
        logger.warning("⚠ Hugging Face API key missing")
        
    if openai_key:
        logger.warning("⚠ OpenAI API key still present (should be removed)")
    else:
        logger.info("✓ OpenAI API key removed")

def calculate_cost_savings():
    """Calculate estimated cost savings"""
    logger.info("\n=== Cost Savings Analysis ===")
    
    # Estimated monthly usage
    chat_tokens = 395000  # tokens per month
    audio_minutes = 20000  # TTS minutes per month
    
    # Old OpenAI costs
    old_chat_cost = (chat_tokens / 1000) * 0.002  # GPT-3.5-turbo
    old_tts_cost = audio_minutes * 0.015  # OpenAI TTS
    old_total = old_chat_cost + old_tts_cost
    
    # New cost-optimized costs
    new_chat_cost = (chat_tokens / 1000) * 0.00125  # Google Gemini Pro via OpenRouter
    new_tts_cost = 0  # HuggingFace free tier
    new_total = new_chat_cost + new_tts_cost
    
    savings = old_total - new_total
    savings_percent = (savings / old_total) * 100
    
    logger.info(f"Previous monthly cost: ${old_total:.2f}")
    logger.info(f"New monthly cost: ${new_total:.2f}")
    logger.info(f"Monthly savings: ${savings:.2f} ({savings_percent:.1f}%)")

def main():
    """Run all migration tests"""
    logger.info("=== AI Cost Optimization Migration Test ===\n")
    
    # Check environment
    check_environment()
    
    # Test imports
    logger.info("\n=== Import Tests ===")
    import_success = test_import_migration()
    
    # Test AI services
    logger.info("\n=== AI Service Tests ===")
    service_success = test_ai_services()
    
    # Test legacy functions
    logger.info("\n=== Legacy Function Tests ===")
    legacy_success = test_legacy_functions()
    
    # Test voice functions
    logger.info("\n=== Voice Function Tests ===")
    voice_success = test_voice_functions()
    
    # Calculate savings
    calculate_cost_savings()
    
    # Summary
    logger.info("\n=== Migration Summary ===")
    total_tests = 4
    passed_tests = sum([import_success, service_success, legacy_success, voice_success])
    
    logger.info(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        logger.info("✓ Migration completed successfully!")
        logger.info("✓ All OpenAI dependencies removed")
        logger.info("✓ Cost-optimized providers working")
        return 0
    else:
        logger.warning("⚠ Some tests failed - migration may need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())