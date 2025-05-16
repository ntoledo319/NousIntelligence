# Centralized Feature Chat Integration

This document outlines the `cfhat` (Centralized Feature Chat) function that serves as the central hub for all chat-related features in the application.

## Overview

The `cfhat` function is designed to be the single point of entry for all natural language interactions, allowing the application to maintain consistent context, tracking, knowledge management, and model selection across features.

## Function Signature

```python
def cfhat(message_text, user_id=None, feature=None, context=None, include_debug=False):
    """
    Central function for all chat-related features. All features should connect through this
    function to ensure consistent handling, knowledge storage, and model selection.
    
    Args:
        message_text (str): The user's message
        user_id (str, optional): User ID for personalized knowledge
        feature (str, optional): The specific feature being used (e.g., 'email_analysis', 'weather', 'travel')
        context (dict, optional): Additional context relevant to the feature
        include_debug (bool): Whether to include debug info in response
        
    Returns:
        str or dict: Response to the user's message
    """
```

## Supported Features

The `cfhat` function provides specialized handling for the following features:

- **General Chat**: Direct user conversation without a specific feature context
- **Email Analysis**: Analyze email content for summaries, action items, and key information
- **Weather**: Provide weather forecasts, insights, and pain forecasts
- **Travel**: Assist with travel planning, recommendations, and trip itineraries
- **DBT (Dialectical Behavior Therapy)**: Provide therapy support and mindfulness guidance
- **Spotify**: Deliver music recommendations and handle Spotify-related questions
- **Budget**: Assist with financial management and budget insights
- **Shopping**: Help with shopping list management and product recommendations

## How It Works

1. When a feature needs AI-powered chat functionality, it calls the `cfhat` function with:
   - The user's message
   - The user's ID (for personalized knowledge)
   - The feature identifier (to provide specialized context)
   - Any additional context needed for the feature

2. The `cfhat` function:
   - Prepares appropriate system prompts based on the feature
   - Incorporates the user's relevant knowledge base
   - Sends the request to the appropriate AI model
   - Processes and returns the response

3. The calling feature can then:
   - Display the AI's response directly to the user
   - Parse structured data from the response
   - Take actions based on the AI's analysis

## Example Usage

### General Chat

```python
from utils.ai_helper import cfhat

response = cfhat("How can I improve my sleep?", user_id="user123")
```

### Email Analysis

```python
from utils.ai_helper import cfhat

email_content = "Hi team, we need to schedule the Q3 review for next Friday..."
analysis = cfhat(
    email_content,
    user_id="user123",
    feature="email_analysis",
    context={"email_content": email_content, "format": "json"}
)
```

### Weather Forecast with Pain Risk

```python
from utils.ai_helper import cfhat

weather_data = get_weather_data("New York")
forecast = cfhat(
    "How will the weather affect my pain levels?",
    user_id="user123",
    feature="weather",
    context={"weather_data": weather_data}
)
```

## Benefits

- **Consistent Knowledge**: All features contribute to and benefit from the same knowledge base
- **Model Efficiency**: Uses appropriate models for different needs
- **Context Preservation**: Maintains user context across features
- **Centralized Logging**: Single point for tracking all AI interactions
- **Simplified Integration**: New features can easily integrate with AI capabilities

## Implementation Notes

- All features should use `cfhat` instead of direct model calls
- Feature-specific context should be provided for specialized assistance
- The function handles token usage accounting and fallbacks between models

## Service Usage Priority

The `cfhat` function implements a cascading fallback system:

1. OpenAI (if API key available)
2. OpenRouter (if API key available)
3. Hugging Face (if access token available)
4. Local fallbacks (when no external AI services are available)

This prioritization is managed through the `key_config.py` module. 