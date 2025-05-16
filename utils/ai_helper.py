"""
AI Helper module for handling conversations with OpenAI.
Includes integration with the knowledge base for enhanced responses.
"""

import os
import logging
import json
from datetime import datetime
from openai import OpenAI
# Import knowledge base functions at runtime to avoid circular imports

# Import our key configuration module
from utils.key_config import (
    OPENAI_API_KEY, OPENROUTER_API_KEY, HF_ACCESS_TOKEN,
    USE_HUGGINGFACE, USE_OPENROUTER, get_preferred_service
)

# Only create the OpenAI client if we have a valid OpenAI key
if OPENAI_API_KEY:
    openai = OpenAI(api_key=OPENAI_API_KEY)
else:
    # Create a dummy client for type checking, but we won't use it
    openai = None

# Always check the preferred service for each API call
preferred_service = get_preferred_service()

# Log our API configuration
if preferred_service == "huggingface":
    logging.info("NOUS will use Hugging Face API service for cost-effective AI functionality")
    logging.info(f"Hugging Face token found: {bool(HF_ACCESS_TOKEN)}")
elif preferred_service == "openrouter":
    logging.info("NOUS will use OpenRouter API service for AI functionality")
    logging.info(f"OpenRouter key found: {bool(OPENROUTER_API_KEY)}")
elif preferred_service == "openai":
    logging.info("NOUS will use OpenAI API service for AI functionality") 
    logging.info(f"OpenAI key found: {bool(OPENAI_API_KEY)}")
elif preferred_service == "local":
    logging.info("NOUS will use local fallbacks for AI functionality")
else:
    logging.warning("No valid AI service keys found. Some features may not work correctly")

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
            
            # Import our key configuration which has the latest status
            from utils.key_config import get_preferred_service
            
            # Check if we're using OpenRouter as the preferred service
            if get_preferred_service() == "openrouter":
                # Import our OpenRouter helper
                from utils.openrouter_helper import chat_completion
                
                # Format the response for OpenRouter
                response_text = chat_completion(
                    messages=messages,
                    model="openai/gpt-4-turbo",
                    temperature=0.3,
                    max_tokens=500
                )
                
                # Create a response object similar to OpenAI's
                class MockResponse:
                    def __init__(self, content):
                        self.choices = [type('obj', (object,), {
                            'message': type('obj', (object,), {'content': content})
                        })]
                
                response = MockResponse(response_text)
            else:
                # Use standard OpenAI client
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
            from utils.knowledge_helper import add_to_knowledge_base
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
            from utils.knowledge_helper import add_to_knowledge_base
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
            
            # Check if we should use OpenRouter
            openrouter_key = os.environ.get("OPENROUTER_API_KEY")
            if openrouter_key:
                # Use our dedicated OpenRouter helper
                from utils.openrouter_helper import chat_completion
                logging.info("Using OpenRouter API for chat completion")
                
                # Map to OpenRouter model format
                openrouter_model = "openai/gpt-4-turbo"  # OpenRouter equivalent of gpt-4o
                
                response_text = chat_completion(
                    messages=typed_messages,
                    model=openrouter_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Create a response object matching OpenAI's format for consistent handling
                class MockResponse:
                    class Choice:
                        class Message:
                            def __init__(self, content):
                                self.content = content
                                
                        def __init__(self, content):
                            self.message = self.Message(content)
                    
                    def __init__(self, content):
                        self.choices = [self.Choice(content)]
                
                # If we got a response from OpenRouter, return it in the expected format
                if response_text:
                    response = MockResponse(response_text)
                else:
                    # Fall back to OpenAI if OpenRouter fails
                    response = openai.chat.completions.create(
                        model="gpt-4o",
                        messages=typed_messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
            else:
                # Use standard OpenAI API
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

def cfhat(message_text, user_id=None, feature=None, context=None, include_debug=False):
    """
    Central function for all chat-related features. All features should connect through this
    function to ensure consistent handling, knowledge storage, and model selection.
    
    Args:
        message_text (str): The user's message
        user_id (str, optional): User ID for personalized knowledge
        feature (str, optional): The specific feature being used (e.g., 'email_analysis', 'weather', 'travel')
        context (dict, optional): Additional context relevant to the feature
        include_debug (bool): Whether to include debug info in response
        
    Returns:
        str or dict: Response to the user's message
    """
    try:
        logging.info(f"cfhat called with feature={feature}")
        
        # Prepare the conversation messages
        messages = []
        
        # If we have a specific feature, add context and feature-specific instructions
        if feature:
            # Create a specialized system message based on the feature
            system_content = "You are Nous, an AI personal assistant. "
            
            # Add feature-specific context and instructions
            if feature == "email_analysis":
                system_content += "You're analyzing an email to extract key information and insights."
                if context and "email_content" in context:
                    message_text = context["email_content"]
            elif feature == "weather":
                system_content += "You're providing weather information and insights."
                if context and "weather_data" in context:
                    system_content += f"\nCurrent weather data: {json.dumps(context['weather_data'])}"
            elif feature == "travel":
                system_content += "You're helping with travel planning and recommendations."
                if context and "destination" in context:
                    system_content += f"\nDestination: {context['destination']}"
            elif feature == "dbt":
                system_content += "You're providing Dialectical Behavior Therapy (DBT) support."
            elif feature == "spotify":
                system_content += "You're helping with music recommendations and Spotify features."
            elif feature == "budget":
                system_content += "You're assisting with budget management and financial insights."
            elif feature == "shopping":
                system_content += "You're helping with shopping list management and recommendations."
            
            # Create the system message with feature-specific instructions
            messages.append({
                "role": "system",
                "content": system_content
            })
        
        # Add the user's message
        messages.append({
            "role": "user",
            "content": message_text
        })
        
        # Use the handle_conversation function to get a response
        response = handle_conversation(messages, user_id, include_debug)
        
        # If we have a feature that needs post-processing, handle it here
        if feature and feature == "email_analysis" and context and "format" in context:
            if context["format"] == "json":
                try:
                    # Try to extract structured data from the response
                    from utils.email_parser import extract_structured_data
                    return extract_structured_data(response['response'])
                except Exception as e:
                    logging.error(f"Error extracting structured data: {str(e)}")
        
        # Return either the full response object or just the text based on include_debug
        if include_debug:
            return response
        else:
            return response['response']
            
    except Exception as e:
        logging.error(f"Error in cfhat: {str(e)}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."

# Import these at the end to avoid circular dependencies
try:
    from utils.knowledge_helper import query_knowledge_base, add_to_knowledge_base
except ImportError:
    # Create placeholder functions for environments without knowledge_helper
    def query_knowledge_base(query, user_id=None, similarity_threshold=0.0):
        return []
        
    def add_to_knowledge_base(entry, user_id=None, source=None):
        pass