"""
Weather helper module for NOUS Assistant
Uses OpenWeatherMap API to fetch weather data
Includes pain flare prediction based on barometric pressure changes
"""

import os
import requests
import json
import datetime
import math
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

# Pain Flare Prediction Functions

def get_pressure_trend(location: str, hours: int = 24) -> Dict[str, Any]:
    """
    Get barometric pressure trend over time for a location

    Parameters:
    - location: City name or location
    - hours: Number of hours to analyze (max 5 days, 120 hours)

    Returns dictionary with pressure trend data
    """
    if not OPENWEATHER_API_KEY:
        raise ValueError("OpenWeatherMap API key not found in environment variables")

    # First get coordinates for the location
    lat, lon, full_location = get_location_coordinates(location)

    if lat is None or lon is None:
        return None

    # Get forecast data which contains pressure predictions
    url = f"{WEATHER_API_BASE_URL}/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    data = response.json()

    # Create pressure trend data
    pressure_data = []
    timestamps = []

    # Limit to the requested number of hours
    limit = min(hours, len(data['list']))

    for i in range(limit):
        item = data['list'][i]
        dt = datetime.datetime.fromtimestamp(item['dt'])
        pressure = item['main']['pressure']  # hPa (hectopascals)
        pressure_data.append(pressure)
        timestamps.append(dt)

    # Calculate pressure changes
    pressure_changes = []
    for i in range(1, len(pressure_data)):
        change = pressure_data[i] - pressure_data[i-1]
        pressure_changes.append(change)

    # Calculate overall trend
    if len(pressure_data) > 1:
        overall_change = pressure_data[-1] - pressure_data[0]
    else:
        overall_change = 0

    # Maximum rate of change
    if pressure_changes:
        max_change = max(pressure_changes, key=abs)
    else:
        max_change = 0

    return {
        "location": full_location,
        "pressure_data": [{"timestamp": ts.isoformat(), "pressure": p} for ts, p in zip(timestamps, pressure_data)],
        "overall_change": overall_change,
        "max_change": max_change,
        "current_pressure": pressure_data[0] if pressure_data else None,
        "trend_direction": "rising" if overall_change > 0 else "falling" if overall_change < 0 else "stable"
    }

def calculate_pain_flare_risk(pressure_trend: Dict[str, Any], storm_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Calculate risk of pain flare based on pressure trends and storm data

    Parameters:
    - pressure_trend: Pressure trend data from get_pressure_trend
    - storm_data: Optional storm data

    Returns dictionary with pain flare risk assessment
    """
    if not pressure_trend:
        return {"risk_level": "unknown", "confidence": 0, "message": "No pressure data available"}

    # Initialize risk factors
    risk_score = 0
    confidence = 0.7  # Base confidence level
    factors = []

    # 1. Overall pressure change factor
    overall_change = abs(pressure_trend.get("overall_change", 0))

    # Significant pressure changes often trigger pain (>6 hPa in 24h is significant)
    if overall_change > 10:
        risk_score += 5
        factors.append(f"Very significant pressure change ({overall_change:.1f} hPa)")
        confidence += 0.1
    elif overall_change > 6:
        risk_score += 3
        factors.append(f"Significant pressure change ({overall_change:.1f} hPa)")
    elif overall_change > 3:
        risk_score += 1
        factors.append(f"Moderate pressure change ({overall_change:.1f} hPa)")

    # 2. Rate of change factor (how quickly pressure is changing)
    max_change = abs(pressure_trend.get("max_change", 0))
    if max_change > 3:  # More than 3 hPa in 3 hours is rapid
        risk_score += 3
        factors.append(f"Rapid pressure change rate ({max_change:.1f} hPa)")
        confidence += 0.05
    elif max_change > 1:
        risk_score += 1
        factors.append(f"Moderate pressure change rate ({max_change:.1f} hPa)")

    # 3. Storm presence factor
    if storm_data:
        # Storm conditions increase risk
        if "thunderstorm" in storm_data.get("conditions", "").lower():
            risk_score += 4
            factors.append("Thunderstorm conditions")
            confidence += 0.1
        elif "storm" in storm_data.get("conditions", "").lower():
            risk_score += 3
            factors.append("Storm conditions")
            confidence += 0.05

        # Wind factor
        wind_speed = storm_data.get("wind_speed", 0)
        if wind_speed > 30:
            risk_score += 2
            factors.append(f"High winds ({wind_speed} mph)")

        # Precipitation factor
        precipitation = storm_data.get("precipitation", 0)
        if precipitation > 10:
            risk_score += 1
            factors.append(f"Heavy precipitation ({precipitation} mm)")

    # 4. Current pressure factor (very low or very high pressure)
    current_pressure = pressure_trend.get("current_pressure", 0)
    avg_pressure = 1013.25  # Average sea level pressure (hPa)

    if abs(current_pressure - avg_pressure) > 15:
        risk_score += 1
        factors.append(f"Extreme pressure ({current_pressure} hPa)")

    # Calculate risk level based on score
    risk_level = "low"
    if risk_score >= 8:
        risk_level = "very high"
    elif risk_score >= 5:
        risk_level = "high"
    elif risk_score >= 3:
        risk_level = "moderate"

    # Cap confidence at 0.95
    confidence = min(0.95, confidence)

    # Create recommendation based on risk
    if risk_level == "very high":
        recommendation = "Consider taking preventive pain medication and limiting physical activity. Stay hydrated and keep warm."
    elif risk_level == "high":
        recommendation = "Be prepared for potential pain flare. Have medication ready and consider reducing strenuous activities."
    elif risk_level == "moderate":
        recommendation = "Monitor your symptoms. Consider gentle exercise and stay hydrated."
    else:
        recommendation = "Low risk of weather-related pain flare. Maintain normal activities."

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "confidence": confidence,
        "factors": factors,
        "trend_direction": pressure_trend.get("trend_direction"),
        "recommendation": recommendation
    }

def get_storm_severity(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract storm severity data from weather data"""
    if not weather_data:
        return None

    # Get relevant storm indicators
    conditions = weather_data["weather"]["main"]
    description = weather_data["weather"]["description"]

    wind_speed = weather_data["wind"]["speed"]
    wind_direction = weather_data.get("wind", {}).get("direction", 0)

    # Get precipitation if available (not always present in API response)
    precipitation = 0
    if "rain" in weather_data and "1h" in weather_data["rain"]:
        precipitation = weather_data["rain"]["1h"]
    elif "rain" in weather_data and "3h" in weather_data["rain"]:
        precipitation = weather_data["rain"]["3h"] / 3

    # Calculate storm severity score (0-10)
    severity = 0

    # Weather conditions factor
    if "thunderstorm" in conditions.lower() or "thunderstorm" in description.lower():
        severity += 5
    elif "storm" in conditions.lower() or "storm" in description.lower():
        severity += 3
    elif "rain" in conditions.lower() or "rain" in description.lower():
        severity += 2
    elif "drizzle" in conditions.lower() or "drizzle" in description.lower():
        severity += 1

    # Wind factor (wind over 25mph is significant)
    if wind_speed > 40:
        severity += 3
    elif wind_speed > 25:
        severity += 2
    elif wind_speed > 15:
        severity += 1

    # Precipitation factor
    if precipitation > 10:  # Heavy rain
        severity += 2
    elif precipitation > 5:  # Moderate rain
        severity += 1

    # Cap at 10
    severity = min(10, severity)

    # Determine severity category
    if severity >= 8:
        category = "severe"
    elif severity >= 5:
        category = "moderate"
    elif severity >= 2:
        category = "mild"
    else:
        category = "none"

    return {
        "conditions": f"{conditions} - {description}",
        "wind_speed": wind_speed,
        "wind_direction": wind_direction,
        "precipitation": precipitation,
        "severity_score": severity,
        "category": category
    }

def format_pain_forecast_output(pressure_trend: Dict[str, Any], pain_risk: Dict[str, Any]) -> str:
    """Format pain flare risk assessment for display in terminal"""
    if not pressure_trend or not pain_risk:
        return "Unable to generate pain flare forecast. Try again with a different location."

    risk_level = pain_risk["risk_level"].upper()

    # Choose emoji based on risk level
    risk_emoji = "🟢"  # Low risk
    if risk_level == "MODERATE":
        risk_emoji = "🟡"
    elif risk_level == "HIGH":
        risk_emoji = "🟠"
    elif risk_level == "VERY HIGH":
        risk_emoji = "🔴"

    # Format output
    output = [
        f"📍 {pressure_trend['location']} - Pain Flare Forecast",
        f"",
        f"{risk_emoji} Risk Level: {risk_level} (Confidence: {pain_risk['confidence']*100:.0f}%)",
        f"🌡️ Barometric Pressure: {pressure_trend['current_pressure']} hPa ({pressure_trend['trend_direction']})",
        f"📊 Pressure Change: {pressure_trend['overall_change']:.1f} hPa over {len(pressure_trend['pressure_data'])} hours",
        f"",
        f"🔍 Risk Factors:"
    ]

    # Add factors
    for factor in pain_risk["factors"]:
        output.append(f"  • {factor}")

    if not pain_risk["factors"]:
        output.append("  • No significant risk factors")

    # Add recommendation
    output.extend([
        f"",
        f"💡 Recommendation:",
        f"  {pain_risk['recommendation']}"
    ])

    return "\n".join(output)
