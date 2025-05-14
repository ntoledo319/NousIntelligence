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
        
        If the user is asking about a doctor appointment or mentions a doctor visit, use the appropriate doctor or appointment command format.
        
        Respond with JSON in this exact format:
        {
            "command_type": "calendar|task|note|mood|workout|music|query|reflection|doctor|doctor_list|appointment|appointments_list",
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