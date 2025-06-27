"""
AI Service Manager

This module provides a centralized manager for AI services with cost optimization.
It intelligently routes requests to the most appropriate AI service based on:
1. Task complexity requirements
2. Cost considerations
3. Available API keys
4. Current rate limits

@module utils.ai_service_manager
@description Optimized AI service routing and management
"""

import os
import logging
import time
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
import random
from functools import lru_cache

# Import AI service utilities
# OpenAI integration removed for cost optimization
OPENAI_AVAILABLE = False

# Import individual service helpers
from utils.openai_helper import call_openai_api
from utils.openrouter_helper import call_openrouter_api
from utils.huggingface_helper import call_huggingface_api
from utils.gemini_helper import call_gemini_api, GEMINI_AVAILABLE

# Set up logging
logger = logging.getLogger(__name__)

# Task complexity levels
class TaskComplexity(Enum):
    BASIC = 1    # Simple classification, keyword extraction, etc.
    STANDARD = 2 # Typical chat responses, summarization
    COMPLEX = 3  # Creative content, complex reasoning, etc.

# Service tier configurations
class ServiceTier(Enum):
    ECONOMY = 1  # Lower cost, may have lower quality (Hugging Face, smaller models)
    STANDARD = 2 # Balanced cost/quality (OpenRouter with midrange models)
    PREMIUM = 3  # Highest quality, higher cost (OpenAI with GPT-4, etc.)

# Tracking for rate limits and backoff
class RateLimitTracker:
    def __init__(self):
        self.consecutive_errors = 0
        self.backoff_time = 5  # Starting backoff in seconds
        self.last_request_time = {}  # Track timestamps by service
        self.request_count = {}      # Count requests by service
        self.error_count = {}        # Count errors by service

# Global rate limit tracker
rate_limit_tracker = RateLimitTracker()

# Define provider priorities
PROVIDER_PRIORITY = ["openai", "gemini", "openrouter", "huggingface", "local"]

class AIServiceManager:
    """A service manager that selects the best AI provider based on availability and cost."""
    
    def __init__(self):
        self.cost_config = self._load_cost_config()

    def chat_completion(self, messages: List[Dict[str, str]], complexity: str = "standard", max_tokens: int = 1500, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Routes a chat completion request to the best available provider.
        """
        prompt = self._create_prompt_from_messages(messages)
        provider, model_name = self._select_best_provider(complexity)

        if provider == "gemini" and GEMINI_AVAILABLE:
            result = call_gemini_api(prompt, model_name)
            if result.get("success"):
                return result

        if provider == "openai" and OPENAI_AVAILABLE:
            result = call_openai_api(prompt, model_name, max_tokens, temperature)
            if result.get("success"):
                return result

        if provider == "openrouter" and OPENROUTER_AVAILABLE:
            return call_openrouter_api(prompt, model_name, max_tokens, temperature)
            
        if provider == "huggingface" and HUGGINGFACE_AVAILABLE:
            return call_huggingface_api(prompt, model_name)

        return self._local_fallback(prompt)

    def _select_best_provider(self, complexity: str) -> (str, str):
        if complexity == 'complex':
            if "openai" in PROVIDER_PRIORITY and OPENAI_AVAILABLE:
                return "openai", "gpt-4o"
            if "openrouter" in PROVIDER_PRIORITY and OPENROUTER_AVAILABLE:
                return "openrouter", "anthropic/claude-3-opus"
        
        if "gemini" in PROVIDER_PRIORITY and GEMINI_AVAILABLE:
            return "gemini", "gemini-pro"
        if "openrouter" in PROVIDER_PRIORITY and OPENROUTER_AVAILABLE:
            return "openrouter", "google/gemini-pro"

        if "openai" in PROVIDER_PRIORITY and OPENAI_AVAILABLE:
            return "openai", "gpt-3.5-turbo"
        if "huggingface" in PROVIDER_PRIORITY and HUGGINGFACE_AVAILABLE:
            return "huggingface", "default"

        return "local", "default"

    def _create_prompt_from_messages(self, messages: List[Dict[str, str]]) -> str:
        """Creates a single string prompt from a list of message dicts."""
        prompt = ""
        for message in messages:
            prompt += f"{message['role']}: {message['content']}\n"
        return prompt

    def _local_fallback(self, prompt: str) -> Dict[str, Any]:
        """Local fallback response when no APIs are available."""
        logger.info("Using local fallback response for prompt.")
        return {
            "success": True,
            "response": "I am a local fallback and cannot process this request.",
            "provider": "local"
        }

    def _load_cost_config(self) -> Dict[str, Any]:
        """Load cost configuration for different models"""
        # Default cost configuration (cost per 1K tokens)
        default_config = {
            "openai": {
                "gpt-4o": {"input": 0.01, "output": 0.03},
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
            },
            "openrouter": {
                "anthropic/claude-3-opus": {"input": 0.015, "output": 0.075},
                "anthropic/claude-3-sonnet": {"input": 0.003, "output": 0.015},
                "google/gemini-pro": {"input": 0.00125, "output": 0.00375}
            },
            "huggingface": {
                "default": {"input": 0.0, "output": 0.0}  # Assuming self-hosted or free tier
            },
            "local": {
                "default": {"input": 0.0, "output": 0.0}  # No API costs for local models
            }
        }

        # Try to load custom config if exists
        try:
            from utils.settings import get_setting
            custom_config_str = get_setting("ai_cost_config", "{}")
            custom_config = json.loads(custom_config_str)

            # Merge custom config with defaults
            for service, models in custom_config.items():
                if service in default_config:
                    for model, costs in models.items():
                        default_config[service][model] = costs
                else:
                    default_config[service] = models

        except Exception as e:
            logger.warning(f"Failed to load custom AI cost config: {e}")

        return default_config

    def track_request(self, service: str, success: bool, error_type: Optional[str] = None):
        """Track request success/failure for better service selection"""
        # Update request count
        if service not in rate_limit_tracker.request_count:
            rate_limit_tracker.request_count[service] = 0
        rate_limit_tracker.request_count[service] += 1

        # Track last request time
        rate_limit_tracker.last_request_time[service] = time.time()

        # Track errors if request failed
        if not success:
            if service not in rate_limit_tracker.error_count:
                rate_limit_tracker.error_count[service] = 0
            rate_limit_tracker.error_count[service] += 1

            # Apply exponential backoff for rate limit errors
            if error_type == "rate_limit":
                if rate_limit_tracker.consecutive_errors == 0:
                    rate_limit_tracker.backoff_time = 5
                else:
                    rate_limit_tracker.backoff_time = min(60, rate_limit_tracker.backoff_time * 2)
                rate_limit_tracker.consecutive_errors += 1
        else:
            # Reset consecutive errors on success
            rate_limit_tracker.consecutive_errors = 0

            # Gradually reduce error count for the service
            if service in rate_limit_tracker.error_count and rate_limit_tracker.error_count[service] > 0:
                rate_limit_tracker.error_count[service] = max(0, rate_limit_tracker.error_count[service] - 0.2)

    def estimate_cost(self, service: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a request based on token count"""
        try:
            if service in self.cost_config and model in self.cost_config[service]:
                costs = self.cost_config[service][model]
                input_cost = costs["input"] * (input_tokens / 1000)
                output_cost = costs["output"] * (output_tokens / 1000)
                return input_cost + output_cost
            elif service in self.cost_config:
                # Use default costs for the service
                costs = self.cost_config[service].get("default", {"input": 0.0, "output": 0.0})
                input_cost = costs["input"] * (input_tokens / 1000)
                output_cost = costs["output"] * (output_tokens / 1000)
                return input_cost + output_cost
            else:
                return 0.0
        except Exception as e:
            logger.warning(f"Error estimating cost: {e}")
            return 0.0

    def track_usage(self,
                   user_id: str,
                   service: str,
                   model: str,
                   input_tokens: int,
                   output_tokens: int,
                   success: bool):
        """Track AI service usage for a user"""
        try:
            from models import db, UserAIUsage
            cost = self.estimate_cost(service, model, input_tokens, output_tokens)

            # Record usage in database
            usage = UserAIUsage(
                user_id=user_id,
                service=service,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=cost,
                success=success
            )
            db.session.add(usage)
            db.session.commit()
        except Exception as e:
            logger.warning(f"Failed to track AI usage: {e}")

def get_ai_service_manager():
    return AIServiceManager()

def optimize_prompt(prompt: str, max_length: int = 4000) -> str:
    """Optimize a prompt to reduce token usage while preserving intent"""
    # Simple optimization - just truncate if too long
    if len(prompt) > max_length:
        return prompt[:max_length]
    return prompt

def count_tokens(text: str) -> int:
    """Estimate token count for a text string"""
    # Simple estimation: ~4 characters per token for English
    return len(text) // 4

def should_use_streaming(task_type: str, text_length: int) -> bool:
    """Determine if a request should use streaming based on task and length"""
    if task_type in ["chat", "completion"] and text_length > 1000:
        return True
    return False