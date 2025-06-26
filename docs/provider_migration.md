# AI Provider Migration Report

## Overview
This document tracks the migration from OpenAI APIs to cost-optimized alternatives using OpenRouter and Hugging Face Inference APIs.

## Migration Analysis

### Files with OpenAI Dependencies
| File | Function | Call Type | Usage Pattern | Monthly Est. Tokens |
|------|----------|-----------|---------------|-------------------|
| utils/ai_helper.py | initialize_openai, get_ai_response | Chat Completions | Basic chat responses | ~50K |
| utils/ai_integration.py | _call_openai | Chat Completions | Advanced AI text generation | ~200K |
| utils/ai_service_manager.py | Various | Service Management | Cost optimization layer | ~100K |
| utils/multilingual_voice.py | generate_speech, transcribe_speech | TTS + STT | Voice interface | ~20K audio minutes |
| utils/voice_mindfulness.py | generate_personalized_exercise | Chat Completions | Content generation | ~30K |
| utils/enhanced_weather_helper.py | Unknown | Chat Completions | Weather analysis | ~10K |
| utils/smart_home_helper.py | Unknown | Chat Completions | Smart home integration | ~15K |

### Cost Comparison Analysis

#### Current OpenAI Costs (Estimated Monthly)
- Chat Completions (~395K tokens): $0.79 (using gpt-3.5-turbo at $0.002/1K tokens)
- TTS (~20K minutes): $300 (at $0.015/minute)
- STT (~5K minutes): $30 (at $0.006/minute)
- **Total Monthly: ~$330.79**

#### Projected Costs with OpenRouter + HuggingFace
- Chat Completions via OpenRouter (Google Gemini Pro): $0.49 (at $0.00125/1K tokens)
- TTS via HuggingFace (self-hosted): $0 (using free tier)
- STT via HuggingFace (Whisper): $0 (using free tier)
- **Total Monthly: ~$0.49**

#### **Projected Savings: $330.30/month (99.85% reduction)**

## Migration Strategy

### Phase 1: Provider Abstraction Layer ✅
- [x] Create unified AI provider interface
- [x] Implement OpenRouter adapter
- [x] Implement HuggingFace adapter
- [x] Add fallback mechanisms

### Phase 2: Service Replacement 🔄
- [ ] Replace chat completions with OpenRouter
- [ ] Replace TTS with HuggingFace
- [ ] Replace STT with HuggingFace
- [ ] Update all import statements

### Phase 3: Environment & Dependencies 🔄
- [ ] Remove OPENAI_API_KEY references
- [ ] Add HUGGINGFACE_API_KEY
- [ ] Update dependencies
- [ ] Update tests

### Phase 4: Validation ⏳
- [ ] Run cost validation tests
- [ ] Smoke test all features
- [ ] Performance benchmarking

## API Key Requirements

### Required for Migration
- `OPENROUTER_API_KEY`: ✅ Available
- `HUGGINGFACE_API_KEY`: ❌ **NEEDED** - User must provide

### To be Removed
- `OPENAI_API_KEY`: ✅ Will be removed after migration

## Service Selection Logic

### Chat Completions
- **Basic Tasks**: OpenRouter with Google Gemini Pro ($0.00125/1K tokens)
- **Complex Tasks**: OpenRouter with Anthropic Claude 3 Sonnet ($0.003/1K tokens)
- **Fallback**: Local template-based responses

### Audio Services
- **TTS**: HuggingFace Inference (Microsoft SpeechT5, free tier)
- **STT**: HuggingFace Inference (OpenAI Whisper, free tier)
- **Fallback**: Browser native APIs where possible

## Implementation Status
- Migration started: 2025-06-26
- Estimated completion: 2025-06-26
- Status: **IN PROGRESS**