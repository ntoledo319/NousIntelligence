"""
Weather helper module for NOUS Assistant
Uses OpenWeatherMap API to fetch weather data
"""

import os
import requests
import json
import datetime
from typing import Dict, List, Optional, Tuple, Any, Union

# API Configuration
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
WEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_API_BASE_URL = "http://api.openweathermap.org/geo/1.0"

def kelvin_to_fahrenheit(kelvin: float) -> float:
    """Convert Kelvin temperature to Fahrenheit"""
    return (kelvin - 273.15) * 9/5 + 32

def kelvin_to_celsius(kelvin: float) -> float:
    """Convert Kelvin temperature to Celsius"""
    return kelvin - 273.15

def get_location_coordinates(location: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Get latitude and longitude for a location name"""
    if not OPENWEATHER_API_KEY:
        raise ValueError("OpenWeatherMap API key not found in environment variables")
    
    url = f"{GEO_API_BASE_URL}/direct?q={location}&limit=1&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    data = response.json()
    
    if not data:
        return None, None, None
    
    # Return lat, lon, and full location name
    return data[0]['lat'], data[0]['lon'], f"{data[0]['name']}, {data[0].get('state', '')}, {data[0]['country']}".replace(", ,", ",")

def get_current_weather(location: str, units: str = "imperial") -> Optional[Dict[str, Any]]:
    """
    Get current weather for a specific location
    
    Parameters:
    - location: City name or location
    - units: 'imperial' for Fahrenheit, 'metric' for Celsius
    
    Returns dictionary with weather data or None if location not found
    """
    if not OPENWEATHER_API_KEY:
        raise ValueError("OpenWeatherMap API key not found in environment variables")
    
    # First get coordinates for the location
    lat, lon, full_location = get_location_coordinates(location)
    
    if lat is None or lon is None:
        return None
    
    # Get weather data using coordinates
    url = f"{WEATHER_API_BASE_URL}/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units={units}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    data = response.json()
    
    # Process and format the data
    weather_data = {
        "location": full_location,
        "coordinates": {"lat": lat, "lon": lon},
        "temperature": {
            "current": round(data['main']['temp']),
            "feels_like": round(data['main']['feels_like']),
            "min": round(data['main']['temp_min']),
            "max": round(data['main']['temp_max'])
        },
        "humidity": data['main']['humidity'],
        "pressure": data['main']['pressure'],
        "wind": {
            "speed": data['wind']['speed'],
            "direction": data['wind'].get('deg', 0)
        },
        "clouds": data['clouds']['all'],
        "weather": {
            "main": data['weather'][0]['main'],
            "description": data['weather'][0]['description'],
            "icon": data['weather'][0]['icon']
        },
        "sunrise": datetime.datetime.fromtimestamp(data['sys']['sunrise']),
        "sunset": datetime.datetime.fromtimestamp(data['sys']['sunset']),
        "timezone": data['timezone'],
        "dt": datetime.datetime.fromtimestamp(data['dt']),
        "units": units
    }
    
    return weather_data

def get_weather_forecast(location: str, days: int = 5, units: str = "imperial") -> Optional[Dict[str, Any]]:
    """
    Get weather forecast for a specific location
    
    Parameters:
    - location: City name or location
    - days: Number of days for forecast (max 5)
    - units: 'imperial' for Fahrenheit, 'metric' for Celsius
    
    Returns dictionary with forecast data or None if location not found
    """
    if not OPENWEATHER_API_KEY:
        raise ValueError("OpenWeatherMap API key not found in environment variables")
    
    # First get coordinates for the location
    lat, lon, full_location = get_location_coordinates(location)
    
    if lat is None or lon is None:
        return None
    
    # Get forecast data using coordinates
    url = f"{WEATHER_API_BASE_URL}/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units={units}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    data = response.json()
    
    # Process and organize forecast data by day
    forecast_data = {
        "location": full_location,
        "coordinates": {"lat": lat, "lon": lon},
        "days": [],
        "units": units
    }
    
    # Group forecast data by day
    forecasts_by_day = {}
    for item in data['list']:
        dt = datetime.datetime.fromtimestamp(item['dt'])
        day_key = dt.strftime('%Y-%m-%d')
        
        if day_key not in forecasts_by_day:
            forecasts_by_day[day_key] = []
            
        forecasts_by_day[day_key].append({
            "dt": dt,
            "temperature": {
                "current": round(item['main']['temp']),
                "feels_like": round(item['main']['feels_like']),
                "min": round(item['main']['temp_min']),
                "max": round(item['main']['temp_max'])
            },
            "humidity": item['main']['humidity'],
            "pressure": item['main']['pressure'],
            "wind": {
                "speed": item['wind']['speed'],
                "direction": item['wind'].get('deg', 0)
            },
            "clouds": item['clouds']['all'],
            "weather": {
                "main": item['weather'][0]['main'],
                "description": item['weather'][0]['description'],
                "icon": item['weather'][0]['icon']
            },
            "pop": item.get('pop', 0) * 100  # Probability of precipitation
        })
    
    # Process daily data (limited to requested number of days)
    for day_key in list(forecasts_by_day.keys())[:days]:
        day_data = forecasts_by_day[day_key]
        
        # Calculate min/max for the day
        temp_min = min(f["temperature"]["min"] for f in day_data)
        temp_max = max(f["temperature"]["max"] for f in day_data)
        
        # Get most common weather condition for the day
        weather_counts = {}
        for f in day_data:
            weather_main = f["weather"]["main"]
            weather_counts[weather_main] = weather_counts.get(weather_main, 0) + 1
        
        main_weather = max(weather_counts.items(), key=lambda x: x[1])[0]
        
        # Find a forecast with this weather to get its description and icon
        weather_details = next(f["weather"] for f in day_data if f["weather"]["main"] == main_weather)
        
        # Calculate average values
        avg_humidity = sum(f["humidity"] for f in day_data) / len(day_data)
        avg_pop = sum(f["pop"] for f in day_data) / len(day_data)
        
        # Add summary to forecast_data
        date_obj = datetime.datetime.strptime(day_key, '%Y-%m-%d')
        forecast_data["days"].append({
            "date": date_obj,
            "day_name": date_obj.strftime("%A"),
            "temperature": {
                "min": round(temp_min),
                "max": round(temp_max),
            },
            "humidity": round(avg_humidity),
            "precipitation_chance": round(avg_pop),
            "weather": {
                "main": main_weather,
                "description": weather_details["description"],
                "icon": weather_details["icon"]
            },
            "hourly": day_data
        })
    
    return forecast_data

def get_weather_alerts(lat: float, lon: float) -> List[Dict[str, Any]]:
    """Get weather alerts for a specific location by coordinates"""
    if not OPENWEATHER_API_KEY:
        raise ValueError("OpenWeatherMap API key not found in environment variables")
    
    url = f"{WEATHER_API_BASE_URL}/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,daily&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    data = response.json()
    
    # Return alerts if present, otherwise empty list
    alerts = []
    if 'alerts' in data:
        for alert in data['alerts']:
            alerts.append({
                "sender": alert.get('sender_name', 'Weather Service'),
                "event": alert.get('event', 'Weather Alert'),
                "start": datetime.datetime.fromtimestamp(alert['start']),
                "end": datetime.datetime.fromtimestamp(alert['end']),
                "description": alert.get('description', '')
            })
    
    return alerts

def get_pollution_data(lat: float, lon: float) -> Dict[str, Any]:
    """Get air pollution data for a specific location by coordinates"""
    if not OPENWEATHER_API_KEY:
        raise ValueError("OpenWeatherMap API key not found in environment variables")
    
    url = f"{WEATHER_API_BASE_URL}/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    data = response.json()
    
    # Process data
    pollution = data['list'][0]
    
    # AQI levels: 1 = Good, 2 = Fair, 3 = Moderate, 4 = Poor, 5 = Very Poor
    aqi_labels = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor"
    }
    
    return {
        "aqi": {
            "index": pollution['main']['aqi'],
            "label": aqi_labels.get(pollution['main']['aqi'], "Unknown")
        },
        "components": {
            "co": pollution['components']['co'],
            "no": pollution['components']['no'],
            "no2": pollution['components']['no2'],
            "o3": pollution['components']['o3'],
            "so2": pollution['components']['so2'],
            "pm2_5": pollution['components']['pm2_5'],
            "pm10": pollution['components']['pm10'],
            "nh3": pollution['components']['nh3']
        },
        "dt": datetime.datetime.fromtimestamp(pollution['dt'])
    }

def format_weather_output(weather_data: Dict[str, Any]) -> str:
    """Format current weather data for display in terminal"""
    if not weather_data:
        return "Location not found. Please try a different location name."
    
    units = weather_data['units']
    temp_unit = "°F" if units == "imperial" else "°C"
    speed_unit = "mph" if units == "imperial" else "m/s"
    
    # Main weather info
    output = [
        f"📍 {weather_data['location']}",
        f"🕒 {weather_data['dt'].strftime('%A, %B %d, %Y at %I:%M %p')}",
        f"",
        f"🌡️ Temperature: {weather_data['temperature']['current']}{temp_unit}",
        f"   Feels like: {weather_data['temperature']['feels_like']}{temp_unit}",
        f"   Min/Max: {weather_data['temperature']['min']}{temp_unit} / {weather_data['temperature']['max']}{temp_unit}",
        f"",
        f"☁️ Conditions: {weather_data['weather']['main']} - {weather_data['weather']['description']}",
        f"💧 Humidity: {weather_data['humidity']}%",
        f"🌬️ Wind: {weather_data['wind']['speed']} {speed_unit}",
        f"",
        f"🌅 Sunrise: {weather_data['sunrise'].strftime('%I:%M %p')}",
        f"🌇 Sunset: {weather_data['sunset'].strftime('%I:%M %p')}"
    ]
    
    return "\n".join(output)

def format_forecast_output(forecast_data: Dict[str, Any]) -> str:
    """Format forecast data for display in terminal"""
    if not forecast_data:
        return "Location not found. Please try a different location name."
    
    units = forecast_data['units']
    temp_unit = "°F" if units == "imperial" else "°C"
    
    output = [f"📍 {forecast_data['location']} - {len(forecast_data['days'])}-Day Forecast", ""]
    
    for day in forecast_data['days']:
        output.append(f"📅 {day['date'].strftime('%A, %B %d')}:")
        output.append(f"   🌡️ {day['temperature']['min']}{temp_unit} to {day['temperature']['max']}{temp_unit}")
        output.append(f"   ☁️ {day['weather']['main']} - {day['weather']['description']}")
        output.append(f"   💧 Humidity: {day['humidity']}%")
        output.append(f"   🌧️ Precipitation chance: {day['precipitation_chance']}%")
        output.append("")
    
    return "\n".join(output)