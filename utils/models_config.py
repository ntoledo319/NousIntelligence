"""
Models Configuration for Cost-Optimized AI Usage
This module defines which models to use for different AI tasks,
prioritizing cost-effective options without sacrificing quality.
Includes cost tracking, dynamic model selection, and smart fallbacks.
"""

import os
import logging
import time
from typing import Dict, Tuple, List, Optional, Any
from functools import lru_cache

# Configure logger
logger = logging.getLogger(__name__)

# ===== MODEL COST METRICS (relative units per 1K tokens) =====
MODEL_COSTS = {
    "huggingface": {
        # Embeddings
        "BAAI/bge-small-en-v1.5": {"input": 0.01, "output": 0.0},
        "BAAI/bge-base-en-v1.5": {"input": 0.02, "output": 0.0},
        "sentence-transformers/all-MiniLM-L6-v2": {"input": 0.005, "output": 0.0},
        
        # Chat models
        "HuggingFaceH4/zephyr-7b-beta": {"input": 0.05, "output": 0.05},
        "mistralai/Mixtral-8x7B-Instruct-v0.1": {"input": 0.2, "output": 0.2},
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0": {"input": 0.01, "output": 0.01},
        "meta-llama/Llama-2-7b-chat-hf": {"input": 0.1, "output": 0.1},
        
        # Vision models
        "Salesforce/blip-image-captioning-base": {"image": 0.1, "output": 0.0},
        "google/vit-base-patch16-224": {"image": 0.05, "output": 0.0},
        "facebook/detr-resnet-50": {"image": 0.15, "output": 0.0},
        
        # Audio models
        "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition": {"audio_second": 0.05},
        "superb/wav2vec2-base-superb-ks": {"audio_second": 0.03},
        "facebook/wav2vec2-base-960h": {"audio_second": 0.04}
    },
    "openrouter": {
        # Via OpenRouter (costs are approximate)
        "openai/text-embedding-ada-002": {"input": 0.05, "output": 0.0},
        "openai/gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "anthropic/claude-instant-v1": {"input": 1.0, "output": 3.0},
        "anthropic/claude-3-haiku": {"input": 1.0, "output": 3.0},
        "mistral/mistral-tiny": {"input": 0.2, "output": 0.6},
        "mistral/mistral-small": {"input": 0.8, "output": 2.4}
    },
    "openai": {
        "text-embedding-ada-002": {"input": 0.1, "output": 0.0},
        "gpt-3.5-turbo": {"input": 1.0, "output": 2.0},
        "gpt-4o": {"input": 5.0, "output": 15.0},
        "gpt-4-vision-preview": {"input": 10.0, "output": 30.0, "image": 10.0},
        "whisper-1": {"audio_second": 0.1}
    }
}

# ===== EMBEDDING MODELS =====

# Text embedding models in order of cost preference (lowest to highest)
EMBEDDING_MODELS = {
    "huggingface": {
        "default": "BAAI/bge-small-en-v1.5",           # Good balance of quality/cost
        "high_quality": "BAAI/bge-base-en-v1.5",       # Better quality when needed
        "lightweight": "sentence-transformers/all-MiniLM-L6-v2",  # Very efficient, lower quality
        "cached": "sentence-transformers/all-MiniLM-L6-v2"  # For large batch processing with caching
    },
    "openrouter": {
        "default": "openai/text-embedding-ada-002",     # Standard model via OpenRouter
        "cached": "openai/text-embedding-ada-002"       # For cached operations
    },
    "openai": {
        "default": "text-embedding-ada-002",           # Standard OpenAI embedding model
        "cached": "text-embedding-ada-002"             # For cached operations
    }
}

# ===== CHAT COMPLETION MODELS =====

# Text generation models in order of cost preference (lowest to highest)
CHAT_MODELS = {
    "huggingface": {
        "default": "HuggingFaceH4/zephyr-7b-beta",     # Good balance model
        "high_quality": "mistralai/Mixtral-8x7B-Instruct-v0.1",  # Better quality
        "lightweight": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",     # Ultra-efficient
        "fallback": "meta-llama/Llama-2-7b-chat-hf"    # Alternative if primary not available
    },
    "openrouter": {
        "default": "mistral/mistral-tiny",             # Updated default to more cost-effective
        "high_quality": "openai/gpt-4-turbo",          # Premium model for complex tasks
        "lightweight": "anthropic/claude-3-haiku",     # Efficient, high-quality model
        "fallback": "openai/gpt-3.5-turbo"             # Popular backup
    },
    "openai": {
        "default": "gpt-3.5-turbo",                    # Standard model
        "high_quality": "gpt-4o",                      # Premium model
        "fallback": "gpt-3.5-turbo"                    # Same as default
    }
}

# ===== VISION MODELS =====

# Image processing models in order of cost preference (lowest to highest)
VISION_MODELS = {
    "huggingface": {
        "caption": "Salesforce/blip-image-captioning-base",     # Image captioning
        "classification": "google/vit-base-patch16-224",        # Image classification
        "object_detection": "facebook/detr-resnet-50",          # Object detection
        "fallback": "Salesforce/blip-image-captioning-base"     # General fallback for image tasks
    },
    "openai": {
        "vision": "gpt-4-vision-preview",                       # OpenAI vision model
        "fallback": "gpt-4-vision-preview"                      # Same as default
    }
}

# ===== AUDIO/VOICE MODELS =====

# Audio processing models in order of cost preference (lowest to highest)
AUDIO_MODELS = {
    "huggingface": {
        "audio_emotion": "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",
        "audio_classification": "superb/wav2vec2-base-superb-ks",
        "speech_recognition": "facebook/wav2vec2-base-960h",
        "fallback": "facebook/wav2vec2-base-960h"               # General fallback for audio
    },
    "openai": {
        "speech_recognition": "whisper-1",
        "fallback": "whisper-1"                                 # Same as default
    }
}

# Track model usage and quotas
model_usage = {
    "daily": {},     # Daily usage counter
    "monthly": {},   # Monthly usage counter
    "last_reset": time.time()
}

# Environment-based quota controls (default to unlimited)
MAX_DAILY_MODEL_COST = float(os.environ.get("MAX_DAILY_MODEL_COST", "0"))  # 0 = unlimited
MAX_MONTHLY_MODEL_COST = float(os.environ.get("MAX_MONTHLY_MODEL_COST", "0"))  # 0 = unlimited
COST_ALERT_THRESHOLD = float(os.environ.get("COST_ALERT_THRESHOLD", "0.8"))  # Alert at 80% of quota

def reset_usage_counters():
    """Reset usage counters if a day has passed"""
    current_time = time.time()
    last_reset = model_usage["last_reset"]
    
    # Reset daily counter if more than 24 hours since last reset
    if current_time - last_reset > 86400:  # 24 hours in seconds
        model_usage["daily"] = {}
        model_usage["last_reset"] = current_time
        
        # Reset monthly counter on the 1st of each month
        current_month = time.strftime("%Y-%m")
        last_month = time.strftime("%Y-%m", time.localtime(last_reset))
        
        if current_month != last_month:
            model_usage["monthly"] = {}

def track_model_usage(provider: str, model: str, input_tokens: int = 0, output_tokens: int = 0, 
                     images: int = 0, audio_seconds: float = 0.0) -> float:
    """
    Track usage of a specific model and return the cost
    
    Args:
        provider: AI provider (huggingface, openrouter, openai)
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        images: Number of images processed
        audio_seconds: Seconds of audio processed
        
    Returns:
        Estimated cost of this usage
    """
    # Reset counters if needed
    reset_usage_counters()
    
    # Calculate cost
    cost = 0.0
    
    if provider in MODEL_COSTS and model in MODEL_COSTS[provider]:
        cost_metrics = MODEL_COSTS[provider][model]
        
        # Calculate based on tokens
        if input_tokens > 0 and "input" in cost_metrics:
            cost += (input_tokens / 1000) * cost_metrics["input"]
        
        if output_tokens > 0 and "output" in cost_metrics:
            cost += (output_tokens / 1000) * cost_metrics["output"]
            
        # Calculate based on images
        if images > 0 and "image" in cost_metrics:
            cost += images * cost_metrics["image"]
            
        # Calculate based on audio seconds
        if audio_seconds > 0 and "audio_second" in cost_metrics:
            cost += audio_seconds * cost_metrics["audio_second"]
    
    # Update usage counters
    model_key = f"{provider}/{model}"
    
    # Update daily usage
    if model_key not in model_usage["daily"]:
        model_usage["daily"][model_key] = {"cost": 0.0, "calls": 0}
    
    model_usage["daily"][model_key]["cost"] += cost
    model_usage["daily"][model_key]["calls"] += 1
    
    # Update monthly usage
    if model_key not in model_usage["monthly"]:
        model_usage["monthly"][model_key] = {"cost": 0.0, "calls": 0}
    
    model_usage["monthly"][model_key]["cost"] += cost
    model_usage["monthly"][model_key]["calls"] += 1
    
    # Check quotas and log warnings
    total_daily_cost = sum(data["cost"] for data in model_usage["daily"].values())
    total_monthly_cost = sum(data["cost"] for data in model_usage["monthly"].values())
    
    if MAX_DAILY_MODEL_COST > 0 and total_daily_cost > MAX_DAILY_MODEL_COST * COST_ALERT_THRESHOLD:
        logger.warning(f"Daily model cost ({total_daily_cost:.2f}) approaching limit ({MAX_DAILY_MODEL_COST:.2f})")
        
    if MAX_MONTHLY_MODEL_COST > 0 and total_monthly_cost > MAX_MONTHLY_MODEL_COST * COST_ALERT_THRESHOLD:
        logger.warning(f"Monthly model cost ({total_monthly_cost:.2f}) approaching limit ({MAX_MONTHLY_MODEL_COST:.2f})")
    
    return cost

def is_quota_available(estimated_cost: float = 0.0) -> bool:
    """
    Check if there's quota available for the estimated cost
    
    Args:
        estimated_cost: Estimated cost of the operation
        
    Returns:
        True if quota available, False otherwise
    """
    # No quota limits set
    if MAX_DAILY_MODEL_COST <= 0 and MAX_MONTHLY_MODEL_COST <= 0:
        return True
        
    # Calculate current totals
    total_daily_cost = sum(data["cost"] for data in model_usage["daily"].values())
    total_monthly_cost = sum(data["cost"] for data in model_usage["monthly"].values())
    
    # Check against quotas
    if MAX_DAILY_MODEL_COST > 0 and total_daily_cost + estimated_cost > MAX_DAILY_MODEL_COST:
        logger.warning(f"Daily quota exceeded: {total_daily_cost:.2f} + {estimated_cost:.2f} > {MAX_DAILY_MODEL_COST:.2f}")
        return False
        
    if MAX_MONTHLY_MODEL_COST > 0 and total_monthly_cost + estimated_cost > MAX_MONTHLY_MODEL_COST:
        logger.warning(f"Monthly quota exceeded: {total_monthly_cost:.2f} + {estimated_cost:.2f} > {MAX_MONTHLY_MODEL_COST:.2f}")
        return False
        
    return True

@lru_cache(maxsize=64)
def get_model_for_task(task: str, quality_level: str = "default", provider: Optional[str] = None) -> Tuple[str, str]:
    """
    Select the appropriate model for a given task based on cost and quality requirements.
    
    Args:
        task: The AI task (e.g., "embedding", "chat", "caption", "audio_emotion")
        quality_level: Quality level needed ("default", "high_quality", "lightweight")
        provider: Force a specific provider
        
    Returns:
        (provider, model_name) to use for the task
    """
    # Import here to avoid circular imports
    from utils.key_config import validate_keys
    
    # Validate API keys first
    keys_valid = validate_keys()
    
    # Determine available services based on valid keys
    available_services = [service for service, valid in keys_valid.items() if valid]
    
    # Add explicit provider validation with environment flags
    from utils.key_config import USE_HUGGINGFACE, USE_OPENROUTER, USE_OPENAI
    
    if "huggingface" in available_services and not USE_HUGGINGFACE:
        available_services.remove("huggingface")
        
    if "openrouter" in available_services and not USE_OPENROUTER:
        available_services.remove("openrouter")
        
    if "openai" in available_services and not USE_OPENAI:
        available_services.remove("openai")
    
    if not available_services:
        logger.warning(f"No API services available for task '{task}', using local fallback")
        return ("local", "fallback")
    
    # For non-specified provider, create a prioritized list based on cost-efficiency
    if not provider:
        # Default priority: huggingface (free/lowest cost) > openrouter > openai
        preferred_order = ["huggingface", "openrouter", "openai"]
        provider = next((p for p in preferred_order if p in available_services), available_services[0])
    elif provider not in available_services:
        # If specified provider not available, fall back to first available
        logger.warning(f"Requested provider {provider} not available, falling back to {available_services[0]}")
        provider = available_services[0]
    
    # Select model configuration based on task
    if task == "embedding" or task.startswith("embedding:"):
        model_config = EMBEDDING_MODELS
    elif task == "chat" or task.startswith("chat:"):
        model_config = CHAT_MODELS
    elif task in ["caption", "classification", "object_detection", "vision"]:
        model_config = VISION_MODELS
        # Map task names to vision model types if not explicitly specified
        if task == "vision" and quality_level == "default":
            quality_level = "vision"
        elif task == "caption" and quality_level == "default":
            quality_level = "caption"
        elif task == "classification" and quality_level == "default":
            quality_level = "classification"
        elif task == "object_detection" and quality_level == "default":
            quality_level = "object_detection"
    elif task.startswith("audio") or task.startswith("speech"):
        model_config = AUDIO_MODELS
        # Map audio task types
        if task == "audio_emotion" and quality_level == "default":
            quality_level = "audio_emotion"
        elif task == "audio_classification" and quality_level == "default":
            quality_level = "audio_classification"
        elif task == "speech_recognition" and quality_level == "default":
            quality_level = "speech_recognition"
    else:
        # Default to chat models for unknown tasks
        model_config = CHAT_MODELS
    
    # Try to get the model for the preferred provider
    if provider in model_config:
        # Try requested quality level
        if quality_level in model_config[provider]:
            return (provider, model_config[provider][quality_level])
        
        # Try "fallback" if quality level not found
        if "fallback" in model_config[provider]:
            logger.info(f"Quality level '{quality_level}' not found for {provider}, using fallback")
            return (provider, model_config[provider]["fallback"])
        
        # Default to "default" quality
        if "default" in model_config[provider]:
            logger.info(f"Quality level '{quality_level}' not found for {provider}, using default")
            return (provider, model_config[provider]["default"])
    
    # If we get here, try other providers
    for alt_provider in available_services:
        if alt_provider in model_config:
            if quality_level in model_config[alt_provider]:
                logger.info(f"Falling back to {alt_provider} for task '{task}'")
                return (alt_provider, model_config[alt_provider][quality_level])
            
            if "default" in model_config[alt_provider]:
                logger.info(f"Falling back to {alt_provider} default for task '{task}'")
                return (alt_provider, model_config[alt_provider]["default"])
    
    # Final fallback
    logger.warning(f"No suitable model found for task '{task}', using local fallback")
    return ("local", "fallback")

def estimate_cost(provider: str, model: str, input_tokens: int = 1000, output_tokens: int = 200) -> float:
    """
    Estimate the cost of using a specific model with given parameters
    
    Args:
        provider: AI provider (huggingface, openrouter, openai)
        model: Model name  
        input_tokens: Estimated input tokens
        output_tokens: Estimated output tokens
        
    Returns:
        Estimated cost
    """
    if provider not in MODEL_COSTS or model not in MODEL_COSTS[provider]:
        return 0.0
        
    cost_metrics = MODEL_COSTS[provider][model]
    cost = 0.0
    
    if "input" in cost_metrics:
        cost += (input_tokens / 1000) * cost_metrics["input"]
    
    if "output" in cost_metrics:
        cost += (output_tokens / 1000) * cost_metrics["output"]
        
    return cost

def get_usage_stats() -> Dict[str, Any]:
    """
    Get current usage statistics
    
    Returns:
        Dictionary with usage statistics
    """
    reset_usage_counters()  # Ensure counters are up to date
    
    daily_total = sum(data["cost"] for data in model_usage["daily"].values())
    monthly_total = sum(data["cost"] for data in model_usage["monthly"].values())
    
    # Sort models by cost (descending)
    daily_by_model = sorted(
        [{"model": model, **data} for model, data in model_usage["daily"].items()],
        key=lambda x: x["cost"],
        reverse=True
    )
    
    monthly_by_model = sorted(
        [{"model": model, **data} for model, data in model_usage["monthly"].items()],
        key=lambda x: x["cost"],
        reverse=True
    )
    
    return {
        "daily_total": daily_total,
        "monthly_total": monthly_total,
        "daily_quota": MAX_DAILY_MODEL_COST if MAX_DAILY_MODEL_COST > 0 else None,
        "monthly_quota": MAX_MONTHLY_MODEL_COST if MAX_MONTHLY_MODEL_COST > 0 else None,
        "daily_usage_percent": (daily_total / MAX_DAILY_MODEL_COST * 100) if MAX_DAILY_MODEL_COST > 0 else 0,
        "monthly_usage_percent": (monthly_total / MAX_MONTHLY_MODEL_COST * 100) if MAX_MONTHLY_MODEL_COST > 0 else 0,
        "daily_by_model": daily_by_model,
        "monthly_by_model": monthly_by_model
    }