"""
AI Helper module for handling conversations with OpenAI.
Includes integration with the knowledge base for enhanced responses.
"""

import os
import logging
import json
from datetime import datetime
from openai import OpenAI
from utils.knowledge_helper import query_knowledge_base, add_to_knowledge_base

# Initialize OpenAI client with key directly from .env file
env_path = '.env'
openai_api_key = ""
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip().startswith('OPENAI_API_KEY='):
                openai_api_key = line.strip().split('=', 1)[1]
                break

if openai_api_key:
    logging.info(f"Using OpenAI API key (first 8 chars): {openai_api_key[:8]}")
else:
    logging.warning("OpenAI API key not found in .env file")

openai = OpenAI(api_key=openai_api_key)

def handle_conversation(messages, user_id=None, include_debug=False):
    """
    Handle a conversation with OpenAI, enhanced with knowledge base integration.
    
    Args:
        messages (list): List of message objects with role and content
        user_id (str, optional): User ID for personalized knowledge
        include_debug (bool): Whether to include debug info in response
        
    Returns:
        dict: Response with AI output and optional debug info
    """
    try:
        # Step 1: Check if the user's query matches anything in the knowledge base
        if messages and messages[-1]['role'] == 'user':
            user_query = messages[-1]['content']
            knowledge_results = query_knowledge_base(user_query, user_id, similarity_threshold=0.1)
        else:
            knowledge_results = []
            
        debug_info = {}
        
        # Step 2: If knowledge was found, integrate it into the prompt
        if knowledge_results:
            # Format knowledge context
            knowledge_context = "\n\n".join([
                f"[Relevant knowledge {i+1} (similarity: {similarity:.2f})] {entry.content}" 
                for i, (entry, similarity) in enumerate(knowledge_results)
            ])
            
            # Save debug info
            debug_info['knowledge_used'] = [
                {
                    'id': entry.id,
                    'content': entry.content,
                    'similarity': similarity,
                    'source': entry.source,
                    'created_at': entry.created_at.isoformat() if entry.created_at else None
                }
                for entry, similarity in knowledge_results
            ]
            
            # Add system message with knowledge context
            system_message = {
                'role': 'system',
                'content': f"""You are Nous, an AI personal assistant with a self-learning knowledge base.
                Use the following relevant information from your knowledge base to help answer the user's question.
                
                {knowledge_context}
                
                Based on this information and your general knowledge, provide a helpful, accurate response.
                Your response should feel natural and not explicitly reference the knowledge base unless necessary."""
            }
            
            # Insert system message at the beginning
            conversation = [system_message] + messages
        else:
            # No knowledge found, use standard prompt
            system_message = {
                'role': 'system',
                'content': "You are Nous, an AI personal assistant. Provide helpful, accurate, and friendly responses."
            }
            conversation = [system_message] + messages
            debug_info['knowledge_used'] = []
        
        # Step 3: Call OpenAI API for the response
        response = openai.chat.completions.create(
            model="gpt-4o",  # Use the latest model
            messages=conversation,
            temperature=0.7,
            max_tokens=800
        )
        
        # Extract the response content
        response_text = response.choices[0].message.content
        
        # Step 4: Store the assistant's response in the knowledge base for future retrieval
        if user_query and response_text:
            try:
                # Store a summarized version that pairs the query with the response
                knowledge_entry = f"Q: {user_query}\nA: {response_text}"
                add_to_knowledge_base(knowledge_entry, user_id, source="conversation")
                debug_info['knowledge_added'] = True
            except Exception as e:
                logging.error(f"Error adding response to knowledge base: {str(e)}")
                debug_info['knowledge_added'] = False
        
        # Prepare the final response
        result = {
            'response': response_text
        }
        
        if include_debug:
            result['debug'] = debug_info
            
        return result
        
    except Exception as e:
        logging.error(f"Error in handle_conversation: {str(e)}")
        return {
            'response': "I apologize, but I'm having trouble processing your request right now. Please try again in a moment.",
            'error': str(e) if include_debug else None
        }