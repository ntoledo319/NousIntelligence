"""
Smart Home Integration module
Features:
- Smart device control integration
- Weather-based automation suggestions
- Spotify playback on home devices
- Remote control of smart home devices
"""

import os
import logging
import json
import requests
from typing import Dict, List, Any, Optional, Union, Tuple

from utils.spotify_helper import get_spotify_client
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Smart Home API configurations - placeholders until user provides actual API keys
SMARTTHINGS_API_KEY = os.environ.get("SMARTTHINGS_API_KEY")
SMARTTHINGS_API_BASE = "https://api.smartthings.com/v1"

HOMEASSISTANT_TOKEN = os.environ.get("HOMEASSISTANT_TOKEN")
HOMEASSISTANT_URL = os.environ.get("HOMEASSISTANT_URL")

HUBITAT_TOKEN = os.environ.get("HUBITAT_TOKEN")
HUBITAT_URL = os.environ.get("HUBITAT_URL")

class SmartHomeStatus:
    """Status tracker for smart home integration state"""
    def __init__(self):
        self.enabled = False
        self.platform = None
        self.devices = {}
        self.device_capabilities = {}
        self.rooms = {}
        self.last_error = None
        self.last_updated = None
        
    def set_platform(self, platform: str):
        """Set the active smart home platform"""
        self.platform = platform
        self.enabled = True
        
    def reset(self):
        """Reset the integration state"""
        self.enabled = False
        self.platform = None
        self.devices = {}
        self.device_capabilities = {}
        self.rooms = {}
        
    def has_devices(self) -> bool:
        """Check if any devices are registered"""
        return len(self.devices) > 0
        
    def has_audio_devices(self) -> bool:
        """Check if any audio-capable devices are registered"""
        for device_id, capabilities in self.device_capabilities.items():
            if "audio" in capabilities or "speaker" in capabilities or "mediaPlayback" in capabilities:
                return True
        return False

# Global status object
SMART_HOME_STATUS = SmartHomeStatus()

def configure_smart_home_integration(platform: str, api_key: str = None, url: str = None) -> Dict[str, Any]:
    """
    Configure smart home integration with a specific platform
    
    Args:
        platform: Smart home platform (smartthings, homeassistant, hubitat)
        api_key: API key/token for the platform
        url: Base URL for the platform (for HomeAssistant and Hubitat)
        
    Returns:
        Dict with configuration status
    """
    try:
        platform = platform.lower()
        
        # Reset current status
        SMART_HOME_STATUS.reset()
        
        # Configure based on platform
        if platform == "smartthings":
            if not api_key and not SMARTTHINGS_API_KEY:
                return {"success": False, "error": "SmartThings API key required"}
                
            # Set key in environment if provided
            if api_key:
                os.environ["SMARTTHINGS_API_KEY"] = api_key
                
            # Test the connection
            headers = {
                "Authorization": f"Bearer {api_key or SMARTTHINGS_API_KEY}",
                "Content-Type": "application/json"
            }
            
            try:
                # Mock API call for demonstration purposes
                # In a real implementation, we would call the actual API
                # response = requests.get(f"{SMARTTHINGS_API_BASE}/devices", headers=headers)
                # if response.status_code != 200:
                #    return {"success": False, "error": f"API Error: {response.status_code}"}
                
                # Update status
                SMART_HOME_STATUS.set_platform("smartthings")
                return {"success": True, "message": "SmartThings integration configured"}
            except Exception as e:
                return {"success": False, "error": f"Connection error: {str(e)}"}
                
        elif platform == "homeassistant":
            if not url and not HOMEASSISTANT_URL:
                return {"success": False, "error": "Home Assistant URL required"}
                
            if not api_key and not HOMEASSISTANT_TOKEN:
                return {"success": False, "error": "Home Assistant API token required"}
                
            # Set values in environment if provided
            if url:
                os.environ["HOMEASSISTANT_URL"] = url
            if api_key:
                os.environ["HOMEASSISTANT_TOKEN"] = api_key
                
            # Test the connection
            headers = {
                "Authorization": f"Bearer {api_key or HOMEASSISTANT_TOKEN}",
                "Content-Type": "application/json"
            }
            
            try:
                # Mock API call for demonstration purposes
                # response = requests.get(f"{url or HOMEASSISTANT_URL}/api/states", headers=headers)
                # if response.status_code != 200:
                #    return {"success": False, "error": f"API Error: {response.status_code}"}
                
                # Update status
                SMART_HOME_STATUS.set_platform("homeassistant")
                return {"success": True, "message": "Home Assistant integration configured"}
            except Exception as e:
                return {"success": False, "error": f"Connection error: {str(e)}"}
                
        elif platform == "hubitat":
            if not url and not HUBITAT_URL:
                return {"success": False, "error": "Hubitat hub URL required"}
                
            if not api_key and not HUBITAT_TOKEN:
                return {"success": False, "error": "Hubitat access token required"}
                
            # Set values in environment if provided
            if url:
                os.environ["HUBITAT_URL"] = url
            if api_key:
                os.environ["HUBITAT_TOKEN"] = api_key
                
            # Test the connection
            try:
                # Mock API call for demonstration purposes
                # response = requests.get(f"{url or HUBITAT_URL}/apps/api/{api_key or HUBITAT_TOKEN}/devices")
                # if response.status_code != 200:
                #    return {"success": False, "error": f"API Error: {response.status_code}"}
                
                # Update status
                SMART_HOME_STATUS.set_platform("hubitat")
                return {"success": True, "message": "Hubitat integration configured"}
            except Exception as e:
                return {"success": False, "error": f"Connection error: {str(e)}"}
        else:
            return {"success": False, "error": f"Unsupported platform: {platform}"}
    
    except Exception as e:
        logging.error(f"Error configuring smart home integration: {str(e)}")
        return {"success": False, "error": f"Configuration error: {str(e)}"}

def discover_devices() -> Dict[str, Any]:
    """
    Discover smart home devices
    
    Returns:
        Dict with discovered devices
    """
    try:
        if not SMART_HOME_STATUS.enabled:
            return {"success": False, "error": "Smart home integration not configured"}
            
        platform = SMART_HOME_STATUS.platform
        
        # Mock device discovery based on platform
        if platform == "smartthings":
            # In a real implementation, we would call the actual API
            # headers = {"Authorization": f"Bearer {SMARTTHINGS_API_KEY}"}
            # response = requests.get(f"{SMARTTHINGS_API_BASE}/devices", headers=headers)
            # if response.status_code != 200:
            #    return {"success": False, "error": f"API Error: {response.status_code}"}
            # devices = response.json()["items"]
            
            # Mock devices for demonstration
            devices = [
                {
                    "id": "abc123",
                    "name": "Living Room Light",
                    "type": "light",
                    "capabilities": ["switch", "switchLevel"],
                    "room": "Living Room"
                },
                {
                    "id": "def456",
                    "name": "Kitchen Light",
                    "type": "light",
                    "capabilities": ["switch"],
                    "room": "Kitchen"
                },
                {
                    "id": "ghi789",
                    "name": "Bedroom Speaker",
                    "type": "speaker",
                    "capabilities": ["switch", "audioVolume", "mediaPlayback"],
                    "room": "Bedroom"
                },
                {
                    "id": "jkl012",
                    "name": "Living Room Thermostat",
                    "type": "thermostat",
                    "capabilities": ["thermostatMode", "thermostatCoolingSetpoint", "thermostatHeatingSetpoint"],
                    "room": "Living Room"
                }
            ]
        
        elif platform == "homeassistant":
            # Mock devices for HomeAssistant
            devices = [
                {
                    "id": "light.living_room",
                    "name": "Living Room Light",
                    "type": "light",
                    "capabilities": ["switch", "brightness"],
                    "room": "Living Room"
                },
                {
                    "id": "light.kitchen",
                    "name": "Kitchen Light",
                    "type": "light",
                    "capabilities": ["switch"],
                    "room": "Kitchen"
                },
                {
                    "id": "media_player.bedroom",
                    "name": "Bedroom Speaker",
                    "type": "media_player",
                    "capabilities": ["volume", "media_player"],
                    "room": "Bedroom"
                },
                {
                    "id": "climate.living_room",
                    "name": "Living Room Thermostat",
                    "type": "climate",
                    "capabilities": ["temperature", "hvac_mode"],
                    "room": "Living Room"
                }
            ]
            
        elif platform == "hubitat":
            # Mock devices for Hubitat
            devices = [
                {
                    "id": "123",
                    "name": "Living Room Light",
                    "type": "Light",
                    "capabilities": ["Switch", "SwitchLevel"],
                    "room": "Living Room"
                },
                {
                    "id": "456",
                    "name": "Kitchen Light",
                    "type": "Light",
                    "capabilities": ["Switch"],
                    "room": "Kitchen"
                },
                {
                    "id": "789",
                    "name": "Bedroom Speaker",
                    "type": "Speaker",
                    "capabilities": ["Switch", "AudioVolume"],
                    "room": "Bedroom"
                },
                {
                    "id": "012",
                    "name": "Living Room Thermostat",
                    "type": "Thermostat",
                    "capabilities": ["Thermostat"],
                    "room": "Living Room"
                }
            ]
        else:
            return {"success": False, "error": f"Unsupported platform: {platform}"}
        
        # Update internal state
        for device in devices:
            SMART_HOME_STATUS.devices[device["id"]] = {
                "name": device["name"],
                "type": device["type"],
                "room": device["room"]
            }
            SMART_HOME_STATUS.device_capabilities[device["id"]] = device["capabilities"]
            
            # Add room to rooms dict if not exists
            if device["room"] not in SMART_HOME_STATUS.rooms:
                SMART_HOME_STATUS.rooms[device["room"]] = []
                
            # Add device to room
            SMART_HOME_STATUS.rooms[device["room"]].append(device["id"])
            
        return {
            "success": True,
            "platform": platform,
            "device_count": len(devices),
            "devices": devices,
            "rooms": list(SMART_HOME_STATUS.rooms.keys())
        }
        
    except Exception as e:
        logging.error(f"Error discovering devices: {str(e)}")
        return {"success": False, "error": f"Discovery error: {str(e)}"}

def control_device(device_id: str, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Send a command to a smart home device
    
    Args:
        device_id: Device ID
        command: Command to execute (on, off, setBrightness, etc.)
        parameters: Optional parameters for the command
        
    Returns:
        Dict with command result
    """
    try:
        if not SMART_HOME_STATUS.enabled:
            return {"success": False, "error": "Smart home integration not configured"}
            
        platform = SMART_HOME_STATUS.platform
        parameters = parameters or {}
        
        # Check if the device exists
        if device_id not in SMART_HOME_STATUS.devices:
            return {"success": False, "error": f"Device not found: {device_id}"}
            
        device_name = SMART_HOME_STATUS.devices[device_id]["name"]
        device_type = SMART_HOME_STATUS.devices[device_id]["type"]
        
        # Mock device control based on platform
        if platform == "smartthings":
            # In a real implementation, we would call the actual API
            # headers = {"Authorization": f"Bearer {SMARTTHINGS_API_KEY}"}
            # body = {"commands": [{"component": "main", "capability": capability, "command": command, "arguments": list(parameters.values())}]}
            # response = requests.post(f"{SMARTTHINGS_API_BASE}/devices/{device_id}/commands", headers=headers, json=body)
            # if response.status_code != 200:
            #    return {"success": False, "error": f"API Error: {response.status_code}"}
            
            # Mock response for demonstration
            success = True
            message = f"Command '{command}' sent to {device_name}"
            
        elif platform == "homeassistant":
            # Mock HomeAssistant control
            service = None
            if command == "on" or command == "turn_on":
                service = "turn_on"
            elif command == "off" or command == "turn_off":
                service = "turn_off"
            elif command == "setBrightness" or command == "set_brightness":
                service = "turn_on"
                parameters["brightness"] = parameters.get("brightness", 255)
            else:
                service = command
                
            # In a real implementation, we would call the actual API
            # headers = {"Authorization": f"Bearer {HOMEASSISTANT_TOKEN}"}
            # body = {"entity_id": device_id, **parameters}
            # response = requests.post(f"{HOMEASSISTANT_URL}/api/services/{device_type}/{service}", headers=headers, json=body)
            # if response.status_code != 200:
            #    return {"success": False, "error": f"API Error: {response.status_code}"}
            
            # Mock response for demonstration
            success = True
            message = f"Service '{service}' called on {device_name}"
            
        elif platform == "hubitat":
            # Mock Hubitat control
            # In a real implementation, we would call the actual API
            # response = requests.get(f"{HUBITAT_URL}/apps/api/{HUBITAT_TOKEN}/devices/{device_id}/{command}{'/'+'/'.join(str(p) for p in parameters.values()) if parameters else ''}")
            # if response.status_code != 200:
            #    return {"success": False, "error": f"API Error: {response.status_code}"}
            
            # Mock response for demonstration
            success = True
            message = f"Command '{command}' sent to {device_name}"
            
        else:
            return {"success": False, "error": f"Unsupported platform: {platform}"}
            
        return {
            "success": success,
            "device": device_name,
            "command": command,
            "parameters": parameters,
            "message": message
        }
        
    except Exception as e:
        logging.error(f"Error controlling device: {str(e)}")
        return {"success": False, "error": f"Control error: {str(e)}"}

def control_room(room: str, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Send a command to all devices in a room
    
    Args:
        room: Room name
        command: Command to execute (on, off, setBrightness, etc.)
        parameters: Optional parameters for the command
        
    Returns:
        Dict with command results
    """
    try:
        if not SMART_HOME_STATUS.enabled:
            return {"success": False, "error": "Smart home integration not configured"}
            
        # Find all devices in the room
        room_devices = []
        for device_id, device in SMART_HOME_STATUS.devices.items():
            if device["room"].lower() == room.lower():
                room_devices.append(device_id)
                
        if not room_devices:
            return {"success": False, "error": f"No devices found in room: {room}"}
            
        # Send command to all devices
        results = []
        success = True
        
        for device_id in room_devices:
            # Check if the device supports this command based on type
            device_type = SMART_HOME_STATUS.devices[device_id]["type"]
            
            # For light devices
            if device_type.lower() in ["light", "switch"] and command.lower() in ["on", "off", "turn_on", "turn_off", "setbrightness"]:
                result = control_device(device_id, command, parameters)
                results.append(result)
                if not result["success"]:
                    success = False
                    
            # For speaker devices
            elif device_type.lower() in ["speaker", "media_player"] and command.lower() in ["on", "off", "turn_on", "turn_off", "setvolume", "play", "pause", "stop"]:
                result = control_device(device_id, command, parameters)
                results.append(result)
                if not result["success"]:
                    success = False
                    
            # For thermostat devices
            elif device_type.lower() in ["thermostat", "climate"] and command.lower() in ["settemperature", "setmode", "on", "off"]:
                result = control_device(device_id, command, parameters)
                results.append(result)
                if not result["success"]:
                    success = False
                    
        return {
            "success": success,
            "room": room,
            "command": command,
            "parameters": parameters,
            "device_count": len(room_devices),
            "results": results
        }
        
    except Exception as e:
        logging.error(f"Error controlling room: {str(e)}")
        return {"success": False, "error": f"Room control error: {str(e)}"}

def play_spotify_on_device(session, device_id: str, query: str = None, playlist_id: str = None) -> Dict[str, Any]:
    """
    Play Spotify music on a smart home device
    
    Args:
        session: Flask session object
        device_id: Smart home device ID
        query: Search query for track/artist/album
        playlist_id: Spotify playlist ID
        
    Returns:
        Dict with playback result
    """
    try:
        if not SMART_HOME_STATUS.enabled:
            return {"success": False, "error": "Smart home integration not configured"}
            
        # Get Spotify client
        from app import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT
        spotify, _ = get_spotify_client(session, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT)
        
        if not spotify:
            return {"success": False, "error": "Spotify client not available"}
            
        # Check if the device exists
        if device_id not in SMART_HOME_STATUS.devices:
            return {"success": False, "error": f"Device not found: {device_id}"}
            
        # Check if the device supports audio playback
        device_capabilities = SMART_HOME_STATUS.device_capabilities.get(device_id, [])
        device_type = SMART_HOME_STATUS.devices[device_id]["type"]
        
        if not any(cap.lower() in ["audio", "speaker", "mediaplayer", "media_player", "mediaplayback"] 
                for cap in device_capabilities + [device_type]):
            return {"success": False, "error": f"Device does not support audio playback: {device_id}"}
            
        device_name = SMART_HOME_STATUS.devices[device_id]["name"]
        
        # First, power on the device
        control_result = control_device(device_id, "on")
        if not control_result["success"]:
            return {"success": False, "error": f"Failed to power on device: {control_result['error']}"}
            
        # Set volume (optional)
        control_device(device_id, "setVolume", {"level": 50})
        
        # Play content based on what was provided
        message = ""
        if query:
            # Search for the track/artist/album
            from utils.spotify_helper import play_track
            result = play_track(spotify, query)
            message = result
        elif playlist_id:
            # Play a specific playlist
            try:
                spotify.start_playback(context_uri=f"spotify:playlist:{playlist_id}")
                message = f"Playing playlist on {device_name}"
            except Exception as e:
                return {"success": False, "error": f"Failed to play playlist: {str(e)}"}
        else:
            # No content specified, just resume playback
            try:
                spotify.start_playback()
                message = f"Resumed playback on {device_name}"
            except Exception as e:
                return {"success": False, "error": f"Failed to start playback: {str(e)}"}
            
        return {
            "success": True,
            "device": device_name,
            "message": message
        }
        
    except Exception as e:
        logging.error(f"Error playing Spotify on device: {str(e)}")
        return {"success": False, "error": f"Playback error: {str(e)}"}

def get_weather_based_automation_suggestions() -> Dict[str, Any]:
    """
    Generate weather-based automation suggestions for smart home
    
    Returns:
        Dict with automation suggestions
    """
    try:
        if not SMART_HOME_STATUS.enabled:
            return {"success": False, "error": "Smart home integration not configured"}
            
        if not SMART_HOME_STATUS.has_devices():
            return {"success": False, "error": "No devices discovered"}
            
        if not OPENAI_API_KEY:
            return {"success": False, "error": "OpenAI API key required for suggestions"}
            
        # Get weather data (assuming we have a primary location)
        from utils.weather_helper import get_weather_forecast
        
        # Use a default location if none is set
        forecast = get_weather_forecast("New York", days=2)
        if "error" in forecast:
            return {"success": False, "error": f"Could not get weather forecast: {forecast['error']}"}
            
        # Extract relevant weather data
        weather_data = {
            "location": forecast.get("location", "unknown"),
            "current": {
                "temp": forecast.get("temp", "unknown"),
                "conditions": forecast.get("conditions", "unknown"),
                "is_daytime": forecast.get("is_daytime", True),
            },
            "forecast": {
                "high": forecast.get("temp_max", "unknown"),
                "low": forecast.get("temp_min", "unknown"),
                "conditions": forecast.get("conditions", "unknown"),
            }
        }
        
        # Get device information
        devices = []
        rooms = []
        for device_id, device in SMART_HOME_STATUS.devices.items():
            devices.append({
                "id": device_id,
                "name": device["name"],
                "type": device["type"],
                "room": device["room"],
                "capabilities": SMART_HOME_STATUS.device_capabilities.get(device_id, [])
            })
            if device["room"] not in rooms:
                rooms.append(device["room"])
        
        # Generate suggestions with AI
        prompt = f"""
        I need smart home automation suggestions based on weather conditions.
        
        Current weather in {weather_data["location"]}:
        - Temperature: {weather_data["current"]["temp"]}
        - Conditions: {weather_data["current"]["conditions"]}
        - Time of day: {"Daytime" if weather_data["current"]["is_daytime"] else "Nighttime"}
        
        Forecast:
        - High: {weather_data["forecast"]["high"]}
        - Low: {weather_data["forecast"]["low"]}
        - Conditions: {weather_data["forecast"]["conditions"]}
        
        Available rooms: {", ".join(rooms)}
        
        Available devices:
        {json.dumps(devices, indent=2)}
        
        Please suggest automation rules based on:
        1. Current and forecast weather conditions
        2. Available devices and their capabilities
        3. Common comfort and energy efficiency needs
        
        For each suggestion, include:
        - Name: Short, descriptive name for the automation
        - Trigger: Weather or time condition that triggers the automation
        - Actions: Device commands to execute
        - Benefits: Why this automation is useful
        
        Format as a JSON object with an array of suggestions.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a smart home automation expert who provides practical and useful automation suggestions based on weather conditions."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        suggestions = json.loads(response.choices[0].message.content)
        
        # Add weather data to the response
        suggestions["weather"] = weather_data
        suggestions["success"] = True
        
        return suggestions
        
    except Exception as e:
        logging.error(f"Error generating automation suggestions: {str(e)}")
        return {"success": False, "error": f"Suggestion error: {str(e)}"}

def create_voice_command(command_text: str, user_id: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Process a natural language voice command for smart home control with enhanced context awareness
    
    Args:
        command_text: Natural language command
        user_id: Optional user ID for personalization and context
        context: Optional additional context (time of day, user location, etc.)
        
    Returns:
        Dict with processed command and execution result
    """
    try:
        if not SMART_HOME_STATUS.enabled:
            return {"success": False, "error": "Smart home integration not configured"}
            
        if not SMART_HOME_STATUS.has_devices():
            return {"success": False, "error": "No devices discovered"}
            
        if not OPENAI_API_KEY:
            return {"success": False, "error": "OpenAI API key required for voice commands"}
            
        # Get device and room information
        devices = []
        rooms = []
        for device_id, device in SMART_HOME_STATUS.devices.items():
            devices.append({
                "id": device_id,
                "name": device["name"],
                "type": device["type"],
                "room": device["room"],
                "capabilities": SMART_HOME_STATUS.device_capabilities.get(device_id, [])
            })
            if device["room"] not in rooms:
                rooms.append(device["room"])
        
        # Prepare context information
        context_str = ""
        if context:
            context_items = []
            
            if "time_of_day" in context:
                context_items.append(f"Time of day: {context['time_of_day']}")
                
            if "user_location" in context:
                context_items.append(f"User location: {context['user_location']}")
                
            if "weather" in context:
                context_items.append(f"Weather: {context['weather']}")
                
            if "temperature" in context:
                context_items.append(f"Current temperature: {context['temperature']}")
                
            if "previous_commands" in context and context["previous_commands"]:
                prev_cmds = context["previous_commands"][-3:]  # Get last 3 commands
                context_items.append(f"Recent commands: {', '.join(prev_cmds)}")
                
            context_str = "\n".join(context_items)
        
        # Use AI to parse the command with added context awareness
        system_prompt = """
        You are an advanced smart home voice assistant that parses natural language commands into structured device control commands.
        
        You should understand context, implied targets, and natural conversational references like "it", "them", "there", etc. when 
        referring to previously mentioned devices or rooms.
        
        You should also understand complex commands that may involve multiple devices or rooms, as well as multi-step controls.
        
        When parsing commands, determine:
        1. Target (device name, room, or "all")
        2. Target type (device, room, all)
        3. Command (on, off, setBrightness, setTemperature, etc.)
        4. Parameters (brightness level, temperature, etc.)
        
        Return a JSON object with the following structure:
        {
            "target_type": "device|room|all",
            "target": "name of device or room",
            "command": "command name",
            "parameters": {"param1": value1, "param2": value2},
            "confirmation_message": "human-friendly confirmation of the action"
        }
        
        If the command is ambiguous or targets unavailable devices, include an "error" field.
        """
        
        user_prompt = f"""
        Parse this voice command for smart home control: "{command_text}"
        
        Available rooms: {", ".join(rooms)}
        
        Available devices:
        {json.dumps(devices, indent=2)}
        """
        
        if context_str:
            user_prompt += f"\n\nContext Information:\n{context_str}"
        
        from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
        
        # Prepare messages with proper typing
        messages = []
        
        # Add system message
        system_msg: ChatCompletionSystemMessageParam = {
            "role": "system",
            "content": system_prompt
        }
        messages.append(system_msg)
        
        # Add user message
        user_msg: ChatCompletionUserMessageParam = {
            "role": "user",
            "content": user_prompt
        }
        messages.append(user_msg)
        
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        result_content = response.choices[0].message.content
        if result_content is None:
            return {"success": False, "error": "Empty response from AI parser"}
            
        parsed_command = json.loads(result_content)
        
        # Check if there was an error in parsing
        if "error" in parsed_command:
            return {"success": False, "error": parsed_command["error"], "parsed_command": parsed_command}
            
        # Execute the command
        result = None
        target_type = parsed_command.get("target_type", "unknown")
        target = parsed_command.get("target", "")
        command = parsed_command.get("command", "")
        parameters = parsed_command.get("parameters", {})
        
        if target_type == "device":
            # Find the device ID by name (case insensitive and partial matching)
            device_id = None
            for id, device in SMART_HOME_STATUS.devices.items():
                if target.lower() in device["name"].lower():
                    device_id = id
                    # Update target to exact name for feedback
                    parsed_command["target"] = device["name"]
                    break
                    
            if device_id:
                result = control_device(device_id, command, parameters)
            else:
                return {"success": False, "error": f"Device not found: {target}", "parsed_command": parsed_command}
                
        elif target_type == "room":
            # Case insensitive room matching
            room_match = None
            for room in rooms:
                if target.lower() in room.lower():
                    room_match = room
                    # Update target to exact room name for feedback
                    parsed_command["target"] = room
                    break
                    
            if room_match:
                result = control_room(room_match, command, parameters)
            else:
                return {"success": False, "error": f"Room not found: {target}", "parsed_command": parsed_command}
            
        elif target_type == "all":
            # Control all devices
            results = []
            success = True
            
            for device_id in SMART_HOME_STATUS.devices:
                device_result = control_device(device_id, command, parameters)
                results.append(device_result)
                if not device_result["success"]:
                    success = False
                    
            result = {
                "success": success,
                "command": command,
                "parameters": parameters,
                "device_count": len(SMART_HOME_STATUS.devices),
                "results": results
            }
        else:
            return {"success": False, "error": f"Unknown target type: {target_type}", "parsed_command": parsed_command}
            
        # Add the parsed command and confirmation message to the result
        final_result = {
            "success": result["success"] if result else False,
            "parsed_command": parsed_command,
            "execution_result": result,
            "confirmation_message": parsed_command.get("confirmation_message", "Command executed successfully")
        }
            
        # If user_id provided, add this command to context memory
        if user_id:
            try:
                from utils.ai_helper import conversation_memory
                
                # Add as context for future commands
                conversation_memory.add_context(
                    user_id, 
                    "smart_home_commands", 
                    f"Command: {command} on {target_type} '{target}' with parameters {parameters}"
                )
            except ImportError:
                logging.warning("Could not import conversation_memory from ai_helper")
            
        return final_result
        
    except Exception as e:
        logging.error(f"Error processing voice command: {str(e)}")
        return {"success": False, "error": f"Voice command processing error: {str(e)}"}
        
def create_routine(name: str, triggers: List[Dict], actions: List[Dict], user_id: str = None) -> Dict[str, Any]:
    """
    Create a smart home routine/automation
    
    Args:
        name: Name of the routine
        triggers: List of trigger conditions (time, device state, etc.)
        actions: List of actions to perform
        user_id: Optional user ID for personalization
        
    Returns:
        Dict with routine creation result
    """
    try:
        if not SMART_HOME_STATUS.enabled:
            return {"success": False, "error": "Smart home integration not configured"}
            
        if not SMART_HOME_STATUS.has_devices():
            return {"success": False, "error": "No devices discovered"}
        
        # Validation
        if not name:
            return {"success": False, "error": "Routine name is required"}
            
        if not triggers or not isinstance(triggers, list):
            return {"success": False, "error": "At least one trigger is required"}
            
        if not actions or not isinstance(actions, list):
            return {"success": False, "error": "At least one action is required"}
        
        # In a real implementation, we would store the routine in a database
        # For demonstration, we return a mock success response
        
        return {
            "success": True,
            "routine": {
                "id": f"routine_{name.lower().replace(' ', '_')}",
                "name": name,
                "triggers": triggers,
                "actions": actions,
                "created_at": datetime.datetime.now().isoformat()
            },
            "message": f"Routine '{name}' created successfully"
        }
    
    except Exception as e:
        logging.error(f"Error creating routine: {str(e)}")
        return {"success": False, "error": f"Routine creation error: {str(e)}"}
        
def get_device_status(device_id: str = None, room: str = None) -> Dict[str, Any]:
    """
    Get status information for devices
    
    Args:
        device_id: Optional specific device ID
        room: Optional room name to filter devices
        
    Returns:
        Dict with device status information
    """
    try:
        if not SMART_HOME_STATUS.enabled:
            return {"success": False, "error": "Smart home integration not configured"}
            
        if not SMART_HOME_STATUS.has_devices():
            return {"success": False, "error": "No devices discovered"}
            
        # If specific device requested
        if device_id:
            if device_id not in SMART_HOME_STATUS.devices:
                return {"success": False, "error": f"Device not found: {device_id}"}
                
            # In a real implementation, we would query the device status via API
            # For demonstration, we return mock data
            device = SMART_HOME_STATUS.devices[device_id]
            capabilities = SMART_HOME_STATUS.device_capabilities.get(device_id, [])
            
            # Generate mock status based on device type
            status = {"online": True}
            
            if "switch" in str(capabilities).lower():
                status["power"] = "on"  # or "off"
                
            if "switchLevel" in str(capabilities).lower() or "brightness" in str(capabilities).lower():
                status["brightness"] = 65  # 0-100
                
            if "thermostat" in str(capabilities).lower() or "temperature" in str(capabilities).lower():
                status["mode"] = "heat"  # or "cool", "auto", "off"
                status["temperature"] = 72  # degrees
                status["target_temperature"] = 68  # degrees
                
            if "audio" in str(capabilities).lower() or "mediaPlayback" in str(capabilities).lower():
                status["volume"] = 40  # 0-100
                status["playing"] = False  # or True
                
            return {
                "success": True,
                "device": {
                    "id": device_id,
                    "name": device["name"],
                    "type": device["type"],
                    "room": device["room"],
                    "capabilities": capabilities,
                    "status": status
                }
            }
            
        # If room filter provided
        elif room:
            # Check if room exists
            if room not in SMART_HOME_STATUS.rooms:
                # Try case-insensitive matching
                room_match = None
                for r in SMART_HOME_STATUS.rooms.keys():
                    if room.lower() == r.lower():
                        room_match = r
                        break
                        
                if not room_match:
                    return {"success": False, "error": f"Room not found: {room}"}
                    
                room = room_match
                
            # Get devices in the room
            device_ids = SMART_HOME_STATUS.rooms.get(room, [])
            devices = []
            
            for device_id in device_ids:
                device = SMART_HOME_STATUS.devices[device_id]
                capabilities = SMART_HOME_STATUS.device_capabilities.get(device_id, [])
                
                # Generate mock status (similar to above)
                status = {"online": True}
                
                if "switch" in str(capabilities).lower():
                    status["power"] = "on"  # or "off"
                    
                if "switchLevel" in str(capabilities).lower() or "brightness" in str(capabilities).lower():
                    status["brightness"] = 65  # 0-100
                    
                if "thermostat" in str(capabilities).lower() or "temperature" in str(capabilities).lower():
                    status["mode"] = "heat"  # or "cool", "auto", "off"
                    status["temperature"] = 72  # degrees
                    status["target_temperature"] = 68  # degrees
                    
                if "audio" in str(capabilities).lower() or "mediaPlayback" in str(capabilities).lower():
                    status["volume"] = 40  # 0-100
                    status["playing"] = False  # or True
                    
                devices.append({
                    "id": device_id,
                    "name": device["name"],
                    "type": device["type"],
                    "capabilities": capabilities,
                    "status": status
                })
                
            return {
                "success": True,
                "room": room,
                "device_count": len(devices),
                "devices": devices
            }
        
        # If no filters, return all devices
        else:
            all_devices = []
            
            for device_id, device in SMART_HOME_STATUS.devices.items():
                capabilities = SMART_HOME_STATUS.device_capabilities.get(device_id, [])
                
                # Generate mock status (similar to above)
                status = {"online": True}
                
                if "switch" in str(capabilities).lower():
                    status["power"] = "on"  # or "off"
                    
                if "switchLevel" in str(capabilities).lower() or "brightness" in str(capabilities).lower():
                    status["brightness"] = 65  # 0-100
                    
                if "thermostat" in str(capabilities).lower() or "temperature" in str(capabilities).lower():
                    status["mode"] = "heat"  # or "cool", "auto", "off"
                    status["temperature"] = 72  # degrees
                    status["target_temperature"] = 68  # degrees
                    
                if "audio" in str(capabilities).lower() or "mediaPlayback" in str(capabilities).lower():
                    status["volume"] = 40  # 0-100
                    status["playing"] = False  # or True
                    
                all_devices.append({
                    "id": device_id,
                    "name": device["name"],
                    "type": device["type"],
                    "room": device["room"],
                    "capabilities": capabilities,
                    "status": status
                })
                
            return {
                "success": True,
                "device_count": len(all_devices),
                "devices": all_devices,
                "rooms": list(SMART_HOME_STATUS.rooms.keys())
            }
            
    except Exception as e:
        logging.error(f"Error getting device status: {str(e)}")
        return {"success": False, "error": f"Status retrieval error: {str(e)}"}