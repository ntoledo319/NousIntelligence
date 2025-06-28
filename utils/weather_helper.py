"""
Weather Helper - Comprehensive Weather Services Integration
Weather data, forecasts, alerts, and activity recommendations
"""

import logging
import json
import requests
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import os

logger = logging.getLogger(__name__)


class WeatherAPI:
    """Base weather API interface"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('WEATHER_API_KEY')
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather for location"""
        raise NotImplementedError
    
    def get_forecast(self, location: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast"""
        raise NotImplementedError
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]['timestamp']
        return (datetime.now() - cached_time).seconds < self.cache_duration
    
    def _cache_data(self, cache_key: str, data: Dict[str, Any]):
        """Cache weather data"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached weather data"""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        return None


class OpenWeatherMapAPI(WeatherAPI):
    """OpenWeatherMap API implementation"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather from OpenWeatherMap"""
        try:
            cache_key = f"current_{location}"
            
            # Check cache first
            cached_data = self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            if not self.api_key:
                return self._get_fallback_weather(location)
            
            # Get coordinates for location
            coords = self._geocode_location(location)
            if not coords:
                return {'error': 'Location not found'}
            
            lat, lon = coords
            
            # Make API request
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    'success': True,
                    'location': location,
                    'coordinates': {'lat': lat, 'lon': lon},
                    'current': {
                        'temperature': data['main']['temp'],
                        'feels_like': data['main']['feels_like'],
                        'humidity': data['main']['humidity'],
                        'pressure': data['main']['pressure'],
                        'description': data['weather'][0]['description'],
                        'icon': data['weather'][0]['icon'],
                        'wind_speed': data.get('wind', {}).get('speed', 0),
                        'wind_direction': data.get('wind', {}).get('deg', 0),
                        'visibility': data.get('visibility', 0),
                        'uv_index': 0  # Not available in current weather endpoint
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source': 'openweathermap'
                }
                
                # Cache the result
                self._cache_data(cache_key, result)
                return result
            else:
                logger.error(f"Weather API error: {response.status_code}")
                return self._get_fallback_weather(location)
        
        except Exception as e:
            logger.error(f"Error getting current weather: {str(e)}")
            return self._get_fallback_weather(location)
    
    def get_forecast(self, location: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast from OpenWeatherMap"""
        try:
            cache_key = f"forecast_{location}_{days}"
            
            # Check cache first
            cached_data = self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            if not self.api_key:
                return self._get_fallback_forecast(location, days)
            
            # Get coordinates for location
            coords = self._geocode_location(location)
            if not coords:
                return {'error': 'Location not found'}
            
            lat, lon = coords
            
            # Make API request
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process forecast data
                daily_forecasts = []
                current_date = None
                daily_data = {}
                
                for item in data['list']:
                    dt = datetime.fromtimestamp(item['dt'], timezone.utc)
                    date_str = dt.strftime('%Y-%m-%d')
                    
                    if date_str != current_date:
                        if current_date and daily_data:
                            daily_forecasts.append(daily_data)
                        
                        current_date = date_str
                        daily_data = {
                            'date': date_str,
                            'day_name': dt.strftime('%A'),
                            'temperature': {
                                'min': item['main']['temp'],
                                'max': item['main']['temp']
                            },
                            'description': item['weather'][0]['description'],
                            'icon': item['weather'][0]['icon'],
                            'humidity': item['main']['humidity'],
                            'wind_speed': item.get('wind', {}).get('speed', 0),
                            'precipitation': item.get('rain', {}).get('3h', 0)
                        }
                    else:
                        # Update min/max temperatures
                        daily_data['temperature']['min'] = min(
                            daily_data['temperature']['min'],
                            item['main']['temp']
                        )
                        daily_data['temperature']['max'] = max(
                            daily_data['temperature']['max'],
                            item['main']['temp']
                        )
                
                # Add last day if exists
                if daily_data:
                    daily_forecasts.append(daily_data)
                
                result = {
                    'success': True,
                    'location': location,
                    'coordinates': {'lat': lat, 'lon': lon},
                    'forecast': daily_forecasts[:days],
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'source': 'openweathermap'
                }
                
                # Cache the result
                self._cache_data(cache_key, result)
                return result
            else:
                logger.error(f"Forecast API error: {response.status_code}")
                return self._get_fallback_forecast(location, days)
        
        except Exception as e:
            logger.error(f"Error getting forecast: {str(e)}")
            return self._get_fallback_forecast(location, days)
    
    def _geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """Convert location name to coordinates"""
        try:
            if not self.api_key:
                # Return default coordinates for major cities
                city_coords = {
                    'new york': (40.7128, -74.0060),
                    'london': (51.5074, -0.1278),
                    'tokyo': (35.6762, 139.6503),
                    'paris': (48.8566, 2.3522),
                    'sydney': (-33.8688, 151.2093)
                }
                return city_coords.get(location.lower())
            
            url = "http://api.openweathermap.org/geo/1.0/direct"
            params = {
                'q': location,
                'limit': 1,
                'appid': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return (data[0]['lat'], data[0]['lon'])
            
            return None
        
        except Exception as e:
            logger.error(f"Geocoding error: {str(e)}")
            return None
    
    def _get_fallback_weather(self, location: str) -> Dict[str, Any]:
        """Get fallback weather data when API is unavailable"""
        return {
            'success': True,
            'location': location,
            'current': {
                'temperature': 22.0,
                'feels_like': 24.0,
                'humidity': 65,
                'pressure': 1013,
                'description': 'partly cloudy',
                'icon': '02d',
                'wind_speed': 5.2,
                'wind_direction': 180,
                'visibility': 10000,
                'uv_index': 6
            },
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'fallback',
            'note': 'Using sample data - API key required for real weather data'
        }
    
    def _get_fallback_forecast(self, location: str, days: int) -> Dict[str, Any]:
        """Get fallback forecast data"""
        forecasts = []
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            forecasts.append({
                'date': date.strftime('%Y-%m-%d'),
                'day_name': date.strftime('%A'),
                'temperature': {
                    'min': 18 + (i % 5),
                    'max': 25 + (i % 7)
                },
                'description': ['sunny', 'partly cloudy', 'cloudy', 'light rain'][i % 4],
                'icon': ['01d', '02d', '03d', '10d'][i % 4],
                'humidity': 60 + (i % 20),
                'wind_speed': 3.0 + (i % 5),
                'precipitation': 0 if i % 3 != 0 else 2.5
            })
        
        return {
            'success': True,
            'location': location,
            'forecast': forecasts,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'fallback',
            'note': 'Using sample data - API key required for real weather data'
        }


class WeatherHelper:
    """Main weather helper class with enhanced functionality"""
    
    def __init__(self, api_key: str = None):
        self.api = OpenWeatherMapAPI(api_key)
        self.activity_recommendations = {
            'sunny': ['hiking', 'picnic', 'outdoor sports', 'gardening', 'beach'],
            'partly_cloudy': ['walking', 'cycling', 'outdoor dining', 'sightseeing'],
            'cloudy': ['indoor activities', 'museums', 'shopping', 'cafes'],
            'rainy': ['indoor gym', 'reading', 'movies', 'cooking', 'gaming'],
            'snow': ['skiing', 'snowboarding', 'ice skating', 'winter hiking'],
            'stormy': ['indoor activities', 'home projects', 'relaxation']
        }
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get enhanced current weather with recommendations"""
        weather_data = self.api.get_current_weather(location)
        
        if weather_data.get('success'):
            # Add activity recommendations
            description = weather_data['current']['description'].lower()
            recommendations = self._get_activity_recommendations(description)
            weather_data['activity_recommendations'] = recommendations
            
            # Add comfort index
            weather_data['comfort_index'] = self._calculate_comfort_index(weather_data['current'])
            
            # Add clothing suggestions
            weather_data['clothing_suggestions'] = self._get_clothing_suggestions(weather_data['current'])
        
        return weather_data
    
    def get_forecast_with_insights(self, location: str, days: int = 5) -> Dict[str, Any]:
        """Get forecast with insights and recommendations"""
        forecast_data = self.api.get_forecast(location, days)
        
        if forecast_data.get('success'):
            # Add insights for each day
            for day in forecast_data['forecast']:
                day['activity_recommendations'] = self._get_activity_recommendations(day['description'])
                day['comfort_index'] = self._calculate_comfort_index_simple(
                    day['temperature']['max'],
                    day['humidity']
                )
                day['outdoor_suitability'] = self._rate_outdoor_suitability(day)
            
            # Add weekly insights
            forecast_data['weekly_insights'] = self._generate_weekly_insights(forecast_data['forecast'])
        
        return forecast_data
    
    def get_weather_alerts(self, location: str) -> Dict[str, Any]:
        """Get weather alerts and warnings"""
        try:
            current_weather = self.api.get_current_weather(location)
            alerts = []
            
            if current_weather.get('success'):
                current = current_weather['current']
                
                # Temperature alerts
                if current['temperature'] > 35:
                    alerts.append({
                        'type': 'heat_warning',
                        'severity': 'high',
                        'message': 'Extreme heat warning - stay hydrated and avoid prolonged sun exposure',
                        'recommendations': ['Stay indoors', 'Drink plenty of water', 'Wear light clothing']
                    })
                elif current['temperature'] < -10:
                    alerts.append({
                        'type': 'cold_warning',
                        'severity': 'high',
                        'message': 'Extreme cold warning - dress warmly and limit outdoor exposure',
                        'recommendations': ['Layer clothing', 'Cover exposed skin', 'Warm up frequently']
                    })
                
                # Wind alerts
                if current['wind_speed'] > 15:
                    alerts.append({
                        'type': 'wind_warning',
                        'severity': 'medium',
                        'message': 'Strong winds expected - secure loose objects',
                        'recommendations': ['Avoid cycling', 'Secure outdoor items', 'Drive carefully']
                    })
                
                # Humidity alerts
                if current['humidity'] > 80:
                    alerts.append({
                        'type': 'humidity_alert',
                        'severity': 'low',
                        'message': 'High humidity levels - may feel warmer than actual temperature',
                        'recommendations': ['Stay cool', 'Use air conditioning', 'Limit strenuous activity']
                    })
            
            return {
                'success': True,
                'location': location,
                'alerts': alerts,
                'alert_count': len(alerts),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting weather alerts: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'alerts': []
            }
    
    def get_best_times_today(self, location: str, activity: str = 'outdoor') -> Dict[str, Any]:
        """Get best times for specific activities today"""
        try:
            # Get hourly forecast (simplified for demo)
            current_weather = self.api.get_current_weather(location)
            
            if not current_weather.get('success'):
                return {'success': False, 'error': 'Weather data unavailable'}
            
            # Generate sample hourly data based on current conditions
            current_temp = current_weather['current']['temperature']
            current_desc = current_weather['current']['description']
            
            hourly_forecast = []
            for hour in range(24):
                # Simulate temperature variation
                temp_variation = -5 + (hour % 12) * 1.2
                hourly_temp = current_temp + temp_variation
                
                hourly_forecast.append({
                    'hour': hour,
                    'time': f"{hour:02d}:00",
                    'temperature': round(hourly_temp, 1),
                    'description': current_desc,
                    'suitability_score': self._calculate_activity_suitability(hourly_temp, activity)
                })
            
            # Find best times
            best_times = sorted(hourly_forecast, key=lambda x: x['suitability_score'], reverse=True)[:3]
            
            return {
                'success': True,
                'location': location,
                'activity': activity,
                'best_times': best_times,
                'hourly_forecast': hourly_forecast,
                'recommendation': f"Best time for {activity}: {best_times[0]['time']}",
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting best times: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_activity_recommendations(self, description: str) -> List[str]:
        """Get activity recommendations based on weather description"""
        description_lower = description.lower()
        
        for weather_type, activities in self.activity_recommendations.items():
            if weather_type in description_lower:
                return activities
        
        # Default recommendations
        return ['indoor activities', 'flexible planning']
    
    def _calculate_comfort_index(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comfort index based on temperature, humidity, and wind"""
        temp = weather_data['temperature']
        humidity = weather_data['humidity']
        wind_speed = weather_data['wind_speed']
        
        # Heat index calculation (simplified)
        if temp > 26:
            heat_index = temp + 0.5 * (humidity - 50) / 100 * (temp - 26)
        else:
            heat_index = temp
        
        # Wind chill calculation (simplified)
        if temp < 10 and wind_speed > 5:
            wind_chill = temp - wind_speed * 0.5
        else:
            wind_chill = temp
        
        # Overall comfort score (0-100)
        if 18 <= temp <= 24 and 40 <= humidity <= 60:
            comfort_score = 90
        elif 15 <= temp <= 27 and 30 <= humidity <= 70:
            comfort_score = 75
        elif 10 <= temp <= 30:
            comfort_score = 60
        else:
            comfort_score = 40
        
        # Adjust for extreme conditions
        if humidity > 80 or wind_speed > 20:
            comfort_score -= 15
        
        return {
            'score': max(0, min(100, comfort_score)),
            'heat_index': round(heat_index, 1),
            'wind_chill': round(wind_chill, 1),
            'rating': self._get_comfort_rating(comfort_score)
        }
    
    def _calculate_comfort_index_simple(self, temperature: float, humidity: int) -> Dict[str, Any]:
        """Simplified comfort index for forecast data"""
        if 18 <= temperature <= 24 and 40 <= humidity <= 60:
            score = 90
        elif 15 <= temperature <= 27 and 30 <= humidity <= 70:
            score = 75
        else:
            score = 50
        
        return {
            'score': score,
            'rating': self._get_comfort_rating(score)
        }
    
    def _get_comfort_rating(self, score: int) -> str:
        """Convert comfort score to rating"""
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        else:
            return 'poor'
    
    def _get_clothing_suggestions(self, weather_data: Dict[str, Any]) -> List[str]:
        """Get clothing suggestions based on weather"""
        temp = weather_data['temperature']
        wind_speed = weather_data['wind_speed']
        description = weather_data['description'].lower()
        
        suggestions = []
        
        # Temperature-based suggestions
        if temp > 25:
            suggestions.extend(['light clothing', 'shorts', 't-shirt', 'sunglasses'])
        elif temp > 15:
            suggestions.extend(['light jacket', 'long pants', 'comfortable shoes'])
        elif temp > 5:
            suggestions.extend(['warm jacket', 'layers', 'closed shoes'])
        else:
            suggestions.extend(['heavy coat', 'warm layers', 'boots', 'gloves', 'hat'])
        
        # Weather-specific additions
        if 'rain' in description:
            suggestions.extend(['umbrella', 'waterproof jacket', 'waterproof shoes'])
        elif 'sun' in description or 'clear' in description:
            suggestions.extend(['sunscreen', 'hat', 'sunglasses'])
        elif wind_speed > 10:
            suggestions.extend(['windbreaker', 'secure hat'])
        
        return list(set(suggestions))  # Remove duplicates
    
    def _rate_outdoor_suitability(self, day_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rate how suitable the day is for outdoor activities"""
        temp_max = day_data['temperature']['max']
        temp_min = day_data['temperature']['min']
        humidity = day_data['humidity']
        wind_speed = day_data['wind_speed']
        precipitation = day_data['precipitation']
        
        score = 100
        
        # Temperature scoring
        if not (15 <= temp_max <= 25):
            score -= 20
        if temp_max - temp_min > 15:  # Large temperature swing
            score -= 10
        
        # Weather conditions
        if precipitation > 2.5:
            score -= 30
        elif precipitation > 0:
            score -= 15
        
        if humidity > 80:
            score -= 15
        elif humidity < 30:
            score -= 10
        
        if wind_speed > 15:
            score -= 20
        
        score = max(0, score)
        
        if score >= 80:
            rating = 'excellent'
        elif score >= 60:
            rating = 'good'
        elif score >= 40:
            rating = 'fair'
        else:
            rating = 'poor'
        
        return {
            'score': score,
            'rating': rating
        }
    
    def _calculate_activity_suitability(self, temperature: float, activity: str) -> int:
        """Calculate suitability score for specific activity"""
        base_score = 50
        
        activity_preferences = {
            'outdoor': {'ideal_temp': 22, 'temp_tolerance': 8},
            'running': {'ideal_temp': 18, 'temp_tolerance': 6},
            'cycling': {'ideal_temp': 20, 'temp_tolerance': 7},
            'hiking': {'ideal_temp': 19, 'temp_tolerance': 9},
            'gardening': {'ideal_temp': 23, 'temp_tolerance': 5}
        }
        
        prefs = activity_preferences.get(activity, {'ideal_temp': 22, 'temp_tolerance': 8})
        
        temp_diff = abs(temperature - prefs['ideal_temp'])
        if temp_diff <= prefs['temp_tolerance']:
            base_score += (prefs['temp_tolerance'] - temp_diff) * 5
        else:
            base_score -= temp_diff * 2
        
        return max(0, min(100, base_score))
    
    def _generate_weekly_insights(self, forecast: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights for the weekly forecast"""
        if not forecast:
            return {}
        
        temps = [day['temperature']['max'] for day in forecast]
        rain_days = len([day for day in forecast if day['precipitation'] > 0])
        
        insights = {
            'warmest_day': max(forecast, key=lambda x: x['temperature']['max'])['day_name'],
            'coolest_day': min(forecast, key=lambda x: x['temperature']['min'])['day_name'],
            'average_high': round(sum(temps) / len(temps), 1),
            'rain_days': rain_days,
            'best_outdoor_day': max(forecast, key=lambda x: x['outdoor_suitability']['score'])['day_name'],
            'recommendations': []
        }
        
        # Generate recommendations
        if rain_days > len(forecast) / 2:
            insights['recommendations'].append('Pack an umbrella - rainy week ahead')
        
        if max(temps) - min(temps) > 10:
            insights['recommendations'].append('Variable temperatures - layer your clothing')
        
        if all(day['outdoor_suitability']['score'] > 70 for day in forecast):
            insights['recommendations'].append('Great week for outdoor activities!')
        
        return insights


# Global weather helper instance
weather_helper = WeatherHelper()


# Helper functions for backward compatibility
def get_current_weather(location: str):
    """Get current weather for location"""
    return weather_helper.get_current_weather(location)


def get_weather_forecast(location: str, days: int = 5):
    """Get weather forecast for location"""
    return weather_helper.get_forecast_with_insights(location, days)


def get_weather_alerts(location: str):
    """Get weather alerts for location"""
    return weather_helper.get_weather_alerts(location)


def get_activity_recommendations(location: str, activity: str = 'outdoor'):
    """Get activity recommendations based on weather"""
    return weather_helper.get_best_times_today(location, activity)


class WeatherService:
    """Legacy compatibility class"""
    
    def __init__(self, api_key: str = None):
        self.helper = WeatherHelper(api_key)
    
    def __getattr__(self, name):
        return getattr(self.helper, name)