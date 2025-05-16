"""
Hugging Face API integration helper
Provides free AI capabilities as an alternative to OpenAI/OpenRouter
"""

import os
import json
import base64
import logging
import requests
from io import BytesIO
from PIL import Image

# Access Hugging Face token from environment variables
HF_TOKEN = os.environ.get("HF_ACCESS_TOKEN")

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
        response = requests.post(
            api_url,
            headers=headers,
            json={"inputs": text, "options": {"wait_for_model": True}}
        )
        
        if response.status_code == 200:
            embeddings = response.json()
            # Return the first embedding vector if it's a list of embeddings
            if isinstance(embeddings, list) and len(embeddings) > 0:
                return embeddings[0]
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

def hf_chat_completion(messages, model="HuggingFaceH4/zephyr-7b-beta"):
    """Generate chat completion using Hugging Face's free chat models"""
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
        response = requests.post(
            api_url,
            headers=headers,
            json={"inputs": prompt, "parameters": {"max_new_tokens": 512}}
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