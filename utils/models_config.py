"""
Models Configuration for Cost-Optimized AI Usage
This module defines which models to use for different AI tasks,
prioritizing cost-effective options without sacrificing quality.
"""

# ===== EMBEDDING MODELS =====

# Text embedding models in order of cost preference (lowest to highest)
EMBEDDING_MODELS = {
    "huggingface": {
        "default": "BAAI/bge-small-en-v1.5",           # Good balance of quality/cost
        "high_quality": "BAAI/bge-base-en-v1.5",       # Better quality when needed
        "lightweight": "sentence-transformers/all-MiniLM-L6-v2"  # Very efficient, lower quality
    },
    "openrouter": {
        "default": "openai/text-embedding-ada-002"     # Standard model via OpenRouter
    },
    "openai": {
        "default": "text-embedding-ada-002",           # Standard OpenAI embedding model
    }
}

# ===== CHAT COMPLETION MODELS =====

# Text generation models in order of cost preference (lowest to highest)
CHAT_MODELS = {
    "huggingface": {
        "default": "HuggingFaceH4/zephyr-7b-beta",     # Good balance model
        "high_quality": "mistralai/Mixtral-8x7B-Instruct-v0.1",  # Better quality
        "lightweight": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"      # Ultra-efficient
    },
    "openrouter": {
        "default": "openai/gpt-3.5-turbo",             # Good standard model
        "high_quality": "openai/gpt-4-turbo",          # Premium model for complex tasks
        "lightweight": "anthropic/claude-instant-v1"   # Efficient model
    },
    "openai": {
        "default": "gpt-3.5-turbo",                    # Standard model
        "high_quality": "gpt-4o",                      # Premium model
    }
}

# ===== VISION MODELS =====

# Image processing models in order of cost preference (lowest to highest)
VISION_MODELS = {
    "huggingface": {
        "caption": "Salesforce/blip-image-captioning-base",     # Image captioning
        "classification": "google/vit-base-patch16-224",        # Image classification
        "object_detection": "facebook/detr-resnet-50"           # Object detection
    },
    "openai": {
        "vision": "gpt-4-vision-preview"                        # OpenAI vision model
    }
}

# ===== AUDIO/VOICE MODELS =====

# Audio processing models in order of cost preference (lowest to highest)
AUDIO_MODELS = {
    "huggingface": {
        "audio_emotion": "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",
        "audio_classification": "superb/wav2vec2-base-superb-ks",
        "speech_recognition": "facebook/wav2vec2-base-960h"
    },
    "openai": {
        "speech_recognition": "whisper-1"
    }
}

# ===== TASK-SPECIFIC MODEL SELECTION =====

def get_model_for_task(task, quality_level="default", provider=None):
    """
    Select the appropriate model for a given task based on cost and quality requirements.
    
    Args:
        task (str): The AI task (e.g., "embedding", "chat", "caption", "audio_emotion")
        quality_level (str): Quality level needed ("default", "high_quality", "lightweight")
        provider (str, optional): Force a specific provider
        
    Returns:
        tuple: (provider, model_name) to use for the task
    """
    # Import here to avoid circular imports
    from utils.key_config import get_preferred_service, HF_ACCESS_TOKEN, OPENROUTER_API_KEY, OPENAI_API_KEY
    
    # Get available services
    preferred_service = provider or get_preferred_service()
    available_services = []
    
    if HF_ACCESS_TOKEN:
        available_services.append("huggingface")
    if OPENROUTER_API_KEY:
        available_services.append("openrouter")
    if OPENAI_API_KEY:
        available_services.append("openai")
    
    if not available_services:
        return ("local", "fallback")
    
    # If specified provider is not available, use the first available
    if preferred_service not in available_services:
        preferred_service = available_services[0]
    
    # Select model configuration based on task
    if task == "embedding":
        model_config = EMBEDDING_MODELS
    elif task == "chat":
        model_config = CHAT_MODELS
    elif task in ["caption", "classification", "object_detection"]:
        model_config = VISION_MODELS
        # Map task names to vision model types
        if task == "caption":
            quality_level = "caption"
        elif task == "classification":
            quality_level = "classification"
        elif task == "object_detection":
            quality_level = "object_detection"
    else:
        # Default to chat models for unknown tasks
        model_config = CHAT_MODELS
    
    # Get the model for the preferred service
    if preferred_service in model_config:
        # Try to get the requested quality level, fall back to default
        if quality_level in model_config[preferred_service]:
            return (preferred_service, model_config[preferred_service][quality_level])
        else:
            return (preferred_service, model_config[preferred_service]["default"])
    
    # If preferred service doesn't support this task, try alternatives
    for service in available_services:
        if service in model_config:
            if quality_level in model_config[service]:
                return (service, model_config[service][quality_level])
            else:
                return (service, model_config[service]["default"])
    
    # Final fallback
    return ("local", "fallback")