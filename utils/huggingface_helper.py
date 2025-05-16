"""
Hugging Face Integration Helper - Provides free alternatives to OpenAI/OpenRouter services
This module handles interaction with Hugging Face Inference API for various NLP tasks
"""

import os
import json
import logging
import numpy as np
import requests
from typing import List, Dict, Any, Optional, Union, Tuple

# Hugging Face API endpoint and access token
HF_API_URL = "https://api-inference.huggingface.co/models"
HF_ACCESS_TOKEN = os.environ.get("HF_ACCESS_TOKEN", "")

# Default models for different tasks (optimized for free tier)
DEFAULT_MODELS = {
    "embedding": "sentence-transformers/all-MiniLM-L6-v2",  # Small but effective embedding model
    "text_generation": "distilgpt2",  # Lightweight text generation
    "summarization": "facebook/bart-large-cnn",  # Good quality/efficiency tradeoff for summaries
    "translation_en_fr": "Helsinki-NLP/opus-mt-en-fr",  # English to French translation
    "translation_fr_en": "Helsinki-NLP/opus-mt-fr-en",  # French to English translation
    "sentiment": "distilbert-base-uncased-finetuned-sst-2-english",  # Sentiment analysis
    "ner": "dbmdz/bert-large-cased-finetuned-conll03-english",  # Named Entity Recognition
    "question_answering": "distilbert-base-cased-distilled-squad",  # Question answering
    "zero_shot": "facebook/bart-large-mnli",  # Zero-shot classification
    "image_captioning": "nlpconnect/vit-gpt2-image-captioning",  # Image captioning
    "speech_recognition": "facebook/wav2vec2-base-960h",  # ASR model
}

def get_headers():
    """Get the headers for HF API requests with authentication if available"""
    headers = {"Content-Type": "application/json"}
    if HF_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {HF_ACCESS_TOKEN}"
    return headers

def get_embedding(text: str, model: str = "") -> Optional[np.ndarray]:
    """
    Generate embeddings using Hugging Face Inference API
    
    Args:
        text (str): The text to embed
        model (str): Model name to use (defaults to sentence-transformers/all-MiniLM-L6-v2)
        
    Returns:
        np.ndarray: The embedding vector or None if failed
    """
    if not model:
        model = DEFAULT_MODELS["embedding"]
    
    # Clean text
    text = text.replace("\n", " ")
    if len(text) > 8000:
        logging.warning(f"Truncating text from {len(text)} to 8000 chars for embedding")
        text = text[:8000]
    
    try:
        url = f"{HF_API_URL}/{model}"
        payload = {"inputs": text}
        
        response = requests.post(
            url, 
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            # The embedding model returns a list of embeddings (one per input)
            embedding = response.json()
            if isinstance(embedding, list) and len(embedding) > 0:
                if isinstance(embedding[0], list):  # Most models return a list of lists
                    logging.info(f"Successfully generated embedding of size {len(embedding[0])}")
                    return np.array(embedding[0], dtype=np.float32)
                else:  # Some models may return a single array directly
                    logging.info(f"Successfully generated embedding of size {len(embedding)}")
                    return np.array(embedding, dtype=np.float32)
            
        logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logging.error(f"Error generating embedding with Hugging Face: {str(e)}")
        return None

def generate_text(prompt: str, max_length: int = 50, model: str = "") -> Optional[str]:
    """
    Generate text completions using Hugging Face Inference API
    
    Args:
        prompt (str): The prompt to complete
        max_length (int): Maximum length of generated text
        model (str): Model name to use (defaults to distilgpt2)
        
    Returns:
        str: The generated text or None if failed
    """
    if not model:
        model = DEFAULT_MODELS["text_generation"]
    
    try:
        url = f"{HF_API_URL}/{model}"
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": max_length,
                "return_full_text": False  # Don't include the prompt in response
            }
        }
        
        response = requests.post(
            url, 
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            if isinstance(results, list) and len(results) > 0:
                if "generated_text" in results[0]:
                    return results[0]["generated_text"]
                
        logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logging.error(f"Error generating text with Hugging Face: {str(e)}")
        return None

def summarize_text(text: str, max_length: int = 130, min_length: int = 30, model: str = "") -> Optional[str]:
    """
    Summarize text using Hugging Face Inference API
    
    Args:
        text (str): The text to summarize
        max_length (int): Maximum length of summary
        min_length (int): Minimum length of summary
        model (str): Model name to use (defaults to facebook/bart-large-cnn)
        
    Returns:
        str: The summary or None if failed
    """
    if not model:
        model = DEFAULT_MODELS["summarization"]
    
    try:
        url = f"{HF_API_URL}/{model}"
        payload = {
            "inputs": text,
            "parameters": {
                "max_length": max_length,
                "min_length": min_length,
                "do_sample": False
            }
        }
        
        response = requests.post(
            url, 
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            if isinstance(results, list) and len(results) > 0:
                if "summary_text" in results[0]:
                    return results[0]["summary_text"]
                
        logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logging.error(f"Error summarizing text with Hugging Face: {str(e)}")
        return None

def translate_text(text: str, source_lang: str = "en", target_lang: str = "fr") -> Optional[str]:
    """
    Translate text using Hugging Face Inference API
    
    Args:
        text (str): The text to translate
        source_lang (str): Source language code (e.g., 'en')
        target_lang (str): Target language code (e.g., 'fr')
        
    Returns:
        str: The translated text or None if failed
    """
    model_key = f"translation_{source_lang}_{target_lang}"
    model = DEFAULT_MODELS.get(model_key)
    
    if not model:
        logging.error(f"No translation model found for {source_lang} to {target_lang}")
        return None
    
    try:
        url = f"{HF_API_URL}/{model}"
        payload = {"inputs": text}
        
        response = requests.post(
            url, 
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            if isinstance(results, list) and len(results) > 0:
                if "translation_text" in results[0]:
                    return results[0]["translation_text"]
                
        logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logging.error(f"Error translating text with Hugging Face: {str(e)}")
        return None

def analyze_sentiment(text: str, model: str = "") -> Optional[Dict[str, float]]:
    """
    Analyze sentiment of text using Hugging Face Inference API
    
    Args:
        text (str): The text to analyze
        model (str): Model name to use (defaults to distilbert-base-uncased-finetuned-sst-2-english)
        
    Returns:
        dict: Sentiment scores or None if failed
    """
    if not model:
        model = DEFAULT_MODELS["sentiment"]
    
    try:
        url = f"{HF_API_URL}/{model}"
        payload = {"inputs": text}
        
        response = requests.post(
            url, 
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            if isinstance(results, list) and len(results) > 0:
                return results[0]
                
        logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logging.error(f"Error analyzing sentiment with Hugging Face: {str(e)}")
        return None

def extract_entities(text: str, model: str = "") -> Optional[List[Dict[str, Any]]]:
    """
    Extract named entities from text using Hugging Face Inference API
    
    Args:
        text (str): The text to analyze
        model (str): Model name to use (defaults to dbmdz/bert-large-cased-finetuned-conll03-english)
        
    Returns:
        list: List of entities or None if failed
    """
    if not model:
        model = DEFAULT_MODELS["ner"]
    
    try:
        url = f"{HF_API_URL}/{model}"
        payload = {"inputs": text}
        
        response = requests.post(
            url, 
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
                
        logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logging.error(f"Error extracting entities with Hugging Face: {str(e)}")
        return None

def answer_question(question: str, context: str, model: str = "") -> Optional[Dict[str, Any]]:
    """
    Answer a question based on context using Hugging Face Inference API
    
    Args:
        question (str): The question to answer
        context (str): The context to extract answer from
        model (str): Model name to use (defaults to distilbert-base-cased-distilled-squad)
        
    Returns:
        dict: Answer with score or None if failed
    """
    if not model:
        model = DEFAULT_MODELS["question_answering"]
    
    try:
        url = f"{HF_API_URL}/{model}"
        payload = {
            "inputs": {
                "question": question,
                "context": context
            }
        }
        
        response = requests.post(
            url, 
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
                
        logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logging.error(f"Error answering question with Hugging Face: {str(e)}")
        return None

def classify_zero_shot(text: str, labels: List[str], model: str = "") -> Optional[Dict[str, List[float]]]:
    """
    Classify text into given labels without training using Hugging Face Inference API
    
    Args:
        text (str): The text to classify
        labels (list): List of class labels
        model (str): Model name to use (defaults to facebook/bart-large-mnli)
        
    Returns:
        dict: Classification scores or None if failed
    """
    if not model:
        model = DEFAULT_MODELS["zero_shot"]
    
    try:
        url = f"{HF_API_URL}/{model}"
        payload = {
            "inputs": text,
            "parameters": {"candidate_labels": labels}
        }
        
        response = requests.post(
            url, 
            headers=get_headers(),
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
                
        logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logging.error(f"Error classifying text with Hugging Face: {str(e)}")
        return None

def describe_image(image_path: str, model: str = "") -> Optional[str]:
    """
    Generate caption for an image using Hugging Face Inference API
    
    Args:
        image_path (str): Path to the image file
        model (str): Model name to use (defaults to nlpconnect/vit-gpt2-image-captioning)
        
    Returns:
        str: Image caption or None if failed
    """
    if not model:
        model = DEFAULT_MODELS["image_captioning"]
    
    try:
        url = f"{HF_API_URL}/{model}"
        
        with open(image_path, "rb") as f:
            data = f.read()
            
        response = requests.post(
            url, 
            headers={"Authorization": f"Bearer {HF_ACCESS_TOKEN}"},
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            if isinstance(results, list) and len(results) > 0:
                return results[0].get("generated_text")
                
        logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logging.error(f"Error describing image with Hugging Face: {str(e)}")
        return None

def generate_chat_response(messages: List[Dict[str, str]], max_length: int = 1000) -> Optional[str]:
    """
    Simulate a chat completion API using Hugging Face text generation models
    
    Args:
        messages (list): List of message dicts with 'role' and 'content'
        max_length (int): Maximum length of generated response
        
    Returns:
        str: Generated response or None if failed
    """
    # Convert messages format to a prompt format that text generation models understand
    prompt = ""
    for message in messages:
        role = message.get("role", "").lower()
        content = message.get("content", "")
        
        if role == "system":
            prompt += f"Instructions: {content}\n\n"
        elif role == "user":
            prompt += f"User: {content}\n\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n\n"
    
    prompt += "Assistant: "
    
    # Use a standard text generation model
    return generate_text(prompt, max_length=max_length, model=DEFAULT_MODELS["text_generation"])

def transcribe_audio(audio_path: str, model: str = "") -> Optional[str]:
    """
    Transcribe audio using Hugging Face Inference API
    
    Args:
        audio_path (str): Path to the audio file
        model (str): Model name to use (defaults to facebook/wav2vec2-base-960h)
        
    Returns:
        str: Transcribed text or None if failed
    """
    if not model:
        model = DEFAULT_MODELS["speech_recognition"]
    
    try:
        url = f"{HF_API_URL}/{model}"
        
        with open(audio_path, "rb") as f:
            data = f.read()
            
        response = requests.post(
            url, 
            headers={"Authorization": f"Bearer {HF_ACCESS_TOKEN}"},
            data=data,
            timeout=60  # Audio processing may take longer
        )
        
        if response.status_code == 200:
            result = response.json()
            if "text" in result:
                return result["text"]
                
        logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logging.error(f"Error transcribing audio with Hugging Face: {str(e)}")
        return None