import os
import logging
import json
import datetime
from typing import Dict, List, Any, Optional, Union, cast
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam

# Import knowledge base utilities
try:
    from utils.knowledge_helper import query_knowledge_base, add_to_knowledge_base
    KNOWLEDGE_BASE_ENABLED = True
except ImportError:
    # If knowledge_helper module is not available, provide dummy functions
    KNOWLEDGE_BASE_ENABLED = False
    
    def query_knowledge_base(question, user_id=None, top_k=3, similarity_threshold=0.75):
        return []
        
    def add_to_knowledge_base(content, user_id=None, source="conversation"):
        pass

# Import adaptive conversation utilities once here to prevent circular imports
try:
    from utils.adaptive_conversation import get_current_difficulty, get_difficulty_context, adapt_response
    ADAPTIVE_CONVERSATION_ENABLED = True
except ImportError:
    # If adaptive_conversation module is not available, provide dummy functions
    ADAPTIVE_CONVERSATION_ENABLED = False
    
    def get_current_difficulty():
        return "intermediate"
        
    def get_difficulty_context():
        return ""
        
    def adapt_response(response, explain_technical_terms=True):
        return response
        
# Import character customization utilities
try:
    from utils.character_customization import get_character_system_prompt, apply_character_style
    CHARACTER_CUSTOMIZATION_ENABLED = True
except ImportError:
    # If character_customization module is not available, provide dummy functions
    CHARACTER_CUSTOMIZATION_ENABLED = False
    
    def get_character_system_prompt():
        return "You are NOUS, a helpful and friendly AI assistant."
        
    def apply_character_style(response):
        return response
        
# Import enhanced memory utilities
try:
    from utils.enhanced_memory import get_user_memory
    ENHANCED_MEMORY_ENABLED = True
except ImportError:
    # If enhanced_memory module is not available, provide dummy functions
    ENHANCED_MEMORY_ENABLED = False
    
    def get_user_memory(user_id):
        class DummyMemory:
            def add_message(self, role, content):
                pass
                
            def get_recent_messages(self, count=None):
                return []
                
            def get_memory_context(self):
                return ""
        return DummyMemory()

# Initialize OpenAI client if key is present
api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
client = None

if api_key:
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        logging.error(f"Error initializing OpenAI client: {str(e)}")

# Global conversation memory with context awareness
class ConversationMemory:
    def __init__(self, max_history: int = 15, context_window_days: int = 7):
        self.user_histories: Dict[str, List[Dict[str, str]]] = {}
        self.user_contexts: Dict[str, Dict[str, Any]] = {}
        self.max_history = max_history
        self.context_window_days = context_window_days
    
    def add_message(self, user_id: str, role: str, content: str) -> None:
        """Add a message to the user's conversation history"""
        if user_id not in self.user_histories:
            self.user_histories[user_id] = []
        
        self.user_histories[user_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        
        # Trim history if needed
        if len(self.user_histories[user_id]) > self.max_history:
            self.user_histories[user_id] = self.user_histories[user_id][-self.max_history:]
    
    def add_context(self, user_id: str, context_type: str, context_data: Any) -> None:
        """Add context information for a user"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {}
        
        if context_type not in self.user_contexts[user_id]:
            self.user_contexts[user_id][context_type] = []
        
        # Add timestamp to the context
        context_entry = {
            "data": context_data,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        self.user_contexts[user_id][context_type].append(context_entry)
        
        # Trim old contexts
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=self.context_window_days)
        self.user_contexts[user_id][context_type] = [
            entry for entry in self.user_contexts[user_id][context_type]
            if datetime.datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
        ]
    
    def get_recent_messages(self, user_id: str, count: Optional[int] = None) -> List[Dict[str, str]]:
        """Get the most recent messages for a user"""
        if user_id not in self.user_histories:
            return []
        
        # If count is None, use self.max_history
        message_count = self.max_history if count is None else count
        history = self.user_histories[user_id][-message_count:]
        # Return only role and content for OpenAI API compatibility
        return [{"role": msg["role"], "content": msg["content"]} for msg in history]
    
    def get_context_summary(self, user_id: str) -> str:
        """Get a summary of the user's context"""
        if user_id not in self.user_contexts:
            return "No context available for this user."
        
        summary = []
        for context_type, contexts in self.user_contexts[user_id].items():
            if contexts:
                summary.append(f"{context_type.capitalize()}:")
                for context in contexts[-3:]:  # Show only the 3 most recent of each type
                    data_str = str(context["data"])
                    if len(data_str) > 100:
                        data_str = data_str[:100] + "..."
                    summary.append(f"- {data_str}")
        
        if not summary:
            return "No context available for this user."
        
        return "\n".join(summary)
    
    def get_formatted_context(self, user_id: str) -> str:
        """Get a formatted context string for the user"""
        ctx_summary = self.get_context_summary(user_id)
        return f"User Context Information:\n{ctx_summary}"

# Initialize the global conversation memory
conversation_memory = ConversationMemory()

def parse_natural_language(user_input: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Use OpenAI to parse natural language input and convert it to a structured command
    
    Args:
        user_input: The user's natural language input
        user_id: Optional user identifier for context awareness
        
    Returns:
        dict: A dictionary with parsed command information
    """
    try:
        if not client:
            return {"error": "Missing OpenAI API key"}
        
        system_prompt = """
        You are a command parser for a personal assistant called NOUS.
        Convert the user's natural language input to one of the following command formats:
        
        1. Calendar: "add [event] at [time]"
        2. Task: "add task: [task]"
        3. Note: "add note: [note]"
        4. Mood: "log mood: [mood details]"
        5. Workout: "log workout: [workout details]"
        6. Music: "play [song/artist]"
        7. Query: "what's my day"
        8. AA Reflection: "show aa reflection"
        9. Doctor: "add doctor [name]"
        10. Doctor List: "list doctors"
        11. Appointment: "set appointment with [doctor] on [date/time]"
        12. Appointments List: "show appointments"
        13. Chat: "chat: [message]" - For free-form conversation with the AI assistant
        14. Analyze Email: "analyze email: [email content or ID]"
        15. Shopping: "add to shopping list: [items]" or "show shopping lists"
        16. Medication: "refill [medication]" or "check medications"
        17. Weather: "check weather in [location]" or "get pain forecast"
        18. Travel: "plan trip to [destination]" or "check my itinerary"
        19. Smart Home: "turn on [device]" or "set temperature to [value]"
        20. Budget: "add expense: [amount] for [category]" or "show budget summary"
        
        If the user is asking about a doctor appointment or mentions a doctor visit, use the appropriate doctor or appointment command format.
        
        If the user seems to be having a conversation or asking a general question that doesn't fit other commands, use the "chat" command type.
        
        If the user wants to analyze an email or get insights from their email, use the "analyze_email" command type.
        
        Respond with JSON in this exact format:
        {
            "command_type": "calendar|task|note|mood|workout|music|query|reflection|doctor|doctor_list|appointment|appointments_list|chat|analyze_email|shopping|medication|weather|travel|smart_home|budget",
            "structured_command": "the exact command in the proper format",
            "confidence": 0.0 to 1.0
        }
        """
        
        # Add context if user_id is provided
        context_str = ""
        if user_id:
            context_str = conversation_memory.get_formatted_context(user_id)
            if len(context_str) > 10:  # Only add if there's meaningful context
                system_prompt += f"\n\nUser Context (use this to better understand the request):\n{context_str}"
        
        # Prepare messages with proper typing
        messages: List[ChatCompletionMessageParam] = []
        
        # Add system message
        system_msg: ChatCompletionSystemMessageParam = {
            "role": "system",
            "content": system_prompt
        }
        messages.append(system_msg)
        
        # Add user message
        user_msg: ChatCompletionUserMessageParam = {
            "role": "user",
            "content": user_input
        }
        messages.append(user_msg)
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=messages,
                response_format={"type": "json_object"}
            )
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            return {"error": f"Error calling OpenAI API: {str(e)}"}
        
        result = response.choices[0].message.content
        
        # The response is already JSON formatted
        try:
            if result is not None and result:
                parsed = json.loads(result)
                
                # Store the interaction in conversation memory if user_id provided
                if user_id:
                    conversation_memory.add_message(user_id, "user", user_input)
                    # Also store the parsed command as context
                    conversation_memory.add_context(
                        user_id, 
                        "command_history", 
                        f"Command: {parsed.get('command_type')} - {parsed.get('structured_command')}"
                    )
                
                return parsed
            else:
                return {"error": "Empty response from OpenAI"}
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON response: {str(e)}")
            return {"error": f"Invalid JSON response: {str(e)}", "original": str(result)}
        
    except Exception as e:
        logging.error(f"Error parsing natural language: {str(e)}")
        return {"error": str(e)}

def generate_weekly_summary(calendar_events, tasks, workouts, moods):
    """Generate a weekly summary of activity using AI"""
    try:
        if not client:
            return "Weekly summary not available (missing OpenAI API key)"
            
        # Prepare the data for the AI
        events_text = "\n".join([f"- {event.get('summary')} at {event.get('start', {}).get('dateTime', 'unknown time')}" for event in calendar_events])
        tasks_text = "\n".join([f"- {task.get('title')}" for task in tasks])
        workouts_text = "\n".join([f"- {workout.get('entry')}" for workout in workouts])
        moods_text = "\n".join([f"- {mood.get('entry')}" for mood in moods])
        
        prompt = f"""
        Please analyze this user's week and provide a thoughtful summary:
        
        Calendar Events:
        {events_text or "No events recorded"}
        
        Tasks:
        {tasks_text or "No tasks recorded"}
        
        Workouts:
        {workouts_text or "No workouts recorded"}
        
        Mood Journal:
        {moods_text or "No mood entries recorded"}
        
        Provide a summary that includes:
        1. Activity patterns and balance
        2. Suggestions for the upcoming week
        3. Any notable achievements
        4. A motivational note
        Keep it under 300 words and make it encouraging.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            return f"Error calling OpenAI API: {str(e)}"
        
    except Exception as e:
        logging.error(f"Error generating weekly summary: {str(e)}")
        return f"Error generating weekly summary: {str(e)}"
        
def get_motivation_quote(theme=None):
    """Generate a motivational quote tailored to the user's needs"""
    try:
        if not client:
            return "Motivational quote not available (missing OpenAI API key)"
            
        theme_prompt = f" related to {theme}" if theme else ""
        
        prompt = f"Generate a short, impactful motivational quote{theme_prompt}. Make it original and profound, under 100 characters."
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            return f"Error calling OpenAI API: {str(e)}"
    
    except Exception as e:
        logging.error(f"Error generating motivational quote: {str(e)}")
        return f"Error generating quote: {str(e)}"
        
def handle_conversation(user_id, message, context_data=None):
    """
    Handle a free-form conversation with the AI assistant, with improved context awareness
    and adaptive difficulty levels. Enhanced with self-learning knowledge base.
    
    Args:
        user_id: The unique identifier for the user
        message: The user's message
        context_data: Optional additional context data to include (dict with context types as keys)
        
    Returns:
        str: The AI assistant's response adapted to the user's preferred difficulty level
    """
    try:
        if not client:
            return "Conversation functionality not available (missing API key)"
            
        # Check knowledge base first if enabled
        kb_results = []
        kb_context = ""
        
        if KNOWLEDGE_BASE_ENABLED:
            # Query the knowledge base for similar knowledge
            kb_results = query_knowledge_base(message, user_id=user_id)
            
            # Format knowledge base results as context
            if kb_results:
                kb_context = "\nRELEVANT KNOWLEDGE FROM MEMORY:\n"
                for i, (entry, similarity) in enumerate(kb_results, 1):
                    kb_context += f"{i}. {entry.content}\n"
                kb_context += "\nUse this knowledge when relevant to answer the user's question.\n"
            
        # Use enhanced memory if enabled, otherwise fall back to regular conversation memory
        if ENHANCED_MEMORY_ENABLED:
            # Get the user's memory object
            user_memory = get_user_memory(user_id)
            
            # Add current message to memory
            user_memory.add_message("user", message)
            
            # Get recent conversation history
            recent_messages = user_memory.get_recent_messages(15)  # Last 15 messages
            
            # Get user memory context (including topics, entities, etc.)
            memory_context = user_memory.get_memory_context()
        else:
            # Fall back to old conversation memory system
            conversation_memory.add_message(user_id, "user", message)
            
            # Add any provided context data
            if context_data:
                for context_type, data in context_data.items():
                    conversation_memory.add_context(user_id, context_type, data)
            
            # Get recent conversation history
            recent_messages = conversation_memory.get_recent_messages(user_id)
            
            # Get user context summary
            memory_context = conversation_memory.get_formatted_context(user_id)
            
        # Get the personalized character system prompt
        if CHARACTER_CUSTOMIZATION_ENABLED:
            system_content = get_character_system_prompt()
        else:
            # Fallback to default system prompt
            system_content = """You are NOUS, a helpful, friendly, and intelligent personal assistant. 
            Respond conversationally and helpfully to the user. Keep responses concise but informative.
            You're running within a larger personal assistant application that has specialized functions 
            for many tasks, so focus on being helpful with general knowledge, advice, and friendly conversation.
            
            When responding:
            - Be personable and engaging
            - Remember prior conversations and show continuity
            - Acknowledge the user's emotions and needs
            - Provide helpful and accurate information
            - Keep responses under 150 words unless detailed information is requested
            """
        
        # Add current date/time
        system_content += "\nThe current date and time is: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        
        # Add difficulty-specific instructions
        difficulty_context = get_difficulty_context()
        if difficulty_context:
            system_content += f"\n{difficulty_context}\n"
        
        # Add context information if available
        if memory_context and len(memory_context) > 10:
            system_content += f"\n{memory_context}\n"
            system_content += "\nUse this context information to personalize your responses and show continuity with previous interactions."
            
        # Prepare the messages for the API call with proper typing
        messages: List[ChatCompletionMessageParam] = []
        
        # Add system message
        system_msg: ChatCompletionSystemMessageParam = {
            "role": "system",
            "content": system_content
        }
        messages.append(system_msg)
        
        # Add conversation history
        for msg in recent_messages:
            if msg["role"] == "user":
                user_msg: ChatCompletionUserMessageParam = {
                    "role": "user",
                    "content": msg["content"]
                }
                messages.append(user_msg)
            elif msg["role"] == "assistant":
                assistant_msg: ChatCompletionAssistantMessageParam = {
                    "role": "assistant",
                    "content": msg["content"]
                }
                messages.append(assistant_msg)
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=messages,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            if assistant_message is not None:
                # Save the original response in conversation memory
                conversation_memory.add_message(user_id, "assistant", assistant_message)
                
                # Apply character customization first
                if CHARACTER_CUSTOMIZATION_ENABLED:
                    assistant_message = apply_character_style(assistant_message)
                
                # Then apply adaptive difficulty transformation if needed
                if ADAPTIVE_CONVERSATION_ENABLED:
                    assistant_message = adapt_response(assistant_message)
                
                return assistant_message
            else:
                return "I received an empty response. Let me try to help you differently."
            
        except Exception as e:
            logging.error(f"OpenAI API error in conversation: {str(e)}")
            return f"I'm having trouble responding right now. Technical details: {str(e)}"
            
    except Exception as e:
        logging.error(f"Error in conversation handler: {str(e)}")
        return f"Something went wrong with our conversation. Technical details: {str(e)}"
        
def analyze_gmail_content(user_id, email_content):
    """
    Analyze Gmail content for insights
    
    Args:
        user_id: The unique identifier for the user
        email_content: The email content to analyze
        
    Returns:
        dict: A dictionary containing the analysis results
    """
    try:
        if not client:
            return {"error": "Email analysis not available (missing API key)"}
            
        system_prompt = """
        You are an expert email analyst. Analyze the provided email content and extract the following insights:
        
        1. Key points and main message
        2. Any action items or requests
        3. Priority level (High, Medium, Low)
        4. Tone (Formal, Casual, Urgent, etc.)
        5. Any deadlines or important dates mentioned
        6. People mentioned and their roles
        
        Format your response as JSON with these keys:
        - key_points: list of the most important points
        - action_items: list of things the user needs to do
        - priority: string indicating priority level
        - tone: string describing the email tone
        - deadlines: list of dates and associated events
        - people: list of people mentioned and their context
        - summary: a short (50 words max) plain-text summary
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": email_content}
                ],
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            
            try:
                if result:
                    parsed = json.loads(result)
                    return parsed
                else:
                    return {"error": "Empty response from analysis"}
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing JSON response from email analysis: {str(e)}")
                return {"error": f"Invalid analysis result: {str(e)}", "original": result}
                
        except Exception as e:
            logging.error(f"API error in email analysis: {str(e)}")
            return {"error": f"Error analyzing email: {str(e)}"}
            
    except Exception as e:
        logging.error(f"Error in email analysis handler: {str(e)}")
        return {"error": f"Email analysis failed: {str(e)}"}

def analyze_gmail_threads(user_id, threads, max_threads=5):
    """
    Analyze multiple Gmail threads for insights and summaries
    
    Args:
        user_id: The unique identifier for the user
        threads: List of Gmail thread objects with message content
        max_threads: Maximum number of threads to analyze
        
    Returns:
        list: List of thread summaries with insights
    """
    try:
        if not client:
            return {"error": "Email analysis not available (missing API key)"}
            
        results = []
        threads_to_analyze = threads[:max_threads]  # Limit number of threads to analyze
        
        system_prompt = """
        You are an expert email thread analyzer. For each email thread, provide:
        
        1. A concise subject line summary (max 10 words)
        2. The overall thread importance (High, Medium, Low)
        3. Main participants in the conversation
        4. Key points from the entire thread (max 3)
        5. Required actions from the user, if any
        6. A very brief thread summary (max 30 words)
        
        Format your response as JSON with these keys:
        - subject: string for the thread subject summary
        - importance: string indicating importance level
        - participants: list of main participants
        - key_points: list of the most important points from the thread
        - actions: list of required actions or null if none
        - summary: brief plain-text summary of the thread
        """
        
        for thread in threads_to_analyze:
            try:
                # Prepare thread content for analysis
                thread_content = "\n\n".join([msg.get("content", "") for msg in thread.get("messages", [])])
                thread_subject = thread.get("subject", "No subject")
                
                prompt = f"Subject: {thread_subject}\n\nThread content:\n{thread_content}"
                
                # Prepare messages with proper typing
                messages: List[ChatCompletionMessageParam] = []
                
                # Add system message
                system_msg: ChatCompletionSystemMessageParam = {
                    "role": "system",
                    "content": system_prompt
                }
                messages.append(system_msg)
                
                # Add user message
                user_msg: ChatCompletionUserMessageParam = {
                    "role": "user",
                    "content": prompt
                }
                messages.append(user_msg)
                
                response = client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                    messages=messages,
                    response_format={"type": "json_object"}
                )
                
                result = response.choices[0].message.content
                
                try:
                    if result and result is not None:
                        parsed = json.loads(result)
                        # Add thread ID to the result
                        parsed["thread_id"] = thread.get("id")
                        results.append(parsed)
                    else:
                        results.append({"thread_id": thread.get("id"), "error": "Empty analysis"})
                except json.JSONDecodeError as e:
                    logging.error(f"Error parsing thread analysis JSON: {str(e)}")
                    results.append({"thread_id": thread.get("id"), "error": f"Invalid analysis result: {str(e)}"})
                    
            except Exception as e:
                logging.error(f"Error analyzing thread {thread.get('id')}: {str(e)}")
                results.append({"thread_id": thread.get("id"), "error": f"Analysis failed: {str(e)}"})
                
        return results
                
    except Exception as e:
        logging.error(f"Error in Gmail threads analysis: {str(e)}")
        return {"error": f"Threads analysis failed: {str(e)}"}

# New multimodal functionality

def analyze_image(image_data, prompt=None):
    """
    Analyze an image using OpenAI's vision capabilities
    
    Args:
        image_data: Base64 encoded image data or image URL
        prompt: Optional custom prompt for the analysis
        
    Returns:
        dict: Dictionary containing the analysis results
    """
    try:
        if not client:
            return {"success": False, "error": "Image analysis not available (missing API key)"}
        
        # Determine if the input is a URL or base64 data
        if image_data.startswith('http'):
            image_url = {"url": image_data}
        else:
            # Assume it's base64 data
            image_url = {"url": f"data:image/jpeg;base64,{image_data}"}
        
        # Default analysis prompt if none provided
        if not prompt:
            prompt = "Analyze this image in detail. Describe what you see, including objects, people, activities, context, and any notable elements."
        
        # Prepare messages with proper typing for multimodal content
        from typing import List, Dict, Any, Union
        
        # Create the structure needed for ChatCompletionContentPartTextParam and ChatCompletionContentPartImageParam
        user_content: List[Dict[str, Union[str, Dict[str, str]]]] = [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": image_url
            }
        ]
        
        # Create a properly typed message object
        user_message: ChatCompletionUserMessageParam = {
            "role": "user", 
            "content": user_content # type: ignore
        }
        
        messages = [user_message]
        
        # Call the API
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=messages,
            max_tokens=500
        )
        
        description = response.choices[0].message.content
        
        # Get additional AI analysis for categorization
        if description:
            # Prepare for categorization
            system_prompt = """
            Based on the image description, provide a structured categorization with the following:
            
            1. Main subject(s) of the image (list)
            2. Scene type (indoor, outdoor, urban, nature, etc.)
            3. Dominant colors
            4. Emotional tone/mood
            5. Suggested tags (max 5)
            
            Format your response as JSON with these keys:
            - subjects: list of main subjects
            - scene_type: string describing the scene
            - colors: list of dominant colors
            - mood: emotional tone of the image
            - tags: list of relevant tags
            """
            
            # Prepare messages for categorization
            category_messages: List[ChatCompletionMessageParam] = []
            
            # Add system message
            system_msg: ChatCompletionSystemMessageParam = {
                "role": "system",
                "content": system_prompt
            }
            category_messages.append(system_msg)
            
            # Add user message
            user_msg: ChatCompletionUserMessageParam = {
                "role": "user",
                "content": f"Image description: {description}"
            }
            category_messages.append(user_msg)
            
            category_response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=category_messages,
                response_format={"type": "json_object"}
            )
            
            category_result = category_response.choices[0].message.content
            
            if category_result and category_result is not None:
                try:
                    categories = json.loads(category_result)
                    return {
                        "success": True,
                        "description": description,
                        "categories": categories
                    }
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "description": description,
                        "categories": {"error": "Failed to parse categories"}
                    }
            else:
                return {
                    "success": True,
                    "description": description,
                    "categories": {"error": "Empty category response"}
                }
        else:
            return {"success": False, "error": "Failed to generate image description"}
            
    except Exception as e:
        logging.error(f"Error analyzing image: {str(e)}")
        return {"success": False, "error": f"Image analysis failed: {str(e)}"}
        
def generate_image(prompt: str, style: Optional[str] = None, size: str = "1024x1024"):
    """
    Generate an image using AI based on a prompt
    
    Args:
        prompt: The description of the image to generate
        style: Optional style parameter (e.g., "photorealistic", "cartoon", etc.)
        size: Image size (default: 1024x1024)
        
    Returns:
        dict: Dictionary containing the generation results
    """
    try:
        if not client:
            return {"success": False, "error": "Image generation not available (missing API key)"}
        
        # Enhance the prompt with style information if provided
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt} Style: {style}."
        
        # Validate size parameter using a literal type
        from typing import Literal
        
        # Cast to the valid literal type
        if size == "1024x1024":
            size_param: Literal["1024x1024"] = "1024x1024"
        elif size == "1792x1024":
            size_param: Literal["1792x1024"] = "1792x1024"
        elif size == "1024x1792":
            size_param: Literal["1024x1792"] = "1024x1792"
        elif size == "1536x1024":
            size_param: Literal["1536x1024"] = "1536x1024"
        elif size == "1024x1536":
            size_param: Literal["1024x1536"] = "1024x1536"
        elif size == "512x512":
            size_param: Literal["512x512"] = "512x512"
        elif size == "256x256":
            size_param: Literal["256x256"] = "256x256"
        else:
            # Default to 1024x1024 if not one of the valid sizes
            size_param: Literal["1024x1024"] = "1024x1024"
            
        # Call the DALL-E API
        response = client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            n=1,
            size=size_param
        )
        
        # Extract the image URL
        if response.data and len(response.data) > 0:
            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt if hasattr(response.data[0], 'revised_prompt') else None
            
            return {
                "success": True,
                "url": image_url,
                "original_prompt": prompt,
                "revised_prompt": revised_prompt
            }
        else:
            return {"success": False, "error": "No image generated"}
            
    except Exception as e:
        logging.error(f"Error generating image: {str(e)}")
        return {"success": False, "error": f"Image generation failed: {str(e)}"}