"""
Enhanced weather helper module with advanced weather features:
- Weather alerts and notifications
- Weather-based health insights
- Trip planning weather integration
- Personalized activity recommendations
"""

import os
import logging
import json
import datetime
import requests
from typing import Dict, List, Any, Optional, Tuple, Union

from utils.weather_helper import (
    get_current_weather, get_weather_forecast, get_location_coordinates,
    kelvin_to_fahrenheit, kelvin_to_celsius
)
from models import db, Trip, WeatherLocation
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# API Configuration
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
WEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5"
ONE_CALL_API_URL = "https://api.openweathermap.org/data/3.0/onecall"

def get_extended_forecast(location: str, days: int = 7, include_hourly: bool = False) -> Dict[str, Any]:
    """
    Get detailed weather forecast with additional data

    Args:
        location: Location name
        days: Number of days to forecast (max 7)
        include_hourly: Whether to include hourly forecast data

    Returns:
        Dict with detailed forecast data
    """
    try:
        if not OPENWEATHER_API_KEY:
            logging.error("OpenWeatherMap API key not found")
            return {"error": "API configuration issue"}

        # Get location coordinates
        lat, lon, location_name = get_location_coordinates(location)
        if not lat or not lon:
            return {"error": f"Could not find coordinates for {location}"}

        # Call OneCall API for more detailed weather data
        params = {
            "lat": lat,
            "lon": lon,
            "exclude": "minutely",
            "appid": OPENWEATHER_API_KEY,
            "units": "imperial"
        }

        # Remove hourly data if not needed to reduce response size
        if not include_hourly:
            params["exclude"] += ",hourly"

        response = requests.get(ONE_CALL_API_URL, params=params)

        if response.status_code != 200:
            return {"error": f"API error: {response.status_code} - {response.text}"}

        data = response.json()

        # Process and format the data
        current = data.get("current", {})
        daily = data.get("daily", [])[:days]  # Limit to requested days

        # Format current conditions
        current_weather = {
            "temp": current.get("temp"),
            "feels_like": current.get("feels_like"),
            "humidity": current.get("humidity"),
            "wind_speed": current.get("wind_speed"),
            "wind_direction": current.get("wind_deg"),
            "uv_index": current.get("uvi"),
            "conditions": current.get("weather", [{}])[0].get("main"),
            "description": current.get("weather", [{}])[0].get("description"),
            "icon": current.get("weather", [{}])[0].get("icon"),
            "pressure": current.get("pressure"),
        }

        # Format daily forecast
        daily_forecast = []
        for day in daily:
            day_date = datetime.datetime.fromtimestamp(day.get("dt")).strftime("%Y-%m-%d")
            daily_forecast.append({
                "date": day_date,
                "temp_max": day.get("temp", {}).get("max"),
                "temp_min": day.get("temp", {}).get("min"),
                "humidity": day.get("humidity"),
                "wind_speed": day.get("wind_speed"),
                "conditions": day.get("weather", [{}])[0].get("main"),
                "description": day.get("weather", [{}])[0].get("description"),
                "icon": day.get("weather", [{}])[0].get("icon"),
                "precipitation_probability": round(day.get("pop", 0) * 100),
                "rain": day.get("rain", 0),
                "uv_index": day.get("uvi"),
                "sunrise": datetime.datetime.fromtimestamp(day.get("sunrise")).strftime("%H:%M"),
                "sunset": datetime.datetime.fromtimestamp(day.get("sunset")).strftime("%H:%M"),
            })

        # Format hourly forecast if requested
        hourly_forecast = []
        if include_hourly and "hourly" in data:
            for hour in data.get("hourly", [])[:48]:  # Limit to 48 hours
                hour_time = datetime.datetime.fromtimestamp(hour.get("dt")).strftime("%Y-%m-%d %H:%M")
                hourly_forecast.append({
                    "time": hour_time,
                    "temp": hour.get("temp"),
                    "feels_like": hour.get("feels_like"),
                    "humidity": hour.get("humidity"),
                    "wind_speed": hour.get("wind_speed"),
                    "conditions": hour.get("weather", [{}])[0].get("main"),
                    "description": hour.get("weather", [{}])[0].get("description"),
                    "icon": hour.get("weather", [{}])[0].get("icon"),
                    "precipitation_probability": round(hour.get("pop", 0) * 100),
                })

        # Get weather alerts if available
        alerts = []
        if "alerts" in data:
            for alert in data.get("alerts", []):
                alert_start = datetime.datetime.fromtimestamp(alert.get("start")).strftime("%Y-%m-%d %H:%M")
                alert_end = datetime.datetime.fromtimestamp(alert.get("end")).strftime("%Y-%m-%d %H:%M")
                alerts.append({
                    "event": alert.get("event"),
                    "description": alert.get("description"),
                    "start": alert_start,
                    "end": alert_end,
                    "sender": alert.get("sender_name")
                })

        # Compile the result
        result = {
            "location": location_name,
            "current": current_weather,
            "daily": daily_forecast,
            "alerts": alerts
        }

        if include_hourly:
            result["hourly"] = hourly_forecast

        return result

    except Exception as e:
        logging.error(f"Error getting extended forecast: {str(e)}")
        return {"error": f"Could not get extended forecast: {str(e)}"}

def get_personalized_activity_recommendations(location: str, date: datetime.date = None,
                                           interests: List[str] = None, indoor_only: bool = False) -> Dict[str, Any]:
    """
    Get weather-based activity recommendations

    Args:
        location: Location name
        date: Optional specific date (defaults to current date)
        interests: List of activity interests
        indoor_only: Whether to only include indoor activities

    Returns:
        Dict with recommended activities
    """
    try:
        if not OPENAI_API_KEY:
            logging.error("OpenAI API key not found")
            return {"error": "API configuration issue"}

        # Get weather forecast for the location and date
        try:
            # If no date provided, use current date
            if not date:
                date = datetime.date.today()

            # Get detailed forecast
            forecast = get_extended_forecast(location)
            if "error" in forecast:
                return {"error": f"Could not get weather forecast: {forecast['error']}"}

            # Get the specific day's forecast
            target_date_str = date.strftime("%Y-%m-%d")
            day_forecast = None
            for day in forecast.get("daily", []):
                if day.get("date") == target_date_str:
                    day_forecast = day
                    break

            if not day_forecast:
                day_forecast = forecast.get("daily", [])[0] if forecast.get("daily") else None

            # Current conditions
            current_weather = forecast.get("current", {})

            # Weather alerts
            alerts = forecast.get("alerts", [])

        except Exception as e:
            logging.error(f"Error getting weather for activity recommendations: {str(e)}")
            return {"error": f"Could not get weather data: {str(e)}"}

        # Format interests
        interests_str = ", ".join(interests) if interests else "general activities"

        # Prepare weather description for the AI
        if day_forecast:
            weather_desc = f"""
            Weather forecast for {location} on {target_date_str}:
            - Conditions: {day_forecast.get('description', 'Not available')}
            - Temperature: {day_forecast.get('temp_min')}°F to {day_forecast.get('temp_max')}°F
            - Precipitation probability: {day_forecast.get('precipitation_probability')}%
            - Wind speed: {day_forecast.get('wind_speed')} mph
            - UV Index: {day_forecast.get('uv_index')}
            - Sunrise: {day_forecast.get('sunrise')}, Sunset: {day_forecast.get('sunset')}
            """
        else:
            weather_desc = f"Weather forecast for {location} unavailable."

        if alerts:
            weather_desc += "\nWeather alerts: " + ", ".join([alert.get("event") for alert in alerts])

        # Only indoor flag
        indoor_flag = "Please suggest indoor activities only due to weather conditions." if indoor_only else ""

        prompt = f"""
        I need activity recommendations for {location} on {target_date_str} based on the weather forecast and interests.

        {weather_desc}

        The person is interested in: {interests_str}

        {indoor_flag}

        Please provide activity recommendations suitable for the weather conditions and specified interests.
        Include:
        1. Name and brief description of each activity
        2. Why it's suitable for the weather conditions
        3. Whether it's indoor or outdoor
        4. Suggested time of day
        5. Estimated duration

        Format as a JSON object with categories of activities:
        {{
          "recommended_activities": [
            {{
              "name": "Activity name",
              "description": "Brief description",
              "weather_suitability": "Why this works with the forecast",
              "indoor": true/false,
              "best_time": "Morning/Afternoon/Evening",
              "duration": "Estimated duration",
              "category": "Category (cultural, adventure, relaxation, etc.)"
            }},
            ...
          ],
          "weather_summary": "Brief summary of the weather and its impact on activities",
          "special_recommendations": "Any special recommendations based on alerts or conditions"
        }}

        Provide a diverse set of activities, with a mix of popular and lesser-known options.
        """

        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a local activities expert who provides weather-appropriate activity recommendations that match the user's interests."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        # Parse the response
        recommendations = json.loads(response.choices[0].message.content)

        # Add original weather data
        if day_forecast:
            recommendations["weather_data"] = day_forecast

        return recommendations

    except Exception as e:
        logging.error(f"Error getting activity recommendations: {str(e)}")
        return {"error": f"Could not get activity recommendations: {str(e)}"}

def get_weather_alerts_for_location(location: str) -> Dict[str, Any]:
    """
    Get weather alerts for a location

    Args:
        location: Location name

    Returns:
        Dict with weather alerts
    """
    try:
        # Get detailed forecast with alerts
        forecast = get_extended_forecast(location)
        if "error" in forecast:
            return {"error": forecast["error"]}

        # Extract and format alerts
        alerts = forecast.get("alerts", [])

        # Format for response
        return {
            "location": forecast.get("location", location),
            "alert_count": len(alerts),
            "alerts": alerts,
            "has_alerts": len(alerts) > 0
        }

    except Exception as e:
        logging.error(f"Error getting weather alerts: {str(e)}")
        return {"error": f"Could not get weather alerts: {str(e)}"}

def get_weather_health_insights(location: str, health_conditions: List[str] = None,
                             user_id: str = None, session=None,
                             include_pain_flare_risk: bool = False) -> Dict[str, Any]:
    """
    Get weather-based health insights

    Args:
        location: Location name
        health_conditions: List of health conditions to consider
        user_id: User ID for storing preferences
        session: Flask session object
        include_pain_flare_risk: Whether to include pain flare risk assessment

    Returns:
        Dict with health insights
    """
    try:
        if not OPENAI_API_KEY:
            logging.error("OpenAI API key not found")
            return {"error": "API configuration issue"}

        # Get detailed weather forecast
        forecast = get_extended_forecast(location, include_hourly=True)
        if "error" in forecast:
            return {"error": forecast["error"]}

        # Extract current and forecast data
        current = forecast.get("current", {})
        daily = forecast.get("daily", [])
        hourly = forecast.get("hourly", [])

        # Format health conditions
        conditions_str = ", ".join(health_conditions) if health_conditions else "general health"

        # Check if pain flare risk is requested
        pain_flare_data = None
        if include_pain_flare_risk:
            try:
                from utils.weather_helper import (
                    get_pressure_trend, calculate_pain_flare_risk, get_storm_severity
                )

                pressure_trend = get_pressure_trend(location, 24)
                storm_data = get_storm_severity(current)
                pain_risk = calculate_pain_flare_risk(pressure_trend, storm_data)

                pain_flare_data = {
                    "risk_level": pain_risk['risk_level'],
                    "risk_score": pain_risk['risk_score'],
                    "confidence": pain_risk['confidence'],
                    "factors": pain_risk['factors'],
                    "recommendation": pain_risk['recommendation']
                }
            except Exception as e:
                logging.error(f"Error calculating pain flare risk: {str(e)}")
                pain_flare_data = {"error": f"Could not calculate pain flare risk: {str(e)}"}

        # Extract relevant weather data for health assessment
        weather_data = {
            "current_temp": current.get("temp"),
            "current_humidity": current.get("humidity"),
            "current_pressure": current.get("pressure"),
            "current_uv": current.get("uv_index"),
            "current_conditions": current.get("description"),
            "forecast_high": daily[0].get("temp_max") if daily else None,
            "forecast_low": daily[0].get("temp_min") if daily else None,
            "pressure_changes": [hour.get("pressure") for hour in hourly[:24]] if hourly else [],
            "humidity_changes": [hour.get("humidity") for hour in hourly[:24]] if hourly else [],
            "alerts": [alert.get("event") for alert in forecast.get("alerts", [])]
        }

        # Prepare weather description for the AI
        weather_desc = f"""
        Current weather in {forecast.get('location', location)}:
        - Temperature: {current.get('temp')}°F, feels like {current.get('feels_like')}°F
        - Humidity: {current.get('humidity')}%
        - Barometric pressure: {current.get('pressure')} hPa
        - UV Index: {current.get('uv_index')}
        - Conditions: {current.get('description')}

        Forecast:
        - Today's high: {daily[0].get('temp_max')}°F, low: {daily[0].get('temp_min')}°F
        - Precipitation probability: {daily[0].get('precipitation_probability')}%

        Alerts: {', '.join([alert.get('event') for alert in forecast.get('alerts', [])]) if forecast.get('alerts') else 'None'}
        """

        prompt = f"""
        I need health insights based on the weather conditions and specific health considerations.

        {weather_desc}

        Health conditions to consider: {conditions_str}

        Please provide health insights related to:
        1. How these weather conditions might affect the specified health conditions
        2. Recommendations for managing health in these conditions
        3. Any warnings or precautions related to the weather
        4. Comfort level assessment

        Format as a JSON object with these sections:
        {{
          "weather_impacts": [
            {{
              "condition": "Health condition",
              "impact": "How the weather might affect this condition",
              "severity": "low/moderate/high",
              "recommendations": ["Recommendation 1", "Recommendation 2", ...]
            }},
            ...
          ],
          "general_recommendations": ["General recommendation 1", "General recommendation 2", ...],
          "warnings": ["Warning 1", "Warning 2", ...],
          "comfort_assessment": {{
            "overall_comfort": "rating from 1-10",
            "factors": ["Factor 1", "Factor 2", ...],
            "summary": "Brief comfort summary"
          }}
        }}

        Be specific about how different weather factors (temperature, humidity, pressure, etc.)
        might affect the specified conditions, and provide practical recommendations.
        """

        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a health expert who provides evidence-based insights about how weather conditions can affect health."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        # Parse the response
        insights = json.loads(response.choices[0].message.content)

        # Add pain flare data if requested
        if pain_flare_data:
            insights["pain_flare_risk"] = pain_flare_data

        # Add original weather data
        insights["weather_data"] = weather_data

        return insights

    except Exception as e:
        logging.error(f"Error getting weather health insights: {str(e)}")
        return {"error": f"Could not get health insights: {str(e)}"}

def get_trip_weather_overview(trip_id: int, session=None) -> Dict[str, Any]:
    """
    Get comprehensive weather overview for a trip

    Args:
        trip_id: Trip ID
        session: Flask session object

    Returns:
        Dict with trip weather overview
    """
    try:
        from utils.travel_helper import get_trip_by_id

        # Get trip details
        trip = get_trip_by_id(trip_id, session)
        if not trip:
            return {"error": "Trip not found"}

        destination = trip.destination
        start_date = trip.start_date
        end_date = trip.end_date

        if not start_date or not end_date:
            return {"error": "Trip dates not set"}

        # Calculate trip duration in days
        duration = (end_date.date() - start_date.date()).days + 1

        # Get extended weather forecast
        forecast = get_extended_forecast(destination, days=min(7, duration))
        if "error" in forecast:
            return {"error": forecast["error"]}

        # Extract daily forecasts
        daily_forecasts = forecast.get("daily", [])

        # Generate weather summary and recommendations
        if OPENAI_API_KEY:
            try:
                # Format forecast data for the AI
                forecast_text = f"Weather forecast for {destination}:\n"
                for day in daily_forecasts:
                    forecast_text += f"- {day.get('date')}: {day.get('description')}, " \
                                   f"{day.get('temp_min')}°F to {day.get('temp_max')}°F, " \
                                   f"Precipitation: {day.get('precipitation_probability')}%, " \
                                   f"UV Index: {day.get('uv_index')}\n"

                prompt = f"""
                I need a weather overview and recommendations for a trip to {destination}
                from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.

                {forecast_text}

                Please provide:
                1. A summary of the overall weather for the trip
                2. Day-by-day activity recommendations based on the forecast
                3. Packing suggestions based on the forecast
                4. Weather-related concerns or alerts to be aware of

                Format as a JSON object with these sections.
                """

                response = client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                    messages=[
                        {"role": "system", "content": "You are a travel weather expert who provides helpful weather insights and recommendations for trips."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )

                # Parse the response
                ai_insights = json.loads(response.choices[0].message.content)

                # Combine AI insights with raw forecast data
                result = {
                    "trip": {
                        "id": trip.id,
                        "name": trip.name,
                        "destination": destination,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "duration": duration,
                    },
                    "weather_data": {
                        "location": forecast.get("location", destination),
                        "current": forecast.get("current", {}),
                        "daily": daily_forecasts,
                        "alerts": forecast.get("alerts", []),
                    },
                    "insights": ai_insights
                }

                return result

            except Exception as e:
                logging.error(f"Error generating weather insights: {str(e)}")
                # Continue with basic forecast if AI insights fail

        # Basic format without AI insights
        return {
            "trip": {
                "id": trip.id,
                "name": trip.name,
                "destination": destination,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "duration": duration,
            },
            "weather_data": {
                "location": forecast.get("location", destination),
                "current": forecast.get("current", {}),
                "daily": daily_forecasts,
                "alerts": forecast.get("alerts", []),
            }
        }

    except Exception as e:
        logging.error(f"Error getting trip weather overview: {str(e)}")
        return {"error": f"Could not get trip weather overview: {str(e)}"}

def set_user_weather_preferences(user_id: str, preferences: Dict[str, Any], session=None) -> Dict[str, Any]:
    """
    Set user weather preferences (only stored, not used for pain flare prediction unless specifically requested)

    Args:
        user_id: User ID
        preferences: Dict with weather preferences
        session: Flask session object

    Returns:
        Dict with result status
    """
    try:
        # Ensure required fields
        if not user_id or not preferences:
            return {"success": False, "error": "Missing required parameters"}

        # Extract preferences
        primary_location = preferences.get("primary_location")
        units = preferences.get("units", "imperial")  # Default to imperial

        # Set primary location if provided
        if primary_location:
            try:
                # Check if this location already exists
                existing = WeatherLocation.query.filter_by(
                    user_id=user_id,
                    name=primary_location
                ).first()

                if existing:
                    # Update existing location as primary
                    WeatherLocation.query.filter_by(user_id=user_id).update({"is_primary": False})
                    existing.is_primary = True
                    db.session.commit()
                else:
                    # Create new location entry
                    lat, lon, formatted_location = get_location_coordinates(primary_location)
                    if lat and lon:
                        # Unset other primary locations first
                        WeatherLocation.query.filter_by(user_id=user_id).update({"is_primary": False})

                        # Create new primary location
                        new_location = WeatherLocation(
                            user_id=user_id,
                            name=formatted_location or primary_location,
                            latitude=lat,
                            longitude=lon,
                            is_primary=True,
                            created_at=datetime.datetime.utcnow()
                        )
                        db.session.add(new_location)
                        db.session.commit()
                    else:
                        return {"success": False, "error": f"Could not find coordinates for {primary_location}"}
            except Exception as e:
                logging.error(f"Error setting primary location: {str(e)}")
                return {"success": False, "error": f"Error setting primary location: {str(e)}"}

        # Store other preferences in session if provided
        if session:
            session["weather_preferences"] = {
                "units": units,
                "show_pain_flares": preferences.get("show_pain_flares", False),
                "health_conditions": preferences.get("health_conditions", []),
                "activity_interests": preferences.get("activity_interests", [])
            }

        return {"success": True, "message": "Weather preferences updated successfully"}

    except Exception as e:
        logging.error(f"Error setting weather preferences: {str(e)}")
        return {"success": False, "error": f"Could not set weather preferences: {str(e)}"}

def enable_pain_flare_monitoring(user_id: str, enable: bool = True, session=None) -> Dict[str, bool]:
    """
    Specifically enable or disable pain flare monitoring

    Args:
        user_id: User ID
        enable: Whether to enable pain flare monitoring
        session: Flask session object

    Returns:
        Dict with result status
    """
    try:
        if session:
            # Get current preferences or initialize
            prefs = session.get("weather_preferences", {})
            prefs["show_pain_flares"] = enable
            session["weather_preferences"] = prefs

        return {"success": True, "pain_flares_enabled": enable}
    except Exception as e:
        logging.error(f"Error setting pain flare monitoring: {str(e)}")
        return {"success": False, "error": f"Could not update setting: {str(e)}"}