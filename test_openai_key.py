#!/usr/bin/env python
import os
import logging
from openai import OpenAI
import dotenv

# Load environment variables
logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv()

# Manually set OpenAI API key from .env file
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip().startswith('OPENAI_API_KEY='):
                key = line.strip().split('=', 1)[1]
                logging.info(f"Found OpenAI API key in .env file, setting in environment")
                os.environ['OPENAI_API_KEY'] = key

# Print environment variables (masking sensitive parts)
env_vars = os.environ.keys()
for key in env_vars:
    if key.endswith('KEY') or key.endswith('SECRET'):
        value = os.environ.get(key)
        if value:
            # Show just the beginning of the key
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"{key}: {masked_value}")

# Get OpenAI API key directly
openai_api_key = os.environ.get("OPENAI_API_KEY")
print(f"\nDirect OPENAI_API_KEY check: {'Found' if openai_api_key else 'Not found'}")
if openai_api_key:
    print(f"Key starts with: {openai_api_key[:8]}...")

# Test OpenAI API
if openai_api_key:
    print("\nTesting OpenAI API...")
    try:
        client = OpenAI(api_key=openai_api_key)
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input="Testing OpenAI embeddings API"
        )
        print(f"API test successful! Embedding size: {len(response.data[0].embedding)}")
        print(f"First few dimensions: {response.data[0].embedding[:3]}")
    except Exception as e:
        print(f"API test failed: {str(e)}")