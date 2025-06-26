"""
AI Integration Module

This module integrates the AI Service Manager with existing code to optimize
API costs while maintaining high performance. It serves as the bridge between
the application's existing AI functionality and the cost-optimized services.

@module utils.ai_integration
@description Integration layer for AI cost optimization
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import time

# Import AI service manager
try:
    from utils.ai_service_manager import (
        get_ai_service_manager,
        TaskComplexity,
        ServiceTier,
        optimize_prompt,
        count_tokens
    )
    AI_MANAGER_AVAILABLE = True
except ImportError:
    AI_MANAGER_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)

# Import existing AI utilities to maintain compatibility
try:
    from utils.ai_helper import generate_ai_text as original_generate_ai_text
    from utils.ai_helper import analyze_document_content as original_analyze_document
    ORIGINAL_AI_AVAILABLE = True
except ImportError:
    ORIGINAL_AI_AVAILABLE = False
    logger.warning("Original AI helper functions not available")

class AIIntegration:
    """Integration class for AI cost optimization"""

    def __init__(self):
        """Initialize the AI integration"""
        self.manager = get_ai_service_manager() if AI_MANAGER_AVAILABLE else None
        logger.info(f"AI Integration initialized with manager: {self.manager is not None}")

    def get_complexity_for_task(self, task_type: str, task_params: Dict[str, Any]) -> TaskComplexity:
        """Determine appropriate complexity level for a task"""
        # Creative tasks generally require more complex models
        if task_type in ["creative_writing", "content_generation", "poem", "story"]:
            return TaskComplexity.COMPLEX

        # Simple tasks can use simpler models
        if task_type in ["classification", "summarization", "translation"]:
            return TaskComplexity.BASIC

        # Check content length as an indicator
        if "text" in task_params and isinstance(task_params["text"], str):
            if len(task_params["text"]) > 10000:
                return TaskComplexity.COMPLEX
            elif len(task_params["text"]) < 1000:
                return TaskComplexity.BASIC

        # Default to STANDARD for most tasks
        return TaskComplexity.STANDARD

    def generate_ai_text(self,
                      prompt: str,
                      task_type: str = "general",
                      max_tokens: int = 1000,
                      temperature: float = 0.7,
                      user_id: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """
        Generate text using the most cost-effective AI service for the task

        This is a drop-in replacement for generate_ai_text that uses cost optimization
        """
        # If AI manager not available, fall back to original function
        if not AI_MANAGER_AVAILABLE:
            if ORIGINAL_AI_AVAILABLE:
                return original_generate_ai_text(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
            else:
                return {"success": False, "error": "AI services not available"}

        # Classify the task complexity
        task_params = {"text": prompt, "max_tokens": max_tokens, **kwargs}
        complexity = self.get_complexity_for_task(task_type, task_params)

        # Get user preferences if available
        preferred_tier = None
        if user_id:
            try:
                from utils.settings import get_user_setting
                quality_pref = get_user_setting(user_id, "ai_quality_preference", "standard")
                if quality_pref == "economy":
                    preferred_tier = ServiceTier.ECONOMY
                elif quality_pref == "premium":
                    preferred_tier = ServiceTier.PREMIUM
                else:
                    preferred_tier = ServiceTier.STANDARD
            except Exception as e:
                logger.warning(f"Could not get user preferences: {e}")

        # Select the service
        service, model = self.manager.select_service_for_task(
            task_type=task_type,
            complexity=complexity,
            preferred_tier=preferred_tier
        )

        # If no service available, return error
        if service == "none":
            return {"success": False, "error": "No AI services available"}

        # Optimize the prompt to reduce token usage
        optimized_prompt = optimize_prompt(prompt)
        input_tokens = count_tokens(optimized_prompt)

        start_time = time.time()
        success = False
        output_tokens = 0
        error_type = None

        try:
            # Route to appropriate service
            if service == "openai":
                result = self._call_openai(optimized_prompt, model, max_tokens, temperature)
                output_tokens = count_tokens(result.get("response", ""))
                success = result.get("success", False)

            elif service == "openrouter":
                result = self._call_openrouter(optimized_prompt, model, max_tokens, temperature)
                output_tokens = count_tokens(result.get("response", ""))
                success = result.get("success", False)

            elif service == "huggingface":
                result = self._call_huggingface(optimized_prompt, max_tokens, temperature)
                output_tokens = count_tokens(result.get("response", ""))
                success = result.get("success", False)

            elif service == "local":
                # Local fallback using templates or rules
                result = self._local_fallback(optimized_prompt, task_type)
                output_tokens = count_tokens(result.get("response", ""))
                success = result.get("success", False)

            else:
                # Unknown service, try original function
                if ORIGINAL_AI_AVAILABLE:
                    result = original_generate_ai_text(optimized_prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
                    output_tokens = count_tokens(result.get("response", ""))
                    success = result.get("success", False)
                else:
                    result = {"success": False, "error": f"Unknown service: {service}"}

        except Exception as e:
            logger.error(f"Error generating AI text with {service}/{model}: {str(e)}")
            error_type = str(e)
            if "rate limit" in error_type.lower() or "429" in error_type:
                error_type = "rate_limit"
            result = {"success": False, "error": str(e)}

        # Track request for rate limiting and stats
        self.manager.track_request(service, success, error_type)

        # Track usage stats if user_id provided
        if user_id:
            self.manager.track_usage(
                user_id=user_id,
                service=service,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                success=success
            )

        # Add metrics to result
        result["service"] = service
        result["model"] = model
        result["processing_time"] = time.time() - start_time
        result["input_tokens"] = input_tokens
        result["output_tokens"] = output_tokens

        return result

    def _call_openai(self,
                    prompt: str,
                    model: str = "gpt-3.5-turbo",
                    max_tokens: int = 1000,
                    temperature: float = 0.7) -> Dict[str, Any]:
        """Legacy OpenAI API call - now redirects to cost-optimized provider"""
        logger.warning("Legacy OpenAI call redirected to cost-optimized provider")

        # Redirect to cost-optimized AI
        from utils.cost_optimized_ai import get_cost_optimized_ai, TaskComplexity
        ai_client = get_cost_optimized_ai()

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]

        complexity = TaskComplexity.STANDARD
        if "gpt-4" in model:
            complexity = TaskComplexity.COMPLEX

        result = ai_client.chat_completion(messages, max_tokens=max_tokens, temperature=temperature, complexity=complexity)

        if result.get("success"):
            return {
                "success": True,
                "response": result.get("response", ""),
                "model": f"cost-optimized-{result.get('model', 'unknown')}"
            }
        else:
            return {"success": False, "error": result.get("error", "Unknown error")}

    def _call_openrouter(self,
                       prompt: str,
                       model: str = "google/gemini-pro",
                       max_tokens: int = 1000,
                       temperature: float = 0.7) -> Dict[str, Any]:
        """Call OpenRouter API with cost optimization"""
        try:
            # Check for OpenRouter key
            openrouter_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY")

            if not openrouter_key:
                return {"success": False, "error": "OpenRouter API key not available"}

            import openai
            client = openai.OpenAI(
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1"
            )

            # Create chat completion
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                headers={
                    "HTTP-Referer": "https://nous.chat",  # Identify app
                    "X-Title": "NOUS Assistant"  # Add context
                }
            )

            return {
                "success": True,
                "response": response.choices[0].message.content.strip(),
                "model": model
            }

        except Exception as e:
            logger.error(f"Error calling OpenRouter: {str(e)}")
            return {"success": False, "error": str(e)}

    def _call_huggingface(self,
                        prompt: str,
                        max_tokens: int = 1000,
                        temperature: float = 0.7) -> Dict[str, Any]:
        """Call Hugging Face API with cost optimization"""
        try:
            # Try to import Hugging Face helper
            try:
                from utils.huggingface_helper import generate_chat_response
                response = generate_chat_response(prompt, max_length=max_tokens)
                return {
                    "success": True,
                    "response": response,
                    "model": "huggingface-default"
                }
            except ImportError:
                # More basic implementation if helper not available
                hf_key = os.environ.get("HUGGINGFACE_API_KEY")

                if not hf_key:
                    return {"success": False, "error": "Hugging Face API key not available"}

                import requests
                API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
                headers = {"Authorization": f"Bearer {hf_key}"}

                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_length": max_tokens,
                        "temperature": temperature,
                        "return_full_text": False
                    }
                }

                response = requests.post(API_URL, headers=headers, json=payload)
                response.raise_for_status()

                return {
                    "success": True,
                    "response": response.json()[0]["generated_text"],
                    "model": "mistral-7b"
                }

        except Exception as e:
            logger.error(f"Error calling Hugging Face: {str(e)}")
            return {"success": False, "error": str(e)}

    def _local_fallback(self, prompt: str, task_type: str) -> Dict[str, Any]:
        """Local fallback for when no AI services are available"""
        # For simple tasks, we can sometimes provide basic responses
        if task_type == "greeting":
            return {
                "success": True,
                "response": "Hello! I'm your NOUS assistant. How can I help you today?",
                "model": "local-fallback"
            }
        elif task_type == "help":
            return {
                "success": True,
                "response": "I can help with various tasks such as answering questions, " +
                           "managing your calendar, providing weather updates, and more. " +
                           "What would you like to know?",
                "model": "local-fallback"
            }
        else:
            return {
                "success": False,
                "error": "Local processing cannot handle this request. Please try again when external AI services are available.",
                "model": "local-fallback"
            }

    def analyze_document(self,
                       document_text: str,
                       document_type: str = "general",
                       user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze document content using the most cost-effective AI service

        This is a drop-in replacement for analyze_document_content
        """
        # If AI manager not available, fall back to original function
        if not AI_MANAGER_AVAILABLE:
            if ORIGINAL_AI_AVAILABLE:
                return original_analyze_document(document_text)
            else:
                return {"success": False, "error": "AI services not available"}

        # Classify the task complexity based on document type and length
        complexity = TaskComplexity.STANDARD
        if len(document_text) > 5000:
            complexity = TaskComplexity.COMPLEX
        elif document_type in ["legal", "medical", "technical"]:
            complexity = TaskComplexity.COMPLEX

        # For very short documents, we can use simpler models
        if len(document_text) < 1000 and document_type == "general":
            complexity = TaskComplexity.BASIC

        # Select the service
        service, model = self.manager.select_service_for_task(
            task_type="document_analysis",
            complexity=complexity
        )

        # Build an appropriate prompt based on document type
        system_prompt = """
        Analyze the provided document and extract the following information:

        1. Key topics and main points
        2. Important entities mentioned (people, organizations, etc.)
        3. Action items or tasks (if any)
        4. Summary (100 words max)

        Format your response as JSON with these keys:
        - topics: list of key topics
        - entities: list of important entities
        - action_items: list of action items (or empty list if none)
        - summary: brief summary text
        """

        # Truncate document if it's too long
        max_length = 12000  # Reasonable context length for most models
        if len(document_text) > max_length:
            document_text = document_text[:max_length] + "...[content truncated]"

        # Format prompt for the AI
        prompt = f"Document content:\n\n{document_text}"

        # Handle based on service
        if service == "openai":
            try:
                # Import the OpenAI client
                from utils.ai_helper import initialize_openai
                openai_client = initialize_openai()

                if not openai_client:
                    return {"success": False, "error": "OpenAI client not available"}

                # Create chat completion with JSON response
                response = openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )

                result = response.choices[0].message.content
                analysis = json.loads(result)
                analysis["success"] = True

                return analysis

            except Exception as e:
                logger.error(f"Error in AI analysis with OpenAI: {str(e)}")
                return {"success": False, "error": f"Analysis failed: {str(e)}"}

        elif service == "openrouter":
            try:
                # Check for OpenRouter key
                openrouter_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY")

                if not openrouter_key:
                    return {"success": False, "error": "OpenRouter API key not available"}

                client = openai.OpenAI(
                    api_key=openrouter_key,
                    base_url="https://openrouter.ai/api/v1"
                )

                # Create chat completion
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    headers={
                        "HTTP-Referer": "https://nous.chat",
                        "X-Title": "NOUS Assistant"
                    }
                )

                result = response.choices[0].message.content
                try:
                    analysis = json.loads(result)
                    analysis["success"] = True
                except json.JSONDecodeError:
                    # Handle non-JSON response
                    analysis = {
                        "success": True,
                        "summary": result[:200],
                        "topics": [],
                        "entities": [],
                        "action_items": []
                    }

                return analysis

            except Exception as e:
                logger.error(f"Error in AI analysis with OpenRouter: {str(e)}")
                return {"success": False, "error": f"Analysis failed: {str(e)}"}

        else:
            # Basic fallback analysis for other services
            return {
                "success": True,
                "summary": document_text[:200] + "...",
                "topics": [],
                "entities": [],
                "action_items": []
            }

# Initialize the global AI integration
ai_integration = AIIntegration()

def get_ai_integration() -> AIIntegration:
    """Get the global AI integration instance"""
    global ai_integration
    return ai_integration

# Function exports for drop-in compatibility with existing code
def generate_ai_text(prompt: str, **kwargs) -> Dict[str, Any]:
    """Drop-in replacement for the original generate_ai_text function"""
    return ai_integration.generate_ai_text(prompt, **kwargs)

def analyze_document_content(document_text: str, **kwargs) -> Dict[str, Any]:
    """Drop-in replacement for the original analyze_document_content function"""
    return ai_integration.analyze_document(document_text, **kwargs)