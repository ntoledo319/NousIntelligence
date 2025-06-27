"""
HuggingFace Helper Module

Provides free-tier AI services through HuggingFace Inference API
for cost optimization while maintaining functionality.
"""
import os
import logging
import requests
from typing import Dict, Any, Optional, List
import tempfile

logger = logging.getLogger(__name__)

# HuggingFace Inference API endpoints
HF_API_BASE = "https://api-inference.huggingface.co/models"
HF_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN")

# Free models available on HuggingFace
FREE_MODELS = {
    "text_generation": "microsoft/DialoGPT-medium",
    "text_to_speech": "microsoft/speecht5_tts",
    "speech_to_text": "openai/whisper-base",
    "text_classification": "j-hartmann/emotion-english-distilroberta-base",
    "summarization": "facebook/bart-large-cnn",
    "translation": "Helsinki-NLP/opus-mt-en-fr",
    "image_caption": "nlpconnect/vit-gpt2-image-captioning",
    "image_classification": "google/vit-base-patch16-224",
    "object_detection": "facebook/detr-resnet-50",
    "image_to_text": "nlpconnect/vit-gpt2-image-captioning",
    "image_segmentation": "nvidia/segformer-b0-finetuned-ade-512-512"
}

def query_huggingface_api(model: str, inputs: Dict[str, Any], max_retries: int = 3, is_binary=False, data=None) -> Dict[str, Any]:
    """
    Query HuggingFace Inference API with fallback handling

    Args:
        model: Model name to use
        inputs: Input data for the model
        max_retries: Maximum number of retry attempts
        is_binary: Flag for binary data (images)
        data: The binary data payload

    Returns:
        API response or fallback response
    """
    if not HF_API_TOKEN:
        logger.warning("HuggingFace API token not found, using fallback")
        return {"success": False, "error": "API token not configured"}

    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    url = f"{HF_API_BASE}/{model}"

    for attempt in range(max_retries):
        try:
            if is_binary:
                response = requests.post(url, headers=headers, data=data, timeout=45)
            else:
                response = requests.post(url, headers=headers, json=inputs, timeout=30)

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            elif response.status_code == 503:
                logger.info(f"Model {model} loading, retrying... (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(5)
                    continue

            return {"success": False, "error": f"API error: {response.status_code}, {response.text}"}

        except Exception as e:
            logger.error(f"HuggingFace API error (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                continue

    return {"success": False, "error": "Max retries exceeded"}

def generate_text_hf(prompt: str, max_length: int = 100) -> Dict[str, Any]:
    """
    Generate text using HuggingFace free models

    Args:
        prompt: Input text prompt
        max_length: Maximum response length

    Returns:
        Generated text response
    """
    try:
        model = FREE_MODELS["text_generation"]
        inputs = {
            "inputs": prompt,
            "parameters": {
                "max_length": max_length,
                "temperature": 0.7,
                "do_sample": True
            }
        }

        result = query_huggingface_api(model, inputs)

        if result.get("success"):
            data = result.get("data", [])
            if data and len(data) > 0:
                return {
                    "success": True,
                    "response": data[0].get("generated_text", "").replace(prompt, "").strip(),
                    "model": model
                }

        # Fallback for text generation
        return {
            "success": True,
            "response": "I understand your request. While I'm processing that, is there anything else I can help you with?",
            "model": "fallback"
        }

    except Exception as e:
        logger.error(f"HuggingFace text generation error: {str(e)}")
        return {"success": False, "error": str(e)}

def text_to_speech_hf(text: str) -> Dict[str, Any]:
    """
    Convert text to speech using HuggingFace TTS

    Args:
        text: Text to convert to speech

    Returns:
        Audio data or status
    """
    try:
        model = FREE_MODELS["text_to_speech"]
        inputs = {"inputs": text}

        result = query_huggingface_api(model, inputs)

        if result.get("success"):
            return {
                "success": True,
                "audio_data": result.get("data"),
                "model": model
            }

        return {"success": False, "error": "TTS service unavailable"}

    except Exception as e:
        logger.error(f"HuggingFace TTS error: {str(e)}")
        return {"success": False, "error": str(e)}

def speech_to_text_hf(audio_data: bytes) -> Dict[str, Any]:
    """
    Convert speech to text using HuggingFace STT

    Args:
        audio_data: Audio data in bytes

    Returns:
        Transcribed text
    """
    try:
        model = FREE_MODELS["speech_to_text"]

        # For audio, we need to send as files
        files = {"file": audio_data}
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        url = f"{HF_API_BASE}/{model}"

        response = requests.post(url, headers=headers, files=files, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "text": data.get("text", ""),
                "model": model
            }

        return {"success": False, "error": "STT service unavailable"}

    except Exception as e:
        logger.error(f"HuggingFace STT error: {str(e)}")
        return {"success": False, "error": str(e)}

def summarize_text_hf(text: str, max_length: int = 150) -> Dict[str, Any]:
    """
    Summarize text using HuggingFace summarization model

    Args:
        text: Text to summarize
        max_length: Maximum summary length

    Returns:
        Summary text
    """
    try:
        model = FREE_MODELS["summarization"]
        inputs = {
            "inputs": text,
            "parameters": {
                "max_length": max_length,
                "min_length": 30,
                "do_sample": False
            }
        }

        result = query_huggingface_api(model, inputs)

        if result.get("success"):
            data = result.get("data", [])
            if data and len(data) > 0:
                return {
                    "success": True,
                    "summary": data[0].get("summary_text", ""),
                    "model": model
                }

        # Simple fallback summarization
        sentences = text.split('. ')
        summary = '. '.join(sentences[:3]) + '.' if len(sentences) > 3 else text
        return {
            "success": True,
            "summary": summary,
            "model": "fallback"
        }

    except Exception as e:
        logger.error(f"HuggingFace summarization error: {str(e)}")
        return {"success": False, "error": str(e)}

def classify_text_hf(text: str) -> Dict[str, Any]:
    """
    Classify the emotion of a text using a HuggingFace model.

    Args:
        text: The text to classify.

    Returns:
        A dictionary containing the classification results.
    """
    try:
        model = FREE_MODELS["text_classification"]
        inputs = {"inputs": text}
        result = query_huggingface_api(model, inputs)

        if result.get("success"):
            data = result.get("data", [])
            if data and len(data) > 0:
                return {
                    "success": True,
                    "classification": data[0],
                    "model": model
                }
        
        return {"success": False, "error": "Text classification service unavailable"}

    except Exception as e:
        logger.error(f"HuggingFace text classification error: {str(e)}")
        return {"success": False, "error": str(e)}

def hf_image_caption(image_path: str) -> str:
    with open(image_path, "rb") as f:
        data = f.read()
    result = query_huggingface_api(FREE_MODELS['image_caption'], {}, is_binary=True, data=data)
    if result.get("success"):
        return result['data'][0]['generated_text']
    return "Could not generate a caption for this image."

def hf_image_classification(image_path: str) -> Dict[str, Any]:
    with open(image_path, "rb") as f:
        data = f.read()
    result = query_huggingface_api(FREE_MODELS['image_classification'], {}, is_binary=True, data=data)
    if result.get("success"):
        return {
            "categories": result['data'],
            "top_category": result['data'][0]['label'] if result['data'] else "N/A",
            "confidence": result['data'][0]['score'] if result['data'] else 0
        }
    return {"error": "Classification failed"}

def hf_object_detection(image_path: str) -> Dict[str, Any]:
    with open(image_path, "rb") as f:
        data = f.read()
    result = query_huggingface_api(FREE_MODELS['object_detection'], {}, is_binary=True, data=data)
    if result.get("success"):
        return {"objects": result['data']}
    return {"error": "Object detection failed"}

def hf_image_to_text(image_path: str, prompt: str) -> str:
    # This model is the same as captioning, so we re-use it. The prompt is not used by this model.
    return hf_image_caption(image_path)

def hf_image_segmentation(image_path: str) -> Dict[str, Any]:
    with open(image_path, "rb") as f:
        data = f.read()
    result = query_huggingface_api(FREE_MODELS['image_segmentation'], {}, is_binary=True, data=data)
    if result.get("success"):
        return {"segments": result['data']}
    return {"error": "Segmentation failed"}

def process_image_for_analysis(image_data: bytes) -> Optional[str]:
    """Saves image data to a temporary file for analysis."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False, dir="temp") as temp_file:
            temp_file.write(image_data)
            return temp_file.name
    except Exception as e:
        logging.error(f"Error saving temp image: {e}")
        return None

def get_model_status() -> Dict[str, Any]:
    """
    Check status of available HuggingFace models

    Returns:
        Status of all configured models
    """
    status = {
        "huggingface_token_configured": bool(HF_API_TOKEN),
        "available_models": FREE_MODELS,
        "api_endpoint": HF_API_BASE
    }

    return status