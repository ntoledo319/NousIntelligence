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

def parse_natural_language(command_text):
    """
    Parse natural language commands into structured format.
    
    Args:
        command_text (str): The natural language command
        
    Returns:
        dict: Structured command with confidence level
    """
    try:
        from utils.cache_helper import cache_result
        
        # Inner function that can be cached 
        @cache_result(ttl_seconds=3600)  # Cache for 1 hour since command understanding is stable
        def _get_parsed_command(cmd_text):
            messages = [
                {
                    "role": "system", 
                    "content": """You are a command parser. Convert natural language commands to structured commands.
                    Examples:
                    - "Add a meeting with John at 3pm tomorrow" -> "add Meeting with John at 3pm tomorrow"
                    - "What's the weather like in New York?" -> "weather New York"
                    - "Check my calendar for Friday" -> "what's my day Friday"
                    
                    Respond in JSON format with:
                    - structured_command: The parsed command
                    - confidence: A value from 0 to 1 indicating how confident you are
                    - error: Only include if there's an error parsing
                    """
                },
                {"role": "user", "content": cmd_text}
            ]
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Using a smaller model for efficiency
                messages=messages,
                temperature=0.2,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content is not None:
                return json.loads(content)
            return {"error": "Empty response", "confidence": 0, "structured_command": cmd_text}
        
        # Call the cached function
        parsed_data = _get_parsed_command(command_text)
        logging.info(f"Parsed command: {parsed_data}")
        return parsed_data
        
    except Exception as e:
        logging.error(f"Error parsing natural language: {str(e)}")
        return {"error": str(e), "confidence": 0, "structured_command": command_text}

def analyze_gmail_content(content, headers=None, user_id=None):
    """
    Analyze the content of a Gmail message using AI.
    
    Args:
        content (str): The email content
        headers (dict, optional): Email headers like subject, from, etc.
        user_id (str, optional): User ID for personalized analysis
        
    Returns:
        dict: Analysis results
    """
    try:
        from utils.cache_helper import cache_result
        
        # Create a unique key for caching based on content
        import hashlib
        email_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Inner function that can be cached
        @cache_result(ttl_seconds=86400)  # Cache for 24 hours since email content doesn't change
        def _analyze_email(content_to_analyze, headers_str, email_id):
            messages = [
                {
                    "role": "system", 
                    "content": """You are an email analyzer. Extract key information from the email and provide a summary.
                    Focus on:
                    - Main topic or purpose of the email
                    - Action items or requests
                    - Important dates or deadlines
                    - Key people mentioned
                    
                    Respond in JSON format with:
                    - summary: Brief summary of the email
                    - action_items: List of action items
                    - important_dates: List of important dates
                    - key_people: List of key people
                    - sentiment: Overall sentiment (positive, neutral, negative)
                    """
                },
                {
                    "role": "user", 
                    "content": f"Email headers:\n{headers_str}\n\nEmail content:\n{content_to_analyze}"
                }
            ]
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            content_str = response.choices[0].message.content
            if content_str is not None:
                return json.loads(content_str)
            return {"error": "Empty response", "summary": "Could not analyze email content."}
            
        # Prepare the headers for context
        header_context = ""
        if headers:
            header_context = "\n".join([f"{key}: {value}" for key, value in headers.items()])
        
        # Call the cached function
        analysis = _analyze_email(content, header_context, email_hash)
        
        # Store analysis in knowledge base if applicable (do this outside the cached function)
        if user_id and 'summary' in analysis:
            knowledge_entry = f"Email Analysis: {analysis['summary']}"
            add_to_knowledge_base(knowledge_entry, user_id, source="email_analysis")
            
        return analysis
        
    except Exception as e:
        logging.error(f"Error analyzing Gmail content: {str(e)}")
        return {"error": str(e), "summary": "Could not analyze email content."}

def analyze_gmail_threads(threads, user_id=None):
    """
    Analyze a Gmail thread (multiple messages) to extract insights.
    
    Args:
        threads (list): List of messages in a thread
        user_id (str, optional): User ID for personalized analysis
        
    Returns:
        dict: Thread analysis with conversation insights
    """
    try:
        # Extract full conversation from threads
        conversation = []
        for message in threads:
            sender = message.get('sender', 'Unknown')
            content = message.get('content', '')
            date = message.get('date', '')
            
            conversation.append(f"[{date}] {sender}:\n{content}\n")
        
        full_conversation = "\n".join(conversation)
        
        messages = [
            {
                "role": "system", 
                "content": """You are an email thread analyzer. Analyze the conversation thread and extract insights.
                Focus on:
                - Thread summary and main topic
                - Key points of discussion
                - Decisions made or conclusions reached
                - Open questions or unresolved issues
                - Overall tone of conversation
                
                Respond in JSON format with:
                - thread_summary: Brief summary of the entire thread
                - key_points: List of key discussion points
                - decisions: List of decisions made or conclusions reached
                - open_items: List of unresolved questions or issues
                - tone: Overall tone of the conversation
                """
            },
            {"role": "user", "content": full_conversation}
        ]
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=600,
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        # Store thread analysis in knowledge base if applicable
        if user_id and 'thread_summary' in analysis:
            knowledge_entry = f"Email Thread Analysis: {analysis['thread_summary']}"
            add_to_knowledge_base(knowledge_entry, user_id, source="email_thread_analysis")
            
        return analysis
        
    except Exception as e:
        logging.error(f"Error analyzing Gmail thread: {str(e)}")
        return {"error": str(e), "thread_summary": "Could not analyze email thread."}

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
        # Step 1: Extract the user query (if any)
        user_query = None
        if messages and messages[-1]['role'] == 'user':
            user_query = messages[-1]['content']
        
        # Initialize debug info
        debug_info = {}
        
        # Step 2: Check if the user's query matches anything in the knowledge base
        knowledge_results = []
        if user_query:
            knowledge_results = query_knowledge_base(user_query, user_id, similarity_threshold=0.1)
        
        # Step 3: Prepare the conversation with appropriate system message
        conversation = []
        
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
        
        # Utility function to hash conversation for caching
        def hash_conversation(conv_messages):
            import hashlib
            # Convert messages to a consistent string representation
            msg_str = str([(m.get('role', ''), m.get('content', '')) for m in conv_messages])
            return hashlib.md5(msg_str.encode()).hexdigest()
            
        # Use cache helper for the actual API call
        from utils.cache_helper import cache_result
        
        # This function encapsulates the API call for caching
        @cache_result(ttl_seconds=300)  # Cache for 5 minutes to balance freshness and efficiency
        def get_ai_response(conversation_hash, temperature, max_tokens):
            # We'll pass typed dictionaries directly to the API
            from typing import List, Dict, Any
            typed_messages: List[Dict[str, Any]] = []
            
            for message in conversation:
                role = message.get('role', '')
                content = message.get('content', '')
                if role and content:
                    typed_messages.append({"role": role, "content": content})
            
            response = openai.chat.completions.create(
                model="gpt-4o",  # Use the latest model
                messages=typed_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content
            return None
        
        # Get the response using the cached function
        conv_hash = hash_conversation(conversation)
        response_text = get_ai_response(conv_hash, 0.7, 800)
        
        if not response_text:
            response_text = "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."
        
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