"""
Cost-Optimized AI Provider Module

This module provides a unified interface for AI services, automatically routing
requests to the most cost-effective provider based on task requirements.

Providers:
- OpenRouter: Cost-effective chat completions with multiple model options
- Hugging Face: Free inference endpoints for audio and specialized tasks
- Local: Template-based fallbacks for basic tasks

@module utils.cost_optimized_ai
@description Unified cost-optimized AI provider interface
"""

import os
import logging
import json
import time
import requests
import base64
import io
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)

class TaskComplexity(Enum):
    BASIC = 1    # Simple responses, classification
    STANDARD = 2 # Regular chat, summarization
    COMPLEX = 3  # Creative content, complex reasoning

class CostOptimizedAI:
    """Unified AI provider with cost optimization"""
    
    def __init__(self):
        self.openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        self.huggingface_key = os.environ.get("HUGGINGFACE_API_KEY")
        
        # Track request costs and usage
        self.total_cost = 0.0
        self.request_count = 0
        
        logger.info(f"CostOptimized AI initialized - OpenRouter: {'✓' if self.openrouter_key else '✗'}, HuggingFace: {'✓' if self.huggingface_key else '✗'}")
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       max_tokens: int = 1000,
                       temperature: float = 0.7,
                       complexity: TaskComplexity = TaskComplexity.STANDARD) -> Dict[str, Any]:
        """
        Generate chat completion using the most cost-effective provider
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Response randomness (0.0-1.0)
            complexity: Task complexity level
            
        Returns:
            Dict with response and metadata
        """
        # Select model based on complexity and cost
        if complexity == TaskComplexity.COMPLEX:
            model = "anthropic/claude-3-sonnet-20240229"
            cost_per_1k_input = 0.003
            cost_per_1k_output = 0.015
        elif complexity == TaskComplexity.STANDARD:
            model = "google/gemini-pro"
            cost_per_1k_input = 0.00125
            cost_per_1k_output = 0.00375
        else:  # BASIC
            model = "google/gemini-pro"  # Still cost-effective for basic tasks
            cost_per_1k_input = 0.00125
            cost_per_1k_output = 0.00375
        
        # Try OpenRouter first
        if self.openrouter_key:
            try:
                return self._openrouter_chat(messages, model, max_tokens, temperature, cost_per_1k_input, cost_per_1k_output)
            except Exception as e:
                logger.warning(f"OpenRouter failed: {e}")
        
        # Fallback to local template-based response
        return self._local_chat_fallback(messages)
    
    def _openrouter_chat(self, messages, model, max_tokens, temperature, cost_per_1k_input, cost_per_1k_output):
        """Call OpenRouter API for chat completion"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "HTTP-Referer": "https://nous.chat",
            "X-Title": "NOUS Assistant",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract response
        response_text = data["choices"][0]["message"]["content"]
        
        # Calculate cost
        input_tokens = data.get("usage", {}).get("prompt_tokens", 0)
        output_tokens = data.get("usage", {}).get("completion_tokens", 0)
        
        cost = (input_tokens * cost_per_1k_input / 1000) + (output_tokens * cost_per_1k_output / 1000)
        self.total_cost += cost
        self.request_count += 1
        
        return {
            "success": True,
            "response": response_text,
            "provider": "openrouter",
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "total_cost": self.total_cost
        }
    
    def _local_chat_fallback(self, messages):
        """Local fallback for basic chat responses"""
        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "").lower()
                
        # Basic pattern matching for common queries
        if any(word in user_message for word in ["hello", "hi", "greeting"]):
            response = "Hello! I'm NOUS, your personal assistant. How can I help you today?"
        elif any(word in user_message for word in ["weather", "temperature", "forecast"]):
            response = "I can help with weather information. Please provide your location or ask about specific weather details."
        elif any(word in user_message for word in ["music", "play", "song"]):
            response = "I can help with music requests. Would you like me to find songs, artists, or playlists for you?"
        elif any(word in user_message for word in ["help", "what can you do"]):
            response = "I'm NOUS, your AI assistant. I can help with tasks like managing your schedule, weather updates, music recommendations, and answering questions."
        else:
            response = "I'm here to help! You can ask me about weather, music, scheduling, or general questions. What would you like to know?"
        
        return {
            "success": True,
            "response": response,
            "provider": "local",
            "model": "template-based",
            "input_tokens": len(" ".join([msg.get("content", "") for msg in messages])) // 4,
            "output_tokens": len(response) // 4,
            "cost": 0.0,
            "total_cost": self.total_cost
        }
    
    def text_to_speech(self, text: str, voice: str = "default", language: str = "en") -> Dict[str, Any]:
        """
        Convert text to speech using cost-effective providers
        
        Args:
            text: Text to convert to speech
            voice: Voice preference
            language: Language code
            
        Returns:
            Dict with audio data and metadata
        """
        if not self.huggingface_key:
            return {
                "success": False,
                "error": "Hugging Face API key required for TTS",
                "audio_base64": None
            }
        
        try:
            # Use Microsoft SpeechT5 TTS model on Hugging Face
            api_url = "https://api-inference.huggingface.co/models/microsoft/speecht5_tts"
            headers = {"Authorization": f"Bearer {self.huggingface_key}"}
            
            payload = {
                "inputs": text,
                "parameters": {
                    "speaker_embeddings": "default"
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            # Convert audio to base64
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            
            return {
                "success": True,
                "audio_base64": audio_base64,
                "provider": "huggingface",
                "model": "microsoft/speecht5_tts",
                "cost": 0.0,  # Free tier
                "metadata": {
                    "language": language,
                    "voice": voice,
                    "text_length": len(text)
                }
            }
            
        except Exception as e:
            logger.error(f"HuggingFace TTS failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_base64": None
            }
    
    def speech_to_text(self, audio_data: bytes, language: str = "en") -> Dict[str, Any]:
        """
        Convert speech to text using cost-effective providers
        
        Args:
            audio_data: Audio data as bytes
            language: Language code for transcription
            
        Returns:
            Dict with transcription results
        """
        if not self.huggingface_key:
            return {
                "success": False,
                "error": "Hugging Face API key required for STT",
                "text": None
            }
        
        try:
            # Use OpenAI Whisper model on Hugging Face
            api_url = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
            headers = {"Authorization": f"Bearer {self.huggingface_key}"}
            
            response = requests.post(api_url, headers=headers, data=audio_data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            transcription = result.get("text", "")
            
            return {
                "success": True,
                "text": transcription,
                "provider": "huggingface",
                "model": "openai/whisper-large-v3",
                "cost": 0.0,  # Free tier
                "metadata": {
                    "language": language,
                    "confidence": 0.9  # Whisper generally has high confidence
                }
            }
            
        except Exception as e:
            logger.error(f"HuggingFace STT failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": None
            }
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost and usage summary"""
        return {
            "total_requests": self.request_count,
            "total_cost": round(self.total_cost, 4),
            "average_cost_per_request": round(self.total_cost / max(self.request_count, 1), 4),
            "providers_available": {
                "openrouter": bool(self.openrouter_key),
                "huggingface": bool(self.huggingface_key)
            }
        }

# Global instance
_cost_optimized_ai = None

def get_cost_optimized_ai() -> CostOptimizedAI:
    """Get or create the global cost-optimized AI instance"""
    global _cost_optimized_ai
    if _cost_optimized_ai is None:
        _cost_optimized_ai = CostOptimizedAI()
    return _cost_optimized_ai

# Convenience functions for backward compatibility
def generate_ai_response(prompt: str, complexity: TaskComplexity = TaskComplexity.STANDARD) -> Dict[str, Any]:
    """Generate AI response using cost-optimized providers"""
    ai = get_cost_optimized_ai()
    messages = [{"role": "user", "content": prompt}]
    return ai.chat_completion(messages, complexity=complexity)

def generate_speech(text: str, voice: str = "default", language: str = "en") -> Dict[str, Any]:
    """Generate speech using cost-optimized providers"""
    ai = get_cost_optimized_ai()
    return ai.text_to_speech(text, voice, language)

def transcribe_audio(audio_data: bytes, language: str = "en") -> Dict[str, Any]:
    """Transcribe audio using cost-optimized providers"""
    ai = get_cost_optimized_ai()
    return ai.speech_to_text(audio_data, language)