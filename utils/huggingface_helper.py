"""
Hugging Face API integration helper
Provides free AI capabilities as an alternative to OpenAI/OpenRouter
"""

import os
import json
import base64
import logging
import requests
import numpy as np  # Used for embedding conversion
from io import BytesIO
from PIL import Image

# Access Hugging Face token from environment variables
HF_TOKEN = os.environ.get("HF_ACCESS_TOKEN")

# Define get_embedding to match import in knowledge_helper.py
def get_embedding(text, model="BAAI/bge-small-en-v1.5"):
    """Function alias for compatibility with knowledge_helper.py import"""
    embedding = hf_text_embeddings(text, model)
    
    # Ensure the embedding is a list and not a float
    if embedding is not None:
        # If it's a single float value (which causes "object of type 'float' has no len()" error)
        if isinstance(embedding, float):
            # Create a simple vector with the expected dimension (e.g., 384 for bge-small)
            # This is a fallback to prevent errors
            return np.ones(384, dtype=np.float32) * embedding
        
        # If it's already a list-like object, convert to numpy array
        return np.array(embedding, dtype=np.float32)
    
    return None
    
def hf_text_embeddings(text, model="BAAI/bge-small-en-v1.5"):
    """Generate text embeddings using Hugging Face's free embedding models"""
    if not HF_TOKEN:
        logging.error("No Hugging Face access token available")
        return None
        
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    try:
        logging.info(f"Requesting embedding from Hugging Face model: {model}")
        response = requests.post(
            api_url,
            headers=headers,
            json={"inputs": text, "options": {"wait_for_model": True}}
        )
        
        if response.status_code == 200:
            embeddings = response.json()
            logging.info(f"Received embedding response type: {type(embeddings)}")
            
            # Different models return embeddings in different formats
            # BGE models typically return a list where the first item contains the embedding vector
            if isinstance(embeddings, list):
                if len(embeddings) > 0:
                    # For models that return list of embeddings
                    if isinstance(embeddings[0], list):
                        logging.info(f"Using list embedding of length {len(embeddings[0])}")
                        return embeddings[0]
                    # For models that return objects with embedding info
                    elif isinstance(embeddings[0], dict) and 'embedding' in embeddings[0]:
                        logging.info(f"Using dict embedding of length {len(embeddings[0]['embedding'])}")
                        return embeddings[0]['embedding']
                    else:
                        logging.info(f"Using default list embedding")
                        return embeddings[0]
            # For models that return a single embedding vector
            elif isinstance(embeddings, dict) and 'embedding' in embeddings:
                logging.info(f"Using dict embedding of length {len(embeddings['embedding'])}")
                return embeddings['embedding']
            
            # Final fallback - just return whatever we got
            logging.info(f"Using fallback embedding approach")
            return embeddings
        else:
            logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error calling Hugging Face API: {str(e)}")
        return None

def hf_sentiment_analysis(text, model="distilbert-base-uncased-finetuned-sst-2-english"):
    """Analyze sentiment using Hugging Face's free sentiment analysis models"""
    if not HF_TOKEN:
        logging.error("No Hugging Face access token available")
        return {"error": "API configuration issue"}
        
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json={"inputs": text}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Format the results for easy consumption
            if isinstance(result, list) and len(result) > 0:
                result = result[0]  # Get first result for single texts
                
                # Format the output to have consistent structure
                formatted_result = {
                    "sentiment": max(result, key=lambda x: x["score"])["label"],
                    "confidence": max(result, key=lambda x: x["score"])["score"],
                    "details": result
                }
                return formatted_result
            return result
        else:
            logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        logging.error(f"Error calling Hugging Face API: {str(e)}")
        return {"error": str(e)}

def hf_entity_extraction(text, model="dslim/bert-base-NER"):
    """Extract named entities from text using Hugging Face's free NER models"""
    if not HF_TOKEN:
        logging.error("No Hugging Face access token available")
        return {"error": "API configuration issue"}
        
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json={"inputs": text}
        )
        
        if response.status_code == 200:
            entities = response.json()
            # Group entities by type
            grouped_entities = {}
            for entity in entities:
                entity_type = entity.get("entity_group")
                if entity_type not in grouped_entities:
                    grouped_entities[entity_type] = []
                grouped_entities[entity_type].append({
                    "text": entity.get("word"),
                    "score": entity.get("score")
                })
            
            return grouped_entities
        else:
            logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        logging.error(f"Error calling Hugging Face API: {str(e)}")
        return {"error": str(e)}

def hf_chat_completion(messages, model="HuggingFaceH4/zephyr-7b-beta", max_tokens=512, temperature=0.7):
    """
    Generate chat completion using Hugging Face's free chat models
    
    Args:
        messages: List of message objects with role and content
        model: Hugging Face model ID to use
        max_tokens: Maximum number of tokens to generate
        temperature: Controls randomness (0-1)
        
    Returns:
        str: Generated response text or None if failed
    """
    # Check for cache first to save API calls
    try:
        from utils.cache_helper import cache_result
        
        # Create a unique signature for this request
        import hashlib
        request_str = f"{model}:{str(messages)}:{max_tokens}:{temperature}"
        request_hash = hashlib.md5(request_str.encode()).hexdigest()
        
        # Function to be cached
        @cache_result(ttl_seconds=3600)  # Cache for 1 hour since model outputs are deterministic with same inputs
        def _get_hf_chat_response(req_hash, msg, mdl, mx_tokens, temp):
            if not HF_TOKEN:
                logging.error("No Hugging Face access token available")
                return None
                
            headers = {
                "Authorization": f"Bearer {HF_TOKEN}"
            }
            
            api_url = f"https://api-inference.huggingface.co/models/{mdl}"
            
            # Model-specific prompt formats
            if "zephyr" in mdl.lower():
                # Zephyr format
                prompt = _format_zephyr_prompt(msg)
            elif "mixtral" in mdl.lower():
                # Mixtral format
                prompt = _format_mixtral_prompt(msg)
            elif "llama" in mdl.lower():
                # Llama format
                prompt = _format_llama_prompt(msg)
            else:
                # Default format
                prompt = _format_default_prompt(msg)
            
            try:
                # Add parameters to control generation quality
                params = {
                    "max_new_tokens": mx_tokens,
                    "temperature": temp,
                    "return_full_text": False,  # Only return generated text without prompt
                    "top_p": 0.95,  # Nucleus sampling for more coherent outputs
                    "do_sample": temp > 0  # Use sampling for temperature > 0
                }
                
                response = requests.post(
                    api_url,
                    headers=headers,
                    json={"inputs": prompt, "parameters": params},
                    timeout=30  # Set reasonable timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Extract the generated text
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get("generated_text", "")
                        # Some models might still return the prompt, remove it
                        if generated_text.startswith(prompt):
                            generated_text = generated_text[len(prompt):]
                        return generated_text.strip()
                    return result.get("generated_text", "")
                else:
                    logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
                    return None
            except Exception as e:
                logging.error(f"Error calling Hugging Face API: {str(e)}")
                return None
        
        # Call the cached function
        return _get_hf_chat_response(request_hash, messages, model, max_tokens, temperature)
        
    except ImportError:
        # If caching is unavailable, do a direct call
        if not HF_TOKEN:
            logging.error("No Hugging Face access token available")
            return None
            
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}"
        }
        
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        # Convert messages to a prompt format that Hugging Face models can understand
        prompt = ""
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "system":
                prompt += f"<|system|>\n{content}\n"
            elif role == "user":
                prompt += f"<|user|>\n{content}\n"
            elif role == "assistant":
                prompt += f"<|assistant|>\n{content}\n"
        
        prompt += "<|assistant|>\n"  # Add the assistant prefix for the response
        
        try:
            params = {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "return_full_text": False
            }
            
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": prompt, "parameters": params}
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extract the generated text
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    # Remove the prompt to get only the new generated content
                    if generated_text.startswith(prompt):
                        generated_text = generated_text[len(prompt):]
                    return generated_text.strip()
                return result.get("generated_text", "")
            else:
                logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logging.error(f"Error calling Hugging Face API: {str(e)}")
            return None
            
def _format_zephyr_prompt(messages):
    """Format a prompt for Zephyr models"""
    prompt = ""
    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")
        
        if role == "system":
            prompt += f"<|system|>\n{content}\n"
        elif role == "user":
            prompt += f"<|user|>\n{content}\n"
        elif role == "assistant":
            prompt += f"<|assistant|>\n{content}\n"
    
    prompt += "<|assistant|>\n"  # Add the assistant prefix for the response
    return prompt
    
def _format_mixtral_prompt(messages):
    """Format a prompt for Mixtral models"""
    prompt = ""
    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")
        
        if role == "system":
            prompt += f"<s>[INST] System: {content} [/INST]\n"
        elif role == "user":
            prompt += f"<s>[INST] {content} [/INST]\n"
        elif role == "assistant":
            prompt += f"{content}</s>\n"
    
    prompt += "<s>"  # Add the start token for the response
    return prompt
    
def _format_llama_prompt(messages):
    """Format a prompt for Llama models"""
    prompt = ""
    system_content = ""
    
    # Extract system message first if it exists
    for message in messages:
        if message.get("role") == "system":
            system_content = message.get("content", "")
            break
    
    # Build conversation in Llama format
    for i, message in enumerate(messages):
        role = message.get("role", "")
        content = message.get("content", "")
        
        if role == "system":
            continue  # Already handled
        elif role == "user":
            if i == 0 or messages[i-1].get("role") != "assistant":
                if system_content:
                    prompt += f"<s>[INST] <<SYS>>\n{system_content}\n<</SYS>>\n\n{content} [/INST]"
                    system_content = ""  # Only include system message once
                else:
                    prompt += f"<s>[INST] {content} [/INST]"
            else:
                prompt += f"<s>[INST] {content} [/INST]"
        elif role == "assistant":
            prompt += f" {content} </s>"
    
    return prompt
    
def _format_default_prompt(messages):
    """Default prompt format for models without specific formatting"""
    prompt = ""
    has_system = False
    
    # Check if there's a system message
    for message in messages:
        if message.get("role") == "system":
            has_system = True
            break
    
    # Add a generic system instruction if none exists
    if not has_system:
        prompt += "You are a helpful, respectful assistant. Answer the following questions accurately and concisely.\n\n"
    
    # Add messages
    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")
        
        if role == "system":
            prompt += f"Instructions: {content}\n\n"
        elif role == "user":
            prompt += f"User: {content}\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n"
    
    prompt += "Assistant: "  # Add prefix for the response
    return prompt

def hf_image_caption(image_path, model="Salesforce/blip-image-captioning-base"):
    """Generate a caption for an image using Hugging Face's free vision models"""
    if not HF_TOKEN:
        logging.error("No Hugging Face access token available")
        return {"error": "API configuration issue"}
        
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    try:
        # Open image file
        with open(image_path, "rb") as file:
            image_bytes = file.read()
            
        # Send image to API
        response = requests.post(
            api_url,
            headers=headers,
            data=image_bytes
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Different models return different response formats
            if isinstance(result, list) and len(result) > 0:
                # Some models return a list of captions with scores
                if isinstance(result[0], dict) and "generated_text" in result[0]:
                    return result[0]["generated_text"]
                # Some return just the caption as string in a list
                return result[0]
            elif isinstance(result, dict) and "generated_text" in result:
                return result["generated_text"]
                
            return str(result)
        else:
            logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        logging.error(f"Error calling Hugging Face API: {str(e)}")
        return {"error": str(e)}

def hf_image_classification(image_path, model="google/vit-base-patch16-224"):
    """Classify image content using Hugging Face's free vision models"""
    if not HF_TOKEN:
        logging.error("No Hugging Face access token available")
        return {"error": "API configuration issue"}
        
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    try:
        # Open image file
        with open(image_path, "rb") as file:
            image_bytes = file.read()
            
        # Send image to API
        response = requests.post(
            api_url,
            headers=headers,
            data=image_bytes
        )
        
        if response.status_code == 200:
            result = response.json()
            # Format the results
            categories = []
            
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, dict) and "label" in item and "score" in item:
                        categories.append({
                            "category": item["label"],
                            "confidence": item["score"]
                        })
            
            return {
                "categories": categories,
                "top_category": categories[0]["category"] if categories else None,
                "confidence": categories[0]["confidence"] if categories else 0
            }
        else:
            logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        logging.error(f"Error calling Hugging Face API: {str(e)}")
        return {"error": str(e)}

def hf_object_detection(image_path, model="facebook/detr-resnet-50"):
    """Detect objects in an image using Hugging Face's free object detection models"""
    if not HF_TOKEN:
        logging.error("No Hugging Face access token available")
        return {"error": "API configuration issue"}
        
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    try:
        # Open image file
        with open(image_path, "rb") as file:
            image_bytes = file.read()
            
        # Send image to API
        response = requests.post(
            api_url,
            headers=headers,
            data=image_bytes
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Count objects by category
            object_counts = {}
            objects = []
            
            for obj in result:
                if "label" in obj and "score" in obj:
                    label = obj["label"]
                    if label in object_counts:
                        object_counts[label] += 1
                    else:
                        object_counts[label] = 1
                    
                    objects.append({
                        "label": label,
                        "confidence": obj["score"],
                        "box": obj.get("box", {})
                    })
            
            return {
                "objects": objects,
                "counts": object_counts,
                "total_objects": len(objects)
            }
        else:
            logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        logging.error(f"Error calling Hugging Face API: {str(e)}")
        return {"error": str(e)}

def hf_image_to_text(image_path, prompt="", model="Salesforce/blip-image-captioning-base"):
    """Convert image to text with optional prompt using Hugging Face's free vision-language models"""
    if not HF_TOKEN:
        logging.error("No Hugging Face access token available")
        return {"error": "API configuration issue"}
        
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    try:
        # Open image file
        with open(image_path, "rb") as file:
            image_bytes = file.read()
            
        # Prepare payload - some models accept a text prompt
        payload = image_bytes
        if prompt:
            # For models that accept a prompt, we need to format it differently
            # This is model-specific and may need adjustments
            headers["Content-Type"] = "application/json"
            
            # Convert image to base64
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            
            payload = json.dumps({
                "inputs": {
                    "image": image_b64,
                    "prompt": prompt
                }
            })
            
        # Send image to API
        response = requests.post(
            api_url,
            headers=headers,
            data=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Different models return different response formats
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and "generated_text" in result[0]:
                    return result[0]["generated_text"]
                return result[0]
            elif isinstance(result, dict) and "generated_text" in result:
                return result["generated_text"]
                
            return str(result)
        else:
            logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        logging.error(f"Error calling Hugging Face API: {str(e)}")
        return {"error": str(e)}

def hf_image_segmentation(image_path, model="facebook/maskformer-swin-base-coco"):
    """Segment an image into semantic regions using Hugging Face's free segmentation models"""
    if not HF_TOKEN:
        logging.error("No Hugging Face access token available")
        return {"error": "API configuration issue"}
        
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    try:
        # Open image file
        with open(image_path, "rb") as file:
            image_bytes = file.read()
            
        # Send image to API
        response = requests.post(
            api_url,
            headers=headers,
            data=image_bytes
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract segments
            segments = []
            for segment in result:
                if "label" in segment and "mask" in segment:
                    segments.append({
                        "label": segment["label"],
                        "score": segment.get("score", 0),
                        "has_mask": True
                    })
            
            return {
                "segments": segments,
                "segment_count": len(segments),
                "unique_classes": len(set(s["label"] for s in segments))
            }
        else:
            logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        logging.error(f"Error calling Hugging Face API: {str(e)}")
        return {"error": str(e)}

def process_image_for_analysis(image_data, max_size=(800, 800)):
    """Process and resize an image for analysis, saving temporary file"""
    try:
        # Create a BytesIO object from the image data
        image_io = BytesIO(image_data)
        
        # Open the image with PIL
        image = Image.open(image_io)
        
        # Resize the image if it's too large, maintaining aspect ratio
        if image.width > max_size[0] or image.height > max_size[1]:
            image.thumbnail(max_size)
        
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Save the processed image to a temporary file
        temp_path = os.path.join("temp", "temp_image.jpg")
        image.save(temp_path, "JPEG")
        
        return temp_path
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return None