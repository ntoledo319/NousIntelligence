# NOUS AI Integration Setup Guide

## Overview

NOUS uses a unified AI service that supports multiple providers with automatic fallback. You can use **100% free tiers** to get started.

## Quick Start (Free Tier)

### Option 1: Google Gemini (Recommended - Free)

**Pros:** Free tier, fast, good quality, easy setup  
**Cons:** None for basic usage

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Create new API key or use existing
4. Add to your `.env` file:
   ```text
   GEMINI_API_KEY: your-api-key-here
   ```

**That's it!** NOUS will automatically use Gemini for chat.

### Option 2: OpenRouter (Free Models Available)

**Pros:** Access to multiple models, some free tiers  
**Cons:** Requires account creation

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for free account
3. Go to Keys → Create new key
4. Add to `.env`:
   ```text
   OPENROUTER_API_KEY: sk-or-v1-your-key-here
   ```

**Free models available:**
- `meta-llama/llama-3.3-70b-instruct:free`
- `google/gemini-2.0-flash-exp:free`

### Option 3: HuggingFace (Free)

**Pros:** Completely free, many models  
**Cons:** Slower, rate limits

1. Visit [HuggingFace](https://huggingface.co/settings/tokens)
2. Create new token (read access is enough)
3. Add to `.env`:
   ```text
   HUGGINGFACE_API_KEY: hf_your-token-here
   ```

## How NOUS Selects AI Provider

NOUS automatically selects the best available provider:

```
Task Type          → Provider Priority
─────────────────────────────────────
Basic/Simple       → Gemini → OpenRouter → Fallback
Standard Chat      → OpenRouter → Gemini → Fallback
Complex Tasks      → OpenRouter → Gemini → OpenAI
Research Questions → OpenAI → OpenRouter → Gemini
```

## Environment Variable Template

Use this as a reference for your `.env` file:

```text
# ============================================================================
# AI SERVICE CONFIGURATION
# ============================================================================

# FREE TIER OPTION 1: Google Gemini (Recommended)
GEMINI_API_KEY: your-gemini-api-key-here
GEMINI_MODEL: gemini-2.5-flash

# FREE TIER OPTION 2: OpenRouter
# OPENROUTER_API_KEY: sk-or-v1-your-key-here
# OPENROUTER_FREE_MODEL: meta-llama/llama-3.3-70b-instruct:free
# OPENROUTER_BASIC_MODEL: google/gemini-2.0-flash-exp:free

# FREE TIER OPTION 3: HuggingFace
# HUGGINGFACE_API_KEY: hf_your-token-here

# PAID OPTION: OpenAI (if you want premium quality)
# OPENAI_API_KEY: sk-your-openai-key-here
# OPENAI_STANDARD_MODEL: gpt-4o-mini
# OPENAI_RESEARCH_MODEL: gpt-4o
```

## Testing Your Setup

After adding API key(s), test the integration:

```bash
# Start the application
python main.py

# Visit http://localhost:5000
# Try the chat - if it gives real responses (not echoes), it's working!
```

Or test via command line:

```python
from utils.unified_ai_service import get_unified_ai_service

ai = get_unified_ai_service()
response = ai.chat_completion([
    {"role": "user", "content": "Hello! Can you help me with stress?"}
])
print(response)
```

## Cost Breakdown

| Provider | Free Tier | Paid Cost | Best For |
|----------|-----------|-----------|----------|
| **Gemini** | ✅ Generous | $0.075/1M tokens | General use |
| **OpenRouter** | ✅ Some models | $0.22-$3/1M | Variety |
| **HuggingFace** | ✅ Unlimited* | Free | Experimentation |
| **OpenAI** | ❌ No | $0.15-$10/1M | Premium quality |

*Rate limits apply

## Recommended Setup for Sponsors

**Minimal (Free):**
```text
GEMINI_API_KEY: your-key  # Just this one!
```

**Optimal (Free + Fallback):**
```text
GEMINI_API_KEY: your-gemini-key
OPENROUTER_API_KEY: your-openrouter-key
```

**Premium (Best Experience):**
```text
GEMINI_API_KEY: your-gemini-key      # Fast responses
OPENROUTER_API_KEY: your-or-key      # Variety
OPENAI_API_KEY: your-openai-key      # Complex tasks
```

## How AI Integration Works

### 1. User sends message

```javascript
// templates/chat.html
fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message: userMessage })
})
```

### 2. Route processes request

```python
# routes/api_routes.py
@api_bp.post("/chat")
def chat_api():
    msg = request.json.get("message")
    ai_response = _get_ai_response(msg, user_id)
    return jsonify(ai_response)
```

### 3. EmotionAwareTherapeuticAssistant analyzes

```python
# services/emotion_aware_therapeutic_assistant.py
def get_therapeutic_response(user_input, user_id):
    # 1. Detect emotion
    emotion = self.analyze_emotional_state(user_input)
    
    # 2. Select therapeutic approach
    approach = self._select_therapeutic_approach(emotion)
    
    # 3. Get AI response with therapeutic guidance
    response = self.ai_service.chat_completion(messages)
    
    # 4. Add skill recommendations
    return {
        'response': response,
        'emotion': emotion,
        'skills_recommended': skills
    }
```

### 4. AI provider generates response

```python
# utils/unified_ai_service.py
def chat_completion(messages):
    if 'gemini' in available_providers:
        return self._gemini_chat(messages)
    elif 'openrouter' in available_providers:
        return self._openrouter_chat(messages)
    else:
        return self._fallback_response()
```

## Troubleshooting

### "No AI providers available"
- Check that at least one API key is set in `.env`
- Restart the application after adding keys
- Verify key format is correct

### "API key invalid"
- Double-check the key was copied correctly
- Ensure no extra spaces in `.env`
- For Gemini: Key should start with `AI`
- For OpenRouter: Key should start with `sk-or-v1-`
- For OpenAI: Key should start with `sk-`

### "Rate limit exceeded"
- Free tiers have limits
- Add additional provider as fallback
- Consider upgrading to paid tier for high usage

### "Responses still echoing"
- Verify API key is actually being loaded
- Check logs for provider initialization
- Ensure `.env` file is in project root

## Advanced Configuration

### Custom Model Selection

Override default models:

```bash
# Use specific Gemini model
GEMINI_MODEL=gemini-1.5-pro

# Use specific OpenRouter models
OPENROUTER_STANDARD_MODEL=deepseek/deepseek-v3.2
OPENROUTER_RESEARCH_MODEL=anthropic/claude-sonnet-4.5
```

### Provider Priority

The system automatically selects providers, but you can force specific ones:

```python
from utils.unified_ai_service import get_unified_ai_service, TaskComplexity

ai = get_unified_ai_service()

# Force specific complexity level
response = ai.chat_completion(
    messages,
    complexity=TaskComplexity.RESEARCH  # Uses best model
)
```

## For Developers

### Adding a New Provider

1. Add API key environment variable
2. Add provider to `UnifiedAIService.__init__()`
3. Implement provider method (e.g., `_newprovider_chat()`)
4. Add to `_select_best_provider()` logic

### Testing Providers

```python
# Test all providers
from utils.unified_ai_service import get_unified_ai_service

ai = get_unified_ai_service()
print(f"Available providers: {ai.available_providers}")

# Test each
for provider in ai.available_providers:
    print(f"\nTesting {provider}...")
    # Provider will be auto-selected based on availability
```

## Support

- **Issues:** [GitHub Issues](https://github.com/ntoledo319/NousIntelligence/issues)
- **Questions:** [GitHub Discussions](https://github.com/ntoledo319/NousIntelligence/discussions)
- **Documentation:** [Full Docs](../docs/)

---

**Remember:** NOUS works with just ONE free API key. Start with Gemini, it's the easiest!
