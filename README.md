# Image Analysis with Hugging Face API

This feature allows you to analyze images through the chat interface using Hugging Face's free AI services. This implementation helps offload less computationally intensive tasks from OpenRouter/OpenAI, reducing costs while maintaining functionality.

## Features

- **Image Description**: Get a detailed caption and classification of any image
- **Object Detection**: Identify and count objects in images
- **Travel Photo Analysis**: Specialized analysis of travel photos (landmarks, nature, etc.)
- **Image Organization**: Group images by content automatically

## How to Use

1. **Upload an image** using the file attachment button in the chat interface
2. **Use commands** in the chat to analyze your image:
   - `describe image` - Generate a description of your image
   - `detect objects` - Identify objects in your image
   - `analyze image for travel` - Specialized analysis for travel photos

## Implementation Details

- Uses Hugging Face's free inference API as a cost-effective alternative to OpenAI/OpenRouter
- Implements a three-tier fallback system: OpenAI → OpenRouter → Hugging Face → Local
- All image processing happens through the existing chat interface with no separate pages needed
- Supports both text-based and visual AI tasks with the same command structure

## Models Used

- **Image Captioning**: Salesforce/blip-image-captioning-base
- **Image Classification**: google/vit-base-patch16-224
- **Object Detection**: facebook/detr-resnet-50
- **Text Embeddings**: BAAI/bge-small-en-v1.5

## Example Usage

```
User: [Uploads an image of a mountain landscape]
User: describe image

Nous: 🖼️ Analyzing your image using Hugging Face's free AI services...
      🔍 Image Description: A beautiful mountain landscape with snow-capped peaks and a clear blue sky
      🏷️ Categories: landscape, mountain, nature
      📊 Primary classification: Mountain (97.5% confident)
```