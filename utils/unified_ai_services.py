"""
Unified AI Services
Consolidated AI integrations and utilities for multiple providers
"""
import os
import json
import asyncio
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

class UnifiedAIService:
    """Unified AI services with multiple provider support and cost optimization"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = 'openrouter'
        self.usage_stats = {}
        self.cost_tracking = {}
        self.setup_providers()
    
    def setup_providers(self):
        """Setup all available AI providers"""
        # OpenRouter setup (most cost-effective)
        openrouter_key = os.environ.get('OPENROUTER_API_KEY')
        if openrouter_key:
            self.providers['openrouter'] = {
                'api_key': openrouter_key,
                'base_url': 'https://openrouter.ai/api/v1',
                'cost_per_1k_tokens': 0.002,  # Average cost
                'available': True
            }
        
        # Google Gemini setup
        gemini_key = os.environ.get('GOOGLE_API_KEY')
        if gemini_key:
            self.providers['gemini'] = {
                'api_key': gemini_key,
                'cost_per_1k_tokens': 0.001,  # Often free tier
                'available': True
            }
        
        # HuggingFace setup (often free)
        hf_key = os.environ.get('HUGGINGFACE_API_KEY')
        if hf_key:
            self.providers['huggingface'] = {
                'api_key': hf_key,
                'cost_per_1k_tokens': 0.0,  # Free tier
                'available': True
            }
        
        # Fallback: Use environment variables for other providers
        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key:
            self.providers['openai'] = {
                'api_key': openai_key,
                'cost_per_1k_tokens': 0.02,  # More expensive
                'available': True
            }
    
    def get_available_providers(self):
        """Get list of available providers"""
        return [name for name, config in self.providers.items() if config.get('available', False)]
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Simple estimation: ~4 characters per token
        return max(1, len(text) // 4)
    
    def get_cost_estimate(self, prompt: str, provider: str = None) -> float:
        """Estimate cost for AI request"""
        provider = provider or self.default_provider
        token_count = self.estimate_tokens(prompt)
        
        if provider in self.providers:
            cost_per_1k = self.providers[provider]['cost_per_1k_tokens']
            return (token_count / 1000) * cost_per_1k
        
        return 0.0
    
    def get_optimal_provider(self, prompt: str, max_cost: float = 0.01, quality_preference: str = 'balanced'):
        """Get optimal provider based on cost, availability, and quality preference"""
        available_providers = []
        
        for provider, config in self.providers.items():
            if not config.get('available', False):
                continue
                
            cost = self.get_cost_estimate(prompt, provider)
            if cost <= max_cost:
                available_providers.append((provider, cost, config))
        
        if not available_providers:
            return self.default_provider if self.default_provider in self.providers else None
        
        # Sort by preference
        if quality_preference == 'cost':
            # Prioritize lowest cost
            return min(available_providers, key=lambda x: x[1])[0]
        elif quality_preference == 'quality':
            # Prioritize known quality providers
            quality_order = ['gemini', 'openrouter', 'openai', 'huggingface']
            for preferred in quality_order:
                for provider, cost, config in available_providers:
                    if provider == preferred:
                        return provider
        else:  # balanced
            # Balance cost and quality
            free_providers = [p for p, c, _ in available_providers if c == 0.0]
            if free_providers and 'gemini' in free_providers:
                return 'gemini'
            elif free_providers:
                return free_providers[0]
            else:
                return min(available_providers, key=lambda x: x[1])[0]
        
        return available_providers[0][0]
    
    async def generate_response(self, prompt: str, provider: str = None, model: str = None, 
                               max_tokens: int = 1000, temperature: float = 0.7):
        """Generate AI response with provider selection"""
        provider = provider or self.get_optimal_provider(prompt)
        
        if not provider or provider not in self.providers:
            return {"error": "No available AI providers configured"}
        
        start_time = time.time()
        
        try:
            if provider == 'openrouter':
                result = await self._openrouter_generate(prompt, model, max_tokens, temperature)
            elif provider == 'gemini':
                result = await self._gemini_generate(prompt, model, max_tokens, temperature)
            elif provider == 'huggingface':
                result = await self._huggingface_generate(prompt, model, max_tokens)
            elif provider == 'openai':
                result = await self._openai_generate(prompt, model, max_tokens, temperature)
            else:
                return {"error": f"Unknown provider: {provider}"}
            
            # Track usage
            end_time = time.time()
            self._track_usage(provider, prompt, result, end_time - start_time)
            
            return {
                "response": result,
                "provider": provider,
                "model": model,
                "cost_estimate": self.get_cost_estimate(prompt, provider),
                "processing_time": end_time - start_time
            }
            
        except Exception as e:
            return {"error": f"{provider} error: {str(e)}"}
    
    async def _openrouter_generate(self, prompt: str, model: str = None, max_tokens: int = 1000, temperature: float = 0.7):
        """Generate response using OpenRouter"""
        model = model or 'anthropic/claude-3.5-sonnet'
        
        try:
            import aiohttp
            
            headers = {
                'Authorization': f'Bearer {self.providers["openrouter"]["api_key"]}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://nous-assistant.replit.app',
                'X-Title': 'NOUS Personal Assistant'
            }
            
            payload = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': max_tokens,
                'temperature': temperature
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.providers["openrouter"]["base_url"]}/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        return f"Error: HTTP {response.status}"
                        
        except ImportError:
            return "aiohttp library required for OpenRouter. Install with: pip install aiohttp"
        except Exception as e:
            return f"OpenRouter error: {str(e)}"
    
    async def _gemini_generate(self, prompt: str, model: str = None, max_tokens: int = 1000, temperature: float = 0.7):
        """Generate response using Google Gemini"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.providers['gemini']['api_key'])
            
            model = model or 'gemini-pro'
            gemini_model = genai.GenerativeModel(model)
            
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
            
            response = await gemini_model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            return response.text
            
        except ImportError:
            return "Google Generative AI library required. Install with: pip install google-generativeai"
        except Exception as e:
            return f"Gemini error: {str(e)}"
    
    async def _huggingface_generate(self, prompt: str, model: str = None, max_tokens: int = 1000):
        """Generate response using HuggingFace"""
        model = model or 'microsoft/DialoGPT-large'
        
        try:
            import aiohttp
            
            headers = {
                'Authorization': f'Bearer {self.providers["huggingface"]["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'inputs': prompt,
                'parameters': {
                    'max_new_tokens': max_tokens,
                    'temperature': 0.7,
                    'do_sample': True
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'https://api-inference.huggingface.co/models/{model}',
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list) and len(data) > 0:
                            return data[0].get('generated_text', prompt)
                        return data.get('generated_text', 'No response generated')
                    else:
                        return f"Error: HTTP {response.status}"
                        
        except ImportError:
            return "aiohttp library required for HuggingFace"
        except Exception as e:
            return f"HuggingFace error: {str(e)}"
    
    async def _openai_generate(self, prompt: str, model: str = None, max_tokens: int = 1000, temperature: float = 0.7):
        """Generate response using OpenAI"""
        model = model or 'gpt-3.5-turbo'
        
        try:
            import aiohttp
            
            headers = {
                'Authorization': f'Bearer {self.providers["openai"]["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': max_tokens,
                'temperature': temperature
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        return f"Error: HTTP {response.status}"
                        
        except ImportError:
            return "aiohttp library required for OpenAI"
        except Exception as e:
            return f"OpenAI error: {str(e)}"
    
    def _track_usage(self, provider: str, prompt: str, response: str, processing_time: float):
        """Track usage statistics"""
        if provider not in self.usage_stats:
            self.usage_stats[provider] = {
                'requests': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'total_time': 0.0
            }
        
        token_count = self.estimate_tokens(prompt + str(response))
        cost = self.get_cost_estimate(prompt, provider)
        
        self.usage_stats[provider]['requests'] += 1
        self.usage_stats[provider]['total_tokens'] += token_count
        self.usage_stats[provider]['total_cost'] += cost
        self.usage_stats[provider]['total_time'] += processing_time
    
    def get_usage_stats(self):
        """Get usage statistics"""
        return self.usage_stats
    
    def reset_usage_stats(self):
        """Reset usage statistics"""
        self.usage_stats = {}
    
    # Specialized AI Functions
    def analyze_sentiment(self, text: str):
        """Analyze sentiment of text"""
        prompt = f"Analyze the sentiment of this text and respond with just: positive, negative, or neutral.\n\nText: {text}"
        
        # Use sync wrapper for backward compatibility
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.generate_response(prompt, max_tokens=10))
            sentiment = result.get('response', 'neutral').lower().strip()
            
            if 'positive' in sentiment:
                return 'positive'
            elif 'negative' in sentiment:
                return 'negative'
            else:
                return 'neutral'
        finally:
            loop.close()
    
    def summarize_text(self, text: str, max_length: int = 150):
        """Summarize text"""
        prompt = f"Summarize this text in approximately {max_length} characters:\n\n{text}"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.generate_response(prompt, max_tokens=max_length//3))
            return result.get('response', 'Unable to summarize')
        finally:
            loop.close()
    
    def extract_keywords(self, text: str, max_keywords: int = 10):
        """Extract keywords from text"""
        prompt = f"Extract the top {max_keywords} most important keywords from this text. Return only the keywords separated by commas:\n\n{text}"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.generate_response(prompt, max_tokens=100))
            keywords = result.get('response', '').split(',')
            return [kw.strip() for kw in keywords if kw.strip()]
        finally:
            loop.close()
    
    def generate_embeddings(self, text: str):
        """Generate text embeddings (simplified version)"""
        # This is a placeholder - real embeddings would require specific models
        words = text.lower().split()
        # Simple word frequency based embedding
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        return {
            'text': text,
            'word_count': len(words),
            'unique_words': len(word_freq),
            'top_words': sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def translate_text(self, text: str, target_language: str = 'en'):
        """Translate text to target language"""
        prompt = f"Translate this text to {target_language}. Return only the translation:\n\n{text}"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.generate_response(prompt))
            return result.get('response', text)
        finally:
            loop.close()
    
    def generate_creative_content(self, content_type: str, topic: str, length: str = 'medium'):
        """Generate creative content (stories, poems, etc.)"""
        length_map = {
            'short': 'a brief',
            'medium': 'a moderate length',
            'long': 'a detailed'
        }
        
        length_desc = length_map.get(length, 'a moderate length')
        prompt = f"Write {length_desc} {content_type} about {topic}."
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            max_tokens = {'short': 200, 'medium': 500, 'long': 1000}.get(length, 500)
            result = loop.run_until_complete(self.generate_response(prompt, max_tokens=max_tokens))
            return result.get('response', f'Unable to generate {content_type}')
        finally:
            loop.close()
    
    def answer_question(self, question: str, context: str = None):
        """Answer questions with optional context"""
        if context:
            prompt = f"Based on this context, answer the question:\n\nContext: {context}\n\nQuestion: {question}"
        else:
            prompt = f"Answer this question: {question}"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.generate_response(prompt))
            return result.get('response', 'Unable to answer question')
        finally:
            loop.close()

# Backward compatibility functions
def get_ai_response(prompt: str, provider: str = None):
    """Legacy function for backward compatibility"""
    service = UnifiedAIService()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(service.generate_response(prompt, provider))
        return result.get('response', 'No response generated')
    finally:
        loop.close()

def get_cost_optimized_response(prompt: str, max_cost: float = 0.01):
    """Get cost-optimized AI response"""
    service = UnifiedAIService()
    optimal_provider = service.get_optimal_provider(prompt, max_cost)
    return get_ai_response(prompt, optimal_provider)

def analyze_text_sentiment(text: str):
    """Legacy sentiment analysis function"""
    service = UnifiedAIService()
    return service.analyze_sentiment(text)

def summarize_content(text: str, max_length: int = 150):
    """Legacy summarization function"""
    service = UnifiedAIService()
    return service.summarize_text(text, max_length)

def generate_ai_content(content_type: str, topic: str):
    """Legacy content generation function"""
    service = UnifiedAIService()
    return service.generate_creative_content(content_type, topic)

# Cost optimization helpers
def get_cheapest_provider():
    """Get the cheapest available provider"""
    service = UnifiedAIService()
    return service.get_optimal_provider("test", quality_preference='cost')

def get_best_quality_provider():
    """Get the best quality provider within reasonable cost"""
    service = UnifiedAIService()
    return service.get_optimal_provider("test", max_cost=0.05, quality_preference='quality')

# Global service instance for convenience
ai_service = UnifiedAIService()