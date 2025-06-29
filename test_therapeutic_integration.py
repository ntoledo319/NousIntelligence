#!/usr/bin/env python3
"""
Test script for emotion-aware therapeutic integration
Tests the core functionality without requiring full Flask app startup
"""

import sys
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_emotion_detection():
    """Test basic emotion detection functionality"""
    try:
        # Try importing emotion detection
        from utils.emotion_detection import detect_emotion_from_text
        
        # Test emotion detection
        test_phrases = [
            "I'm feeling really anxious about tomorrow",
            "I'm so angry right now, everything is wrong", 
            "I feel sad and hopeless",
            "I'm really happy today!",
            "I feel overwhelmed with everything"
        ]
        
        results = []
        for phrase in test_phrases:
            try:
                emotion_result = detect_emotion_from_text(phrase)
                results.append({
                    'phrase': phrase,
                    'emotion': emotion_result.get('emotion', 'unknown'),
                    'confidence': emotion_result.get('confidence', 0)
                })
                print(f"✓ '{phrase}' → {emotion_result.get('emotion')} ({emotion_result.get('confidence', 0):.2f})")
            except Exception as e:
                print(f"✗ Error analyzing '{phrase}': {e}")
        
        return len(results) > 0
        
    except ImportError as e:
        print(f"✗ Cannot import emotion detection: {e}")
        return False

def test_therapeutic_assistant():
    """Test therapeutic assistant instantiation"""
    try:
        from services.emotion_aware_therapeutic_assistant import therapeutic_assistant
        
        # Test basic functionality
        print("✓ Therapeutic assistant imported successfully")
        
        # Test emotion to skill mapping
        if hasattr(therapeutic_assistant, 'emotion_skill_mapping'):
            print(f"✓ Emotion skill mapping loaded with {len(therapeutic_assistant.emotion_skill_mapping)} emotions")
            
            # Show mapping
            for emotion, skills in therapeutic_assistant.emotion_skill_mapping.items():
                print(f"  - {emotion}: {', '.join(skills.get('dbt', [])[:2])}")
        
        # Test tone mapping
        if hasattr(therapeutic_assistant, 'therapeutic_tones'):
            print(f"✓ Therapeutic tones loaded with {len(therapeutic_assistant.therapeutic_tones)} tone mappings")
        
        return True
        
    except ImportError as e:
        print(f"✗ Cannot import therapeutic assistant: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing therapeutic assistant: {e}")
        return False

def test_skill_recommendations():
    """Test skill recommendation logic"""
    try:
        from services.emotion_aware_therapeutic_assistant import therapeutic_assistant
        
        # Test emotion to skill mapping
        test_emotions = ['anxious', 'angry', 'sad', 'distressed']
        
        for emotion in test_emotions:
            if emotion in therapeutic_assistant.emotion_skill_mapping:
                skills = therapeutic_assistant.emotion_skill_mapping[emotion]
                dbt_skills = skills.get('dbt', [])
                cbt_skills = skills.get('cbt', [])
                print(f"✓ {emotion.title()} emotion:")
                print(f"  DBT skills: {', '.join(dbt_skills[:3])}")
                print(f"  CBT skills: {', '.join(cbt_skills[:3])}")
            else:
                print(f"✗ No skills mapped for {emotion}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing skill recommendations: {e}")
        return False

def test_therapeutic_tones():
    """Test therapeutic tone adaptation"""
    try:
        from services.emotion_aware_therapeutic_assistant import therapeutic_assistant
        
        print("✓ Therapeutic tone adaptations:")
        for emotion, tone in therapeutic_assistant.therapeutic_tones.items():
            print(f"  - {emotion}: {tone}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing therapeutic tones: {e}")
        return False

def test_api_structure():
    """Test API endpoint structure"""
    try:
        from api.therapeutic_chat import therapeutic_chat_bp
        
        print("✓ Therapeutic chat blueprint imported successfully")
        print(f"✓ Blueprint name: {therapeutic_chat_bp.name}")
        print(f"✓ Blueprint URL prefix: {therapeutic_chat_bp.url_prefix}")
        
        # Check if blueprint has routes
        if hasattr(therapeutic_chat_bp, 'deferred_functions'):
            print(f"✓ Blueprint has {len(therapeutic_chat_bp.deferred_functions)} route functions")
        
        return True
        
    except ImportError as e:
        print(f"✗ Cannot import therapeutic chat blueprint: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing API structure: {e}")
        return False

def test_template_exists():
    """Test if therapeutic chat template exists"""
    try:
        template_path = "templates/emotion_aware_chat.html"
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Check for key features
            features = [
                'emotion-indicator',
                'skill-suggestions', 
                'voice-controls',
                'therapeutic-chat',
                'crisis-alert'
            ]
            
            found_features = []
            for feature in features:
                if feature in content:
                    found_features.append(feature)
            
            print(f"✓ Template exists with {len(found_features)}/{len(features)} key features:")
            for feature in found_features:
                print(f"  - {feature}")
            
            return len(found_features) >= 3
        else:
            print(f"✗ Template not found at {template_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error checking template: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("EMOTION-AWARE THERAPEUTIC INTEGRATION TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Emotion Detection", test_emotion_detection),
        ("Therapeutic Assistant", test_therapeutic_assistant),
        ("Skill Recommendations", test_skill_recommendations),
        ("Therapeutic Tones", test_therapeutic_tones),
        ("API Structure", test_api_structure),
        ("Template Existence", test_template_exists)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        print("-" * 40)
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Emotion-aware therapeutic integration is working!")
    elif passed >= total * 0.7:
        print("⚠️  MOSTLY WORKING - Some components may need attention")
    else:
        print("❌ MAJOR ISSUES - Integration needs significant work")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)