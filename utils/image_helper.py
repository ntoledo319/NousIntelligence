"""
Image processing helper utilizing Hugging Face for cost-effective AI tasks
Features:
- Image captioning (describe what's in an image)
- Image classification (identify objects/scenes)
- Image embedding for similarity search
- Travel photo organization and tagging
"""

import os
import logging
import base64
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from PIL import Image
import io
import numpy as np
import requests

# Get Hugging Face API token from environment
HF_ACCESS_TOKEN = os.environ.get("HF_ACCESS_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Hugging Face API base URL
HF_API_URL = "https://api-inference.huggingface.co/models"

# Recommended models for various image tasks (optimized for free tier)
MODELS = {
    "image_captioning": "nlpconnect/vit-gpt2-image-captioning",
    "image_classification": "google/vit-base-patch16-224",
    "object_detection": "facebook/detr-resnet-50",
    "image_segmentation": "facebook/detr-resnet-50-panoptic",
}

def get_headers():
    """Get authenticated headers for Hugging Face API requests"""
    headers = {"Authorization": f"Bearer {HF_ACCESS_TOKEN}"}
    return headers

def describe_image(image_path: str) -> Dict[str, Any]:
    """
    Generate a descriptive caption for an image using Hugging Face's free service
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Description with related metadata
    """
    try:
        model = MODELS["image_captioning"]
        url = f"{HF_API_URL}/{model}"
        
        # Check if file exists
        if not os.path.exists(image_path):
            return {"error": f"Image file not found: {image_path}", "success": False}
        
        # Load and send the image
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            
        headers = get_headers()
        response = requests.post(url, headers=headers, data=image_bytes, timeout=30)
            
        if response.status_code == 200:
            result = response.json()
            
            # Format the response based on the model output structure
            if isinstance(result, list) and len(result) > 0:
                # Most common response format
                if "generated_text" in result[0]:
                    description = result[0]["generated_text"]
                    return {
                        "description": description,
                        "success": True,
                        "provider": "huggingface"
                    }
            
            # Unknown format, return raw result
            return {
                "raw_result": result,
                "success": True,
                "provider": "huggingface"
            }
                
        # Handle errors
        return {
            "error": f"API error: {response.status_code} - {response.text}",
            "success": False
        }
    except Exception as e:
        logging.error(f"Error in describe_image: {str(e)}")
        return {"error": str(e), "success": False}

def classify_image(image_path: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Classify the content of an image, identifying objects and scenes
    
    Args:
        image_path (str): Path to the image file
        top_k (int): Number of top classifications to return
        
    Returns:
        dict: Classifications with confidence scores
    """
    try:
        model = MODELS["image_classification"]
        url = f"{HF_API_URL}/{model}"
        
        # Check if file exists
        if not os.path.exists(image_path):
            return {"error": f"Image file not found: {image_path}", "success": False}
        
        # Load and send the image
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            
        headers = get_headers()
        response = requests.post(url, headers=headers, data=image_bytes, timeout=30)
            
        if response.status_code == 200:
            results = response.json()
            
            # Format and limit to top_k results
            classifications = []
            for result in results[:top_k]:
                if "label" in result and "score" in result:
                    classifications.append({
                        "label": result["label"],
                        "confidence": result["score"]
                    })
            
            return {
                "classifications": classifications,
                "success": True,
                "provider": "huggingface"
            }
                
        # Handle errors
        return {
            "error": f"API error: {response.status_code} - {response.text}",
            "success": False
        }
    except Exception as e:
        logging.error(f"Error in classify_image: {str(e)}")
        return {"error": str(e), "success": False}

def detect_objects(image_path: str) -> Dict[str, Any]:
    """
    Detect and locate objects in an image 
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Object detections with bounding boxes and confidence scores
    """
    try:
        model = MODELS["object_detection"]
        url = f"{HF_API_URL}/{model}"
        
        # Check if file exists
        if not os.path.exists(image_path):
            return {"error": f"Image file not found: {image_path}", "success": False}
        
        # Load and send the image
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            
        headers = get_headers()
        response = requests.post(url, headers=headers, data=image_bytes, timeout=45)  # Longer timeout for object detection
            
        if response.status_code == 200:
            results = response.json()
            
            # Process and format the detections
            detections = []
            if isinstance(results, list):
                for detection in results:
                    if "scores" in detection and "labels" in detection and "boxes" in detection:
                        # Process the detected objects
                        for i, (score, label, box) in enumerate(zip(
                                detection["scores"], 
                                detection["labels"], 
                                detection["boxes"])):
                            
                            # Only include detections with reasonable confidence
                            if score > 0.5:  
                                detections.append({
                                    "label": label,
                                    "confidence": score,
                                    "box": box  # [x1, y1, x2, y2] coordinates
                                })
            
            return {
                "detections": detections,
                "success": True,
                "provider": "huggingface"
            }
                
        # Handle errors
        return {
            "error": f"API error: {response.status_code} - {response.text}",
            "success": False
        }
    except Exception as e:
        logging.error(f"Error in detect_objects: {str(e)}")
        return {"error": str(e), "success": False}

def analyze_travel_photo(image_path: str) -> Dict[str, Any]:
    """
    Comprehensive analysis of travel photos - combines multiple analyses for rich results.
    This is particularly useful for travel apps to automatically organize and tag photos.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Comprehensive analysis including description, classifications, landmarks, etc.
    """
    try:
        # Run multiple analyses in sequence
        description_result = describe_image(image_path)
        classification_result = classify_image(image_path)
        
        # Prepare a comprehensive result
        result = {
            "success": True,
            "provider": "huggingface",
            "description": description_result.get("description", ""),
            "tags": []
        }
        
        # Add classification tags
        if classification_result.get("success", False):
            classifications = classification_result.get("classifications", [])
            result["tags"] = [item["label"] for item in classifications]
        
        # Use classification confidence to determine type of photo
        photo_type = "unknown"
        confidence_threshold = 0.7
        
        if classification_result.get("success", False):
            classifications = classification_result.get("classifications", [])
            
            # Detect common travel photo types with high confidence
            nature_keywords = ["mountain", "beach", "forest", "ocean", "river", "lake", "nature", "landscape"]
            city_keywords = ["city", "building", "architecture", "street", "urban"]
            food_keywords = ["food", "meal", "dish", "restaurant", "cuisine"]
            
            for cls in classifications:
                label = cls["label"].lower()
                confidence = cls["confidence"]
                
                if confidence > confidence_threshold:
                    if any(keyword in label for keyword in nature_keywords):
                        photo_type = "nature"
                        break
                    elif any(keyword in label for keyword in city_keywords):
                        photo_type = "urban"
                        break
                    elif any(keyword in label for keyword in food_keywords):
                        photo_type = "food"
                        break
        
        result["photo_type"] = photo_type
        
        return result
    except Exception as e:
        logging.error(f"Error in analyze_travel_photo: {str(e)}")
        return {"error": str(e), "success": False}

def organize_travel_photos(directory_path: str) -> Dict[str, Any]:
    """
    Batch analyze and organize travel photos in a directory
    
    Args:
        directory_path (str): Path to directory containing travel photos
        
    Returns:
        dict: Organization results with categorized photos
    """
    try:
        # Check if directory exists
        if not os.path.isdir(directory_path):
            return {"error": f"Directory not found: {directory_path}", "success": False}
        
        # Find image files
        image_extensions = ['.jpg', '.jpeg', '.png']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(list(Path(directory_path).glob(f"*{ext}")))
            image_files.extend(list(Path(directory_path).glob(f"*{ext.upper()}")))
        
        if not image_files:
            return {"error": "No image files found in directory", "success": False}
        
        # Organize by categories
        categories = {
            "nature": [],
            "urban": [],
            "food": [],
            "people": [],
            "unknown": []
        }
        
        # Process each image
        for image_file in image_files:
            analysis = analyze_travel_photo(str(image_file))
            
            if analysis.get("success", False):
                photo_type = analysis.get("photo_type", "unknown")
                
                # Add to appropriate category
                if photo_type in categories:
                    categories[photo_type].append({
                        "file": str(image_file),
                        "description": analysis.get("description", ""),
                        "tags": analysis.get("tags", [])
                    })
                else:
                    categories["unknown"].append({
                        "file": str(image_file),
                        "description": analysis.get("description", ""),
                        "tags": analysis.get("tags", [])
                    })
        
        return {
            "categories": categories,
            "total_images": len(image_files),
            "success": True
        }
    except Exception as e:
        logging.error(f"Error in organize_travel_photos: {str(e)}")
        return {"error": str(e), "success": False}