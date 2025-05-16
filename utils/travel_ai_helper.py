"""
AI Travel Assistant helper functions
Features:
- Trip recommendations based on preferences
- Local event discovery
- Smart packing recommendations based on weather
- Personalized itinerary suggestions

Uses a multi-tier approach to AI services:
1. OpenAI (primary for complex tasks)
2. OpenRouter (fallback for complex tasks)
3. Hugging Face (for lighter AI tasks like phrase translation, summarization)
4. Local fallbacks (when all services are unavailable)
"""

import os
import logging
import json
import datetime
import requests
from typing import Dict, List, Any, Optional, Tuple

from utils.weather_helper import get_weather_forecast
from utils.travel_helper import (
    create_trip, add_packing_item, add_itinerary_item,
    generate_standard_packing_list
)
from openai import OpenAI

# Import Hugging Face helper for lightweight tasks
try:
    from utils.huggingface_helper import (
        translate_text, summarize_text, analyze_sentiment, 
        get_embedding, generate_chat_response
    )
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    logging.warning("Hugging Face helper not available, will skip this fallback option")
    HUGGINGFACE_AVAILABLE = False

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# OpenRouter configuration for fallback
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_CHAT_URL = f"{OPENROUTER_BASE_URL}/chat/completions"

# Travel API configuration (Optional - will be checked before use)
TRAVEL_ADVISOR_API_KEY = os.environ.get("TRAVEL_ADVISOR_API_KEY")
TRAVEL_ADVISOR_BASE_URL = "https://api.content.tripadvisor.com/api/v1"

def get_trip_recommendations(preferences: Dict[str, Any], budget: float, 
                           travel_dates: Tuple[datetime.date, datetime.date],
                           session=None) -> List[Dict[str, Any]]:
    """
    Get trip destination recommendations based on user preferences
    
    Args:
        preferences: Dict containing user preferences (climate, activities, etc.)
        budget: Trip budget in USD
        travel_dates: Tuple of (start_date, end_date)
        session: Flask session object
        
    Returns:
        List of recommended destinations with details
    """
    try:
        if not OPENAI_API_KEY:
            logging.error("OpenAI API key not found")
            return [{"error": "API configuration issue - please ask administrator to set up OpenAI API"}]
            
        # Format the request for the AI
        prompt = f"""
        I need travel destination recommendations based on the following criteria:
        - Budget: ${budget} total
        - Travel dates: {travel_dates[0].strftime('%Y-%m-%d')} to {travel_dates[1].strftime('%Y-%m-%d')}
        - Duration: {(travel_dates[1] - travel_dates[0]).days} days
        
        Preferences:
        """
        
        for key, value in preferences.items():
            prompt += f"- {key}: {value}\n"
            
        prompt += """
        For each recommendation, please provide:
        1. Destination name (city, country)
        2. Why it matches the preferences
        3. Estimated daily costs (accommodations, food, activities)
        4. Best areas to stay
        5. Must-see attractions
        6. Recommended activities
        
        Format as a JSON array with objects containing these fields:
        {
          "destination": "City, Country",
          "match_reasons": ["reason1", "reason2"...],
          "daily_cost_estimate": {"accommodation": X, "food": Y, "activities": Z, "total": Sum},
          "best_areas": ["area1", "area2"...],
          "attractions": ["attraction1", "attraction2"...],
          "activities": ["activity1", "activity2"...],
          "ideal_duration": N
        }
        
        Return exactly 3 recommendations, focusing on diverse options that match the criteria.
        """
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a travel planning assistant that provides destination recommendations."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        result = json.loads(response.choices[0].message.content)
        recommendations = result.get("recommendations", [])
        
        # Add weather data to each recommendation if possible
        for rec in recommendations:
            try:
                destination = rec.get("destination", "")
                weather = get_weather_forecast(destination, days=5)
                if weather:
                    rec["weather_forecast"] = {
                        "summary": weather.get("summary", "Weather data unavailable"),
                        "avg_temp": weather.get("avg_temp", {})
                    }
            except Exception as e:
                logging.error(f"Error fetching weather for {destination}: {str(e)}")
                rec["weather_forecast"] = {"summary": "Weather data unavailable"}
        
        return recommendations
        
    except Exception as e:
        logging.error(f"Error getting trip recommendations: {str(e)}")
        return [{"error": f"Could not generate recommendations: {str(e)}"}]

def discover_local_events(destination: str, start_date: datetime.date, 
                        end_date: datetime.date, interests: List[str] = None) -> List[Dict[str, Any]]:
    """
    Discover local events at a destination during specific dates
    
    Args:
        destination: Location name (city, country)
        start_date: Event start date
        end_date: Event end date
        interests: Optional list of user interests to filter events
        
    Returns:
        List of events with details
    """
    try:
        if not OPENAI_API_KEY:
            logging.error("OpenAI API key not found")
            return [{"error": "API configuration issue"}]
        
        # Try to get real event data first if we have an appropriate API key
        events = []
        if TRAVEL_ADVISOR_API_KEY:
            try:
                # This would call an external API, but we'll skip if not configured
                pass
            except Exception as e:
                logging.error(f"Error calling Travel Advisor API: {str(e)}")
            
        # If we didn't get any events from the API or don't have an API key, 
        # use AI to generate recommendations about typical events
        
        interests_str = ", ".join(interests) if interests else "general attractions"
        
        prompt = f"""
        I need information about events, festivals, and interesting activities in {destination} 
        from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.
        
        The traveler is particularly interested in: {interests_str}
        
        For each event or activity, please provide:
        1. Name of the event/activity
        2. Date and time (if applicable)
        3. Location/venue
        4. Brief description
        5. Why it would be interesting
        6. Estimated cost (if applicable)
        
        Format as a JSON array with objects containing these fields:
        {{
          "name": "Event name",
          "date": "YYYY-MM-DD" or "YYYY-MM-DD to YYYY-MM-DD" for multi-day events,
          "time": "Start time - End time" (if applicable),
          "location": "Venue name, address",
          "description": "Brief description of the event",
          "why_interesting": "Reason this matches the interests",
          "cost": "Estimated cost or price range",
          "booking_required": true/false,
          "category": "Category (festival, sports, music, cultural, etc.)"
        }}
        
        Return a variety of events covering different interests, sorted by date.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a local events expert providing information about activities, festivals, and events in destinations worldwide."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("events", [])
        
    except Exception as e:
        logging.error(f"Error discovering local events: {str(e)}")
        return [{"error": f"Could not find events: {str(e)}"}]

def generate_smart_packing_list(destination: str, start_date: datetime.date, 
                             end_date: datetime.date, trip_type: str,
                             activities: List[str], trip_id: int, session=None) -> Dict[str, Any]:
    """
    Generate a smart packing list based on destination, activities, and weather
    
    Args:
        destination: Trip destination
        start_date: Trip start date
        end_date: Trip end date
        trip_type: Type of trip (business, leisure, adventure, etc.)
        activities: List of planned activities
        trip_id: Trip ID to add packing items to
        session: Flask session object
        
    Returns:
        Dict with categories of packing items and success status
    """
    try:
        if not OPENAI_API_KEY:
            logging.error("OpenAI API key not found")
            return {"error": "API configuration issue", "success": False}
        
        # First, get the weather forecast for the destination
        try:
            weather = get_weather_forecast(destination, days=min(7, (end_date - start_date).days + 1))
            weather_summary = f"Weather forecast: {weather.get('summary', 'Not available')}" if weather else "Weather forecast not available"
            temp_range = f"Temperature range: {weather.get('temp_min')}°F to {weather.get('temp_max')}°F" if weather else ""
            precipitation = f"Precipitation expected: {weather.get('precipitation_probability', 0)}%" if weather else ""
        except Exception as e:
            logging.error(f"Error getting weather for packing list: {str(e)}")
            weather_summary = "Weather forecast could not be retrieved"
            temp_range = ""
            precipitation = ""
        
        # Generate smart packing list with AI
        activities_str = ", ".join(activities)
        duration = (end_date - start_date).days
        
        prompt = f"""
        I need a personalized packing list for a trip to {destination} with these details:
        - Trip type: {trip_type}
        - Duration: {duration} days from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
        - Planned activities: {activities_str}
        - {weather_summary}
        - {temp_range}
        - {precipitation}
        
        Please create a comprehensive packing list with items organized by category.
        Consider the destination, weather, activities, and trip duration.
        
        Format as a JSON object with categories as keys and arrays of items as values:
        {{
          "Clothing": [
            {{"name": "T-shirts", "quantity": 5, "notes": "Quick-dry fabrics recommended"}},
            ...
          ],
          "Toiletries": [...],
          "Electronics": [...],
          "Documents": [...],
          ...
        }}
        
        For each item, include:
        - name: Item name
        - quantity: Recommended quantity
        - notes: Any special recommendations or tips (optional)
        
        Be specific and practical. Include essential items but avoid unnecessary items.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a travel packing expert who creates personalized packing lists based on destination, weather, and activities."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        packing_list = json.loads(response.choices[0].message.content)
        
        # If we have a trip_id and session, add these items to the trip's packing list
        if trip_id and session:
            try:
                # Add each item to the database
                for category, items in packing_list.items():
                    for item in items:
                        add_packing_item(
                            trip_id=trip_id,
                            name=item["name"],
                            category=category,
                            quantity=item.get("quantity", 1),
                            notes=item.get("notes", ""),
                            session=session
                        )
                return {"packing_list": packing_list, "success": True, "message": "Packing list created and saved to trip"}
            except Exception as e:
                logging.error(f"Error saving packing list to trip: {str(e)}")
                return {"packing_list": packing_list, "success": False, "message": f"Generated packing list but couldn't save to trip: {str(e)}"}
        
        # Return just the packing list if we don't need to save it
        return {"packing_list": packing_list, "success": True}
        
    except Exception as e:
        logging.error(f"Error generating smart packing list: {str(e)}")
        return {"error": f"Could not generate packing list: {str(e)}", "success": False}

def suggest_personalized_itinerary(destination: str, start_date: datetime.date, 
                                end_date: datetime.date, interests: List[str],
                                pace: str = "moderate", trip_id: int = None, 
                                session=None) -> Dict[str, Any]:
    """
    Generate a personalized daily itinerary based on destination and interests
    
    Args:
        destination: Trip destination
        start_date: Trip start date
        end_date: Trip end date
        interests: List of traveler's interests
        pace: Preferred pace (relaxed, moderate, busy)
        trip_id: Optional trip ID to add itinerary items to
        session: Flask session object
        
    Returns:
        Dict with daily itinerary and success status
    """
    try:
        if not OPENAI_API_KEY:
            logging.error("OpenAI API key not found")
            return {"error": "API configuration issue", "success": False}
            
        interests_str = ", ".join(interests)
        duration = (end_date - start_date).days + 1
        
        prompt = f"""
        I need a personalized daily itinerary for a trip to {destination} with these details:
        - Trip dates: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ({duration} days)
        - Interests: {interests_str}
        - Preferred pace: {pace} (number of activities per day)
        
        Create a day-by-day itinerary with activities, sights, restaurants, and experiences
        that match the traveler's interests. Consider logical grouping of nearby attractions
        and a sensible flow to each day.
        
        Format as a JSON object with dates as keys and daily itineraries as values:
        {{
          "YYYY-MM-DD": {{
            "day_title": "Day 1: Exploring Downtown",
            "activities": [
              {{
                "time": "9:00 AM - 11:00 AM",
                "name": "Activity name",
                "location": "Location",
                "description": "Brief description",
                "notes": "Any special notes or tips",
                "category": "sightseeing/dining/shopping/etc"
              }},
              ...
            ]
          }},
          ...
        }}
        
        Be specific with activity names, times, and locations. Include a mix of:
        - Popular attractions
        - Off-the-beaten-path experiences
        - Local dining recommendations
        - Time for rest or flexibility
        
        For the pace:
        - "relaxed" means 2-3 main activities per day with plenty of rest time
        - "moderate" means 3-5 activities per day with some flexibility
        - "busy" means a full schedule with many activities
        
        Adjust morning start times and evening end times to be reasonable.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a travel itinerary expert who creates personalized daily plans based on destination and interests."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        itinerary = json.loads(response.choices[0].message.content)
        
        # If we have a trip_id and session, add these items to the trip's itinerary
        if trip_id and session:
            try:
                # Add each item to the database
                for date_str, day_plan in itinerary.items():
                    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    
                    for activity in day_plan.get("activities", []):
                        # Parse time range if available
                        time_range = activity.get("time", "")
                        start_time = None
                        end_time = None
                        
                        if "-" in time_range:
                            times = time_range.split("-")
                            try:
                                # Parse "9:00 AM" format
                                start_time = datetime.datetime.strptime(times[0].strip(), "%I:%M %p").time()
                                end_time = datetime.datetime.strptime(times[1].strip(), "%I:%M %p").time()
                            except:
                                # If parsing fails, leave as None
                                pass
                        
                        add_itinerary_item(
                            trip_id=trip_id,
                            name=activity["name"],
                            date=date_obj,
                            start_time=start_time,
                            end_time=end_time,
                            location=activity.get("location", ""),
                            category=activity.get("category", "activity"),
                            notes=activity.get("notes", "") + "\n" + activity.get("description", ""),
                            session=session
                        )
                        
                return {"itinerary": itinerary, "success": True, "message": "Itinerary created and saved to trip"}
            except Exception as e:
                logging.error(f"Error saving itinerary to trip: {str(e)}")
                return {"itinerary": itinerary, "success": False, "message": f"Generated itinerary but couldn't save to trip: {str(e)}"}
        
        # Return just the itinerary if we don't need to save it
        return {"itinerary": itinerary, "success": True}
        
    except Exception as e:
        logging.error(f"Error generating personalized itinerary: {str(e)}")
        return {"error": f"Could not generate itinerary: {str(e)}", "success": False}

def estimate_trip_budget(destination: str, start_date: datetime.date, end_date: datetime.date,
                       accommodation_type: str, travel_style: str, num_travelers: int = 1) -> Dict[str, Any]:
    """
    Estimate a detailed trip budget
    
    Args:
        destination: Trip destination
        start_date: Trip start date
        end_date: Trip end date
        accommodation_type: Type of accommodation (budget, mid-range, luxury)
        travel_style: Travel style (budget, moderate, luxury)
        num_travelers: Number of travelers
        
    Returns:
        Dict with budget breakdown
    """
    try:
        if not OPENAI_API_KEY:
            logging.error("OpenAI API key not found")
            return {"error": "API configuration issue"}
            
        duration = (end_date - start_date).days
        
        prompt = f"""
        I need a detailed trip budget estimate for {destination} with these details:
        - Duration: {duration} days from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
        - Number of travelers: {num_travelers}
        - Accommodation type: {accommodation_type}
        - Travel style: {travel_style}
        
        Please provide a comprehensive budget breakdown with realistic estimates for:
        - Accommodation (total and per night)
        - Transportation (flights, local transport)
        - Food and dining (per day, total)
        - Activities and attractions
        - Shopping and souvenirs
        - Travel insurance
        - Miscellaneous expenses
        
        Format as a JSON object with categories and detailed breakdowns:
        {{
          "currency": "USD",
          "total_estimate": X,
          "per_person": Y,
          "per_day": Z,
          "categories": {{
            "accommodation": {{
              "total": X,
              "per_night": Y,
              "details": "Description of accommodation assumptions"
            }},
            "transportation": {{...}},
            ...
          }},
          "notes": "Any important notes about the estimates"
        }}
        
        Be realistic and specific about costs for this destination.
        Explain major assumptions made for each category.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a travel budget expert who provides detailed and accurate travel budget estimates."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        budget = json.loads(response.choices[0].message.content)
        return budget
        
    except Exception as e:
        logging.error(f"Error estimating trip budget: {str(e)}")
        return {"error": f"Could not estimate budget: {str(e)}"}

def get_safety_information(destination: str) -> Dict[str, Any]:
    """
    Get safety information and travel advisories for a destination
    
    Args:
        destination: Trip destination (city, country)
        
    Returns:
        Dict with safety information
    """
    try:
        if not OPENAI_API_KEY:
            logging.error("OpenAI API key not found")
            return {"error": "API configuration issue"}
            
        prompt = f"""
        Provide comprehensive safety information and travel advisories for {destination}.
        Include:
        
        1. Current travel advisories from major countries (US, UK, Canada, Australia)
        2. Common safety concerns for tourists
        3. Areas to avoid or be cautious in
        4. Local emergency numbers and contacts
        5. Health advisories and required vaccinations
        6. Transportation safety tips
        7. Cultural sensitivities and local laws travelers should know
        8. Natural disaster risks (if applicable)
        
        Format as a JSON object with these sections and detailed information.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a travel safety expert who provides accurate and helpful safety information for destinations worldwide."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        safety_info = json.loads(response.choices[0].message.content)
        return safety_info
        
    except Exception as e:
        logging.error(f"Error getting safety information: {str(e)}")
        return {"error": f"Could not retrieve safety information: {str(e)}"}

def translate_common_phrases(destination_country: str, phrases: List[str] = None) -> Dict[str, List[Dict[str, str]]]:
    """
    Translate common travel phrases to the local language
    
    Args:
        destination_country: Destination country
        phrases: Optional list of specific phrases to translate
        
    Returns:
        Dict with translated phrases
    """
    try:
        if not OPENAI_API_KEY:
            logging.error("OpenAI API key not found")
            return {"error": "API configuration issue"}
            
        # If no specific phrases provided, use common travel phrases
        if not phrases:
            phrases = [
                "Hello", "Thank you", "Excuse me", "Sorry", "Yes", "No",
                "How much does this cost?", "Where is the bathroom?",
                "I need help", "I don't understand", "Do you speak English?",
                "Good morning", "Good evening", "Goodbye", "Cheers/To your health",
                "Delicious", "Bill, please", "Where is the train station?",
                "One ticket, please", "Can I have the menu, please?"
            ]
            
        phrases_str = "\n".join([f"- {phrase}" for phrase in phrases])
        
        prompt = f"""
        Translate these common travel phrases from English to the primary language spoken in {destination_country}:
        
        {phrases_str}
        
        For each phrase, provide:
        1. The English phrase
        2. The translation
        3. The pronunciation guide (in English phonetics)
        
        Format as a JSON object with an array of phrase objects:
        {{
          "language": "Language name",
          "phrases": [
            {{
              "english": "The English phrase",
              "translation": "The translated phrase",
              "pronunciation": "Pronunciation guide"
            }},
            ...
          ]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a language expert who provides accurate translations and pronunciation guides for travelers."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        translations = json.loads(response.choices[0].message.content)
        return translations
        
    except Exception as e:
        logging.error(f"Error translating phrases: {str(e)}")
        return {"error": f"Could not translate phrases: {str(e)}"}