import os
import logging
import json
from openai import OpenAI

# Initialize OpenAI client if key is present
api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
client = None

if api_key:
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        logging.error(f"Error initializing OpenAI client: {str(e)}")

def parse_natural_language(user_input):
    """
    Use OpenAI to parse natural language input and convert it to a structured command
    
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
        
        If the user is asking about a doctor appointment or mentions a doctor visit, use the appropriate doctor or appointment command format.
        
        If the user seems to be having a conversation or asking a general question that doesn't fit other commands, use the "chat" command type.
        
        If the user wants to analyze an email or get insights from their email, use the "analyze_email" command type.
        
        Respond with JSON in this exact format:
        {
            "command_type": "calendar|task|note|mood|workout|music|query|reflection|doctor|doctor_list|appointment|appointments_list|chat|analyze_email",
            "structured_command": "the exact command in the proper format",
            "confidence": 0.0 to 1.0
        }
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                response_format={"type": "json_object"}
            )
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            return {"error": f"Error calling OpenAI API: {str(e)}"}
        
        result = response.choices[0].message.content
        
        # The response is already JSON formatted
        try:
            if result:
                parsed = json.loads(result)
                return parsed
            else:
                return {"error": "Empty response from OpenAI"}
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON response: {str(e)}")
            return {"error": f"Invalid JSON response: {str(e)}", "original": result}
        
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
        
# User conversation history cache (user_id -> list of message objects)
conversation_history = {}
# Conversation history max length per user
MAX_HISTORY_LENGTH = 10

def handle_conversation(user_id, message):
    """
    Handle a free-form conversation with the AI assistant
    
    Args:
        user_id: The unique identifier for the user
        message: The user's message
        
    Returns:
        str: The AI assistant's response
    """
    try:
        if not client:
            return "Conversation functionality not available (missing API key)"
            
        # Initialize conversation history for this user if it doesn't exist
        if user_id not in conversation_history:
            conversation_history[user_id] = []
            
        # Add this message to the history
        conversation_history[user_id].append({"role": "user", "content": message})
        
        # Limit the conversation history length
        if len(conversation_history[user_id]) > MAX_HISTORY_LENGTH:
            conversation_history[user_id] = conversation_history[user_id][-MAX_HISTORY_LENGTH:]
            
        # Prepare the messages for the API call
        system_message = {
            "role": "system", 
            "content": """You are NOUS, a helpful, friendly, and conversational personal assistant. 
            Respond conversationally and helpfully to the user. Keep responses concise but informative.
            You're running within a larger personal assistant application that has specialized functions 
            for many tasks, so focus on being helpful with general knowledge, advice, and friendly conversation."""
        }
        
        messages = [system_message] + conversation_history[user_id]
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=messages,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add the assistant's response to the conversation history
            conversation_history[user_id].append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
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
                
                response = client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                result = response.choices[0].message.content
                
                try:
                    if result:
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