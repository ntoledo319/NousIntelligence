"""
@module model_fallback
@description Cost-saving model fallback strategies with local model options
@author AI Assistant
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional, Callable, Union
from functools import lru_cache

# Configure logger
logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEOUT = 10  # Default timeout in seconds
MAX_RETRIES = 3       # Maximum number of retries
LOCAL_MODELS_ENABLED = os.environ.get("LOCAL_MODELS_ENABLED", "true").lower() == "true"

class ModelTier:
    """Model tier definitions for cost optimization"""
    LIGHTWEIGHT = "lightweight"  # Smallest, fastest, cheapest models
    STANDARD = "standard"        # Default models with good quality/cost
    PREMIUM = "premium"          # Best quality but most expensive

# Model configurations with fallbacks
MODEL_TIERS = {
    # Text completion models
    "completion": {
        ModelTier.LIGHTWEIGHT: [
            {"provider": "local", "model": "distilgpt2", "max_length": 100},
            {"provider": "huggingface", "model": "distilgpt2", "max_length": 100},
            {"provider": "openrouter", "model": "mistralai/mistral-7b", "max_tokens": 100}
        ],
        ModelTier.STANDARD: [
            {"provider": "huggingface", "model": "mistralai/mistral-7b-instruct", "max_length": 500},
            {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct", "max_tokens": 500},
            {"provider": "openai", "model": "gpt-3.5-turbo", "max_tokens": 500}
        ],
        ModelTier.PREMIUM: [
            {"provider": "openrouter", "model": "anthropic/claude-3-opus", "max_tokens": 1000},
            {"provider": "openai", "model": "gpt-4", "max_tokens": 1000}
        ]
    },
    
    # Embedding models
    "embedding": {
        ModelTier.LIGHTWEIGHT: [
            {"provider": "local", "model": "sentence-transformers/all-MiniLM-L6-v2"},
            {"provider": "huggingface", "model": "sentence-transformers/all-MiniLM-L6-v2"},
            {"provider": "openai", "model": "text-embedding-ada-002"}
        ],
        ModelTier.STANDARD: [
            {"provider": "huggingface", "model": "BAAI/bge-small-en-v1.5"},
            {"provider": "openai", "model": "text-embedding-3-small"}
        ],
        ModelTier.PREMIUM: [
            {"provider": "huggingface", "model": "BAAI/bge-large-en-v1.5"},
            {"provider": "openai", "model": "text-embedding-3-large"}
        ]
    },
    
    # Image generation models
    "image": {
        ModelTier.LIGHTWEIGHT: [
            {"provider": "local", "model": "stable-diffusion-sdxl-turbo"},
            {"provider": "huggingface", "model": "stabilityai/stable-diffusion-xl-base-1.0"}
        ],
        ModelTier.STANDARD: [
            {"provider": "huggingface", "model": "stabilityai/sdxl-turbo"},
            {"provider": "openai", "model": "dall-e-3"}
        ],
        ModelTier.PREMIUM: [
            {"provider": "openai", "model": "dall-e-3"}
        ]
    }
}

# Local model handlers
class LocalModelHandler:
    """Handler for local models to reduce costs"""
    
    # Flag to check if local models are available
    _local_models_initialized = False
    _text_model = None
    _embedding_model = None
    _image_model = None
    
    @classmethod
    def initialize_models(cls):
        """Initialize local models if enabled"""
        if not LOCAL_MODELS_ENABLED or cls._local_models_initialized:
            return
            
        try:
            # Initialize text model
            try:
                from transformers import pipeline
                cls._text_model = pipeline('text-generation', model='distilgpt2', device=-1)
                logger.info("Local text model initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize local text model: {str(e)}")
                
            # Initialize embedding model
            try:
                from sentence_transformers import SentenceTransformer
                cls._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Local embedding model initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize local embedding model: {str(e)}")
                
            # Initialize image model if diffusers is available
            try:
                from diffusers import StableDiffusionXLPipeline
                import torch
                cls._image_model = StableDiffusionXLPipeline.from_pretrained(
                    "stabilityai/stable-diffusion-xl-base-1.0",
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    variant="fp16" if torch.cuda.is_available() else None,
                    use_safetensors=True
                )
                if torch.cuda.is_available():
                    cls._image_model.to("cuda")
                logger.info("Local image model initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize local image model: {str(e)}")
                
            cls._local_models_initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing local models: {str(e)}")
    
    @classmethod
    def generate_text(cls, prompt: str, max_length: int = 100) -> str:
        """
        Generate text using local model
        
        Args:
            prompt: Input prompt text
            max_length: Maximum length of generated text
            
        Returns:
            Generated text
        """
        if not cls._local_models_initialized:
            cls.initialize_models()
            
        if cls._text_model is None:
            raise ValueError("Local text model not available")
            
        # Generate text
        result = cls._text_model(prompt, max_length=max_length, do_sample=True)
        generated_text = result[0]['generated_text']
        
        # If the response just repeats the prompt, add a generic response
        if generated_text.strip() == prompt.strip():
            generated_text += " I'm not sure how to respond to that."
            
        return generated_text
    
    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """
        Generate embeddings using local model
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
        """
        if not cls._local_models_initialized:
            cls.initialize_models()
            
        if cls._embedding_model is None:
            raise ValueError("Local embedding model not available")
            
        # Generate embedding
        embedding = cls._embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    @classmethod
    def generate_image(cls, prompt: str) -> bytes:
        """
        Generate image using local model
        
        Args:
            prompt: Text prompt for image generation
            
        Returns:
            Generated image as bytes
        """
        if not cls._local_models_initialized:
            cls.initialize_models()
            
        if cls._image_model is None:
            raise ValueError("Local image model not available")
            
        # Generate image
        import io
        from PIL import Image
        
        result = cls._image_model(prompt).images[0]
        
        # Convert to bytes
        buffer = io.BytesIO()
        result.save(buffer, format="PNG")
        return buffer.getvalue()

def get_fallback_chain(model_type: str, tier: str = ModelTier.STANDARD) -> List[Dict[str, Any]]:
    """
    Get the fallback chain for a specific model type and tier
    
    Args:
        model_type: Type of model (completion, embedding, image)
        tier: Model tier to use
        
    Returns:
        List of model configurations to try in order
    """
    if model_type not in MODEL_TIERS:
        raise ValueError(f"Unknown model type: {model_type}")
        
    if tier not in [ModelTier.LIGHTWEIGHT, ModelTier.STANDARD, ModelTier.PREMIUM]:
        logger.warning(f"Unknown tier: {tier}, falling back to STANDARD")
        tier = ModelTier.STANDARD
        
    return MODEL_TIERS[model_type][tier]

def with_fallbacks(func: Callable, model_type: str, tier: str = ModelTier.STANDARD, 
                  timeout: int = DEFAULT_TIMEOUT, max_retries: int = MAX_RETRIES) -> Callable:
    """
    Decorator to add model fallback capability to a function
    
    Args:
        func: Function to decorate
        model_type: Type of model (completion, embedding, image)
        tier: Model tier to use
        timeout: Timeout in seconds for each attempt
        max_retries: Maximum number of retries per model
        
    Returns:
        Decorated function with fallback capability
    """
    def wrapper(*args, **kwargs):
        # Get the fallback chain
        fallback_chain = get_fallback_chain(model_type, tier)
        
        # Try each model in the chain
        last_error = None
        for model_config in fallback_chain:
            provider = model_config["provider"]
            model_name = model_config["model"]
            
            # Add model config to kwargs
            model_kwargs = kwargs.copy()
            model_kwargs.update(model_config)
            
            # For local provider, use local model handler
            if provider == "local" and LOCAL_MODELS_ENABLED:
                try:
                    if model_type == "completion":
                        return LocalModelHandler.generate_text(
                            args[0] if args else model_kwargs.get("prompt", ""),
                            max_length=model_config.get("max_length", 100)
                        )
                    elif model_type == "embedding":
                        return LocalModelHandler.generate_embedding(
                            args[0] if args else model_kwargs.get("text", "")
                        )
                    elif model_type == "image":
                        return LocalModelHandler.generate_image(
                            args[0] if args else model_kwargs.get("prompt", "")
                        )
                except Exception as e:
                    logger.warning(f"Local model failed for {model_type}: {str(e)}")
                    last_error = e
                    continue
            
            # Try the external provider with retries
            for attempt in range(max_retries):
                try:
                    # Log the attempt
                    logger.info(f"Trying {provider}/{model_name} (attempt {attempt+1}/{max_retries})")
                    
                    # Call the original function with timeout
                    result = func(*args, **model_kwargs)
                    
                    # Log success and return result
                    logger.info(f"Successfully used {provider}/{model_name}")
                    return result
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"Error with {provider}/{model_name}: {str(e)}")
                    
                    # Wait before retrying (exponential backoff)
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** attempt
                        logger.info(f"Retrying in {sleep_time} seconds...")
                        time.sleep(sleep_time)
        
        # If we reach here, all models failed
        error_msg = f"All models failed for {model_type}"
        if last_error:
            error_msg += f": {str(last_error)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    return wrapper

@lru_cache(maxsize=100)
def get_optimal_model_for_task(task_type: str, complexity: str = "medium", 
                              token_count: Optional[int] = None) -> Dict[str, Any]:
    """
    Get the most cost-effective model configuration for a specific task
    
    Args:
        task_type: Type of task (text, chat, summary, etc.)
        complexity: Complexity of the task (low, medium, high)
        token_count: Approximate token count if known
        
    Returns:
        Model configuration to use
    """
    # Map complexity to model tier
    tier_map = {
        "low": ModelTier.LIGHTWEIGHT,
        "medium": ModelTier.STANDARD,
        "high": ModelTier.PREMIUM
    }
    
    tier = tier_map.get(complexity, ModelTier.STANDARD)
    
    # Adjust tier based on token count for completions
    if task_type in ["completion", "chat", "summary"] and token_count:
        if token_count > 1000 and tier == ModelTier.PREMIUM:
            # For very large inputs, consider downsizing to save costs
            tier = ModelTier.STANDARD
        elif token_count < 100 and tier == ModelTier.STANDARD:
            # For very small inputs, lightweight models may be sufficient
            tier = ModelTier.LIGHTWEIGHT
    
    # Get first (preferred) model from the fallback chain
    model_type = "completion"
    if task_type in ["embedding", "similarity", "search"]:
        model_type = "embedding"
    elif task_type in ["image", "generation"]:
        model_type = "image"
        
    fallback_chain = get_fallback_chain(model_type, tier)
    return fallback_chain[0] if fallback_chain else None 