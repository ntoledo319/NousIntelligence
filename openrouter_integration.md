# OpenRouter Integration for API Quota Management

This document explains how Nous AI uses OpenRouter as a fallback API provider when the primary OpenAI API quota is exceeded.

## Overview

To optimize resource usage and ensure system continuity, Nous implements a fallback mechanism using OpenRouter when the OpenAI API quota is exceeded. This ensures that critical AI functionality continues to work even when rate limits or quota issues arise with the primary API provider.

## Setup

1. An OpenRouter API key needs to be present in the `.env` file as `OPENROUTER_API_KEY`
2. The system will automatically detect quota exceeded errors from OpenAI and switch to OpenRouter

## Features Supported by OpenRouter Fallback

The following features are supported by the OpenRouter fallback:

- **Embeddings generation** - Used for semantic search in the knowledge base
- **AI completion requests** - Used for self-reflection and other AI responses
- **Knowledge pre-downloading** - Ensures knowledge base can still be populated

## Technical Implementation

The implementation follows these principles:

1. Always try OpenAI first for optimal quality and consistency
2. Detect quota or rate limit exceeded errors
3. Automatically fall back to OpenRouter with compatible models
4. If both fail, use local deterministic fallbacks as a last resort

## Monitoring and Metrics

The system logs all API provider changes with appropriate warning messages. You can monitor the use of fallback services in the application logs.

Example log patterns:
```
WARNING: OpenAI quota exceeded, trying OpenRouter as fallback
INFO: Successfully generated embedding via OpenRouter
```

## Fallback Model Selection

For optimal compatibility and performance, we use these models with OpenRouter:

- Embeddings: `openai/text-embedding-ada-002` (compatible with OpenAI's embedding model)
- Chat completions: `openai/gpt-3.5-turbo` (widely available, good performance/cost balance)

## Error Handling

If both OpenAI and OpenRouter are unavailable:
- For embeddings: Fall back to deterministic hash-based embeddings
- For AI completions: Return a user-friendly error message

## Performance Considerations

- OpenRouter may have slightly different latency characteristics
- Pre-downloaded knowledge reduces the need for real-time API calls

## Future Improvements

- Implement proactive quota monitoring to switch before hitting limits
- Add configurable model selection for different quality/cost tradeoffs
- Expand caching to further reduce API dependency