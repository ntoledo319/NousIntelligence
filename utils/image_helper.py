"""
Image processing and analysis utilities for Nous
Uses Hugging Face's free services for cost-effective image analysis
"""

import os
import base64
import logging
import tempfile
from io import BytesIO
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from utils.huggingface_helper import (
    hf_image_caption,
    hf_image_classification,
    hf_object_detection,
    hf_image_to_text,
    hf_image_segmentation,
    process_image_for_analysis
)

# Create temp directory if it doesn't exist
os.makedirs("temp", exist_ok=True)

def describe_image(image_data: bytes) -> Dict[str, Any]:
    """Generate a detailed description of an image using Hugging Face's API"""
    try:
        # Process and save the image for analysis
        temp_path = process_image_for_analysis(image_data)
        if not temp_path:
            return {"error": "Failed to process image"}

        # Generate a caption using Hugging Face
        caption = hf_image_caption(temp_path)

        # Classify the image for additional context
        classification = hf_image_classification(temp_path)

        # Format the result
        result = {
            "description": caption,
            "categories": [],
            "confidence": 0
        }

        # Add classification data if available
        if classification and not classification.get("error"):
            result["categories"] = [c["label"] for c in classification["categories"][:3]]
            if classification.get("top_category"):
                result["top_category"] = classification["top_category"]
                result["confidence"] = classification["confidence"]

        return result
    except Exception as e:
        logging.error(f"Error describing image: {str(e)}")
        return {"error": f"Image analysis failed: {str(e)}"}

def detect_objects_in_image(image_data: bytes) -> Dict[str, Any]:
    """Detect and count objects in an image using Hugging Face's API"""
    try:
        # Process and save the image for analysis
        temp_path = process_image_for_analysis(image_data)
        if not temp_path:
            return {"error": "Failed to process image"}

        # Detect objects using Hugging Face
        detection = hf_object_detection(temp_path)

        return detection
    except Exception as e:
        logging.error(f"Error detecting objects in image: {str(e)}")
        return {"error": f"Object detection failed: {str(e)}"}

def analyze_image_for_travel(image_data: bytes) -> Dict[str, Any]:
    """Specialized analysis of travel photos using Hugging Face"""
    try:
        # Process and save the image for analysis
        temp_path = process_image_for_analysis(image_data)
        if not temp_path:
            return {"error": "Failed to process image"}

        # Get a general description
        caption = hf_image_caption(temp_path)

        # Classify the image
        classification = hf_image_classification(temp_path)

        # Check for landmarks, scenery, or other travel-related content
        prompt = "Describe this travel photo, mentioning any landmarks, scenery, or cultural elements"
        travel_analysis = hf_image_to_text(temp_path, prompt=prompt)

        # Format the results
        result = {
            "description": caption,
            "categories": [],
            "travel_details": travel_analysis,
            "is_landmark": False,
            "is_nature": False,
            "is_food": False,
        }

        # Check for specific categories
        if classification and not classification.get("error"):
            result["categories"] = [c["label"] for c in classification["categories"][:5]]

            # Check for common travel photo types
            categories_lower = [c.lower() for c in result["categories"]]
            if any(term in " ".join(categories_lower) for term in ["landmark", "building", "monument", "statue", "tower", "temple"]):
                result["is_landmark"] = True
            if any(term in " ".join(categories_lower) for term in ["nature", "landscape", "mountain", "beach", "ocean", "forest"]):
                result["is_nature"] = True
            if any(term in " ".join(categories_lower) for term in ["food", "meal", "dish", "restaurant", "cuisine"]):
                result["is_food"] = True

        return result
    except Exception as e:
        logging.error(f"Error analyzing travel image: {str(e)}")
        return {"error": f"Travel image analysis failed: {str(e)}"}

def encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64 for API calls or display"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_string
    except Exception as e:
        logging.error(f"Error encoding image: {str(e)}")
        return ""

def segment_image(image_data: bytes) -> Dict[str, Any]:
    """Segment an image into semantic regions using Hugging Face's API"""
    try:
        # Process and save the image for analysis
        temp_path = process_image_for_analysis(image_data)
        if not temp_path:
            return {"error": "Failed to process image"}

        # Perform segmentation
        segmentation = hf_image_segmentation(temp_path)

        return segmentation
    except Exception as e:
        logging.error(f"Error segmenting image: {str(e)}")
        return {"error": f"Image segmentation failed: {str(e)}"}

def organize_images_by_content(image_files: List[Dict[str, Union[bytes, str]]]) -> Dict[str, List[str]]:
    """Group multiple images by their content"""
    results = {}

    try:
        # Process each image
        for image_info in image_files:
            image_data = image_info.get("data")
            filename = image_info.get("filename")

            if not image_data or not filename:
                continue

            # Analyze the image
            temp_path = process_image_for_analysis(image_data)
            if not temp_path:
                continue

            # Classify the image
            classification = hf_image_classification(temp_path)

            if classification and not classification.get("error") and classification.get("top_category"):
                category = classification["top_category"].replace("_", " ").title()

                # Initialize category if it doesn't exist
                if category not in results:
                    results[category] = []

                # Add image filename to the category
                results[category].append(filename)

        return results
    except Exception as e:
        logging.error(f"Error organizing images: {str(e)}")
        return {"error": f"Image organization failed: {str(e)}"}

def get_uploaded_image_file(user_id: int) -> Optional[str]:
    """Get path to most recently uploaded image for a user"""
    try:
        # Create user upload directory if it doesn't exist
        user_dir = os.path.join("uploads", f"user_{user_id}")
        os.makedirs(user_dir, exist_ok=True)

        # Get the most recent file
        files = [f for f in os.listdir(user_dir) if os.path.isfile(os.path.join(user_dir, f))]
        if not files:
            return None

        # Sort by modification time, newest first
        files.sort(key=lambda x: os.path.getmtime(os.path.join(user_dir, x)), reverse=True)

        # Return the path to the most recent file
        return os.path.join(user_dir, files[0])
    except Exception as e:
        logging.error(f"Error getting uploaded image: {str(e)}")
        return None