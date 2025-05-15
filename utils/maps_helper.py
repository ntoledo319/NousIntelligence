"""
Helper module for Google Maps integration
"""
import os
import logging
import requests
from datetime import datetime
import json
from urllib.parse import urlencode

# Google Maps API
MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

def geocode_address(address):
    """Convert an address to geographical coordinates"""
    try:
        if not MAPS_API_KEY:
            return {
                "success": False,
                "error": "Maps API key not available"
            }
            
        # Prepare the URL
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": MAPS_API_KEY
        }
        
        # Make the request
        response = requests.get(url, params=params)
        
        # Process the response
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Geocoding API returned status {response.status_code}"
            }
            
        data = response.json()
        
        # Check if the request was successful
        if data["status"] != "OK":
            return {
                "success": False,
                "error": f"Geocoding failed with status: {data['status']}"
            }
            
        # Extract the coordinates
        location = data["results"][0]["geometry"]["location"]
        formatted_address = data["results"][0]["formatted_address"]
        
        return {
            "success": True,
            "lat": location["lat"],
            "lng": location["lng"],
            "formatted_address": formatted_address,
            "place_id": data["results"][0]["place_id"]
        }
        
    except Exception as e:
        logging.error(f"Error geocoding address: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def reverse_geocode(lat, lng):
    """Convert geographical coordinates to an address"""
    try:
        if not MAPS_API_KEY:
            return {
                "success": False,
                "error": "Maps API key not available"
            }
            
        # Prepare the URL
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{lat},{lng}",
            "key": MAPS_API_KEY
        }
        
        # Make the request
        response = requests.get(url, params=params)
        
        # Process the response
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Reverse geocoding API returned status {response.status_code}"
            }
            
        data = response.json()
        
        # Check if the request was successful
        if data["status"] != "OK":
            return {
                "success": False,
                "error": f"Reverse geocoding failed with status: {data['status']}"
            }
            
        # Extract the address components
        address_components = data["results"][0]["address_components"]
        formatted_address = data["results"][0]["formatted_address"]
        
        # Extract specific address components
        components = {}
        for component in address_components:
            for type in component["types"]:
                components[type] = component["long_name"]
                
        return {
            "success": True,
            "formatted_address": formatted_address,
            "street_number": components.get("street_number", ""),
            "street": components.get("route", ""),
            "city": components.get("locality", ""),
            "state": components.get("administrative_area_level_1", ""),
            "country": components.get("country", ""),
            "postal_code": components.get("postal_code", ""),
            "place_id": data["results"][0]["place_id"]
        }
        
    except Exception as e:
        logging.error(f"Error reverse geocoding: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_distance_matrix(origins, destinations, mode="driving"):
    """Get the distance and duration between origins and destinations"""
    try:
        if not MAPS_API_KEY:
            return {
                "success": False,
                "error": "Maps API key not available"
            }
            
        # Validate the mode
        valid_modes = ["driving", "walking", "bicycling", "transit"]
        if mode not in valid_modes:
            mode = "driving"
            
        # Format origins and destinations
        if isinstance(origins, list):
            origins_str = "|".join(origins)
        else:
            origins_str = origins
            
        if isinstance(destinations, list):
            destinations_str = "|".join(destinations)
        else:
            destinations_str = destinations
            
        # Prepare the URL
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origins_str,
            "destinations": destinations_str,
            "mode": mode,
            "key": MAPS_API_KEY
        }
        
        # Make the request
        response = requests.get(url, params=params)
        
        # Process the response
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Distance Matrix API returned status {response.status_code}"
            }
            
        data = response.json()
        
        # Check if the request was successful
        if data["status"] != "OK":
            return {
                "success": False,
                "error": f"Distance Matrix request failed with status: {data['status']}"
            }
            
        return {
            "success": True,
            "results": data
        }
        
    except Exception as e:
        logging.error(f"Error getting distance matrix: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_place_details(place_id):
    """Get details about a place using its place_id"""
    try:
        if not MAPS_API_KEY:
            return {
                "success": False,
                "error": "Maps API key not available"
            }
            
        # Prepare the URL
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,rating,formatted_phone_number,formatted_address,opening_hours,website,geometry,types",
            "key": MAPS_API_KEY
        }
        
        # Make the request
        response = requests.get(url, params=params)
        
        # Process the response
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Place Details API returned status {response.status_code}"
            }
            
        data = response.json()
        
        # Check if the request was successful
        if data["status"] != "OK":
            return {
                "success": False,
                "error": f"Place Details request failed with status: {data['status']}"
            }
            
        return {
            "success": True,
            "details": data["result"]
        }
        
    except Exception as e:
        logging.error(f"Error getting place details: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def search_nearby_places(lat, lng, radius=1000, type=None, keyword=None):
    """Search for places near a location"""
    try:
        if not MAPS_API_KEY:
            return {
                "success": False,
                "error": "Maps API key not available"
            }
            
        # Prepare the URL
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "key": MAPS_API_KEY
        }
        
        # Add optional parameters
        if type:
            params["type"] = type
            
        if keyword:
            params["keyword"] = keyword
            
        # Make the request
        response = requests.get(url, params=params)
        
        # Process the response
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Nearby Search API returned status {response.status_code}"
            }
            
        data = response.json()
        
        # Check if the request was successful
        if data["status"] != "OK":
            return {
                "success": False,
                "error": f"Nearby Search request failed with status: {data['status']}"
            }
            
        return {
            "success": True,
            "places": data["results"]
        }
        
    except Exception as e:
        logging.error(f"Error searching nearby places: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def search_places(query, location=None, radius=None, type=None):
    """Search for places using text search"""
    try:
        if not MAPS_API_KEY:
            return {
                "success": False,
                "error": "Maps API key not available"
            }
            
        # Prepare the URL
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "key": MAPS_API_KEY
        }
        
        # Add optional parameters
        if location:
            if isinstance(location, str):
                params["location"] = location
            else:
                params["location"] = f"{location[0]},{location[1]}"
                
        if radius:
            params["radius"] = radius
            
        if type:
            params["type"] = type
            
        # Make the request
        response = requests.get(url, params=params)
        
        # Process the response
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Places Text Search API returned status {response.status_code}"
            }
            
        data = response.json()
        
        # Check if the request was successful
        if data["status"] != "OK":
            return {
                "success": False,
                "error": f"Places Text Search request failed with status: {data['status']}"
            }
            
        return {
            "success": True,
            "places": data["results"]
        }
        
    except Exception as e:
        logging.error(f"Error searching places: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_directions(origin, destination, mode="driving", waypoints=None, avoid=None):
    """Get directions between two locations"""
    try:
        if not MAPS_API_KEY:
            return {
                "success": False,
                "error": "Maps API key not available"
            }
            
        # Validate the mode
        valid_modes = ["driving", "walking", "bicycling", "transit"]
        if mode not in valid_modes:
            mode = "driving"
            
        # Prepare the URL
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": MAPS_API_KEY
        }
        
        # Add optional parameters
        if waypoints:
            if isinstance(waypoints, list):
                params["waypoints"] = "|".join(waypoints)
            else:
                params["waypoints"] = waypoints
                
        if avoid:
            params["avoid"] = avoid
            
        # Make the request
        response = requests.get(url, params=params)
        
        # Process the response
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Directions API returned status {response.status_code}"
            }
            
        data = response.json()
        
        # Check if the request was successful
        if data["status"] != "OK":
            return {
                "success": False,
                "error": f"Directions request failed with status: {data['status']}"
            }
            
        # Format the response
        routes = []
        for route in data["routes"]:
            formatted_route = {
                "summary": route["summary"],
                "duration": {
                    "text": route["legs"][0]["duration"]["text"],
                    "value": route["legs"][0]["duration"]["value"]
                },
                "distance": {
                    "text": route["legs"][0]["distance"]["text"],
                    "value": route["legs"][0]["distance"]["value"]
                },
                "steps": []
            }
            
            # Format the steps
            for step in route["legs"][0]["steps"]:
                formatted_step = {
                    "html_instructions": step["html_instructions"],
                    "distance": step["distance"]["text"],
                    "duration": step["duration"]["text"]
                }
                formatted_route["steps"].append(formatted_step)
                
            routes.append(formatted_route)
            
        return {
            "success": True,
            "routes": routes
        }
        
    except Exception as e:
        logging.error(f"Error getting directions: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_static_map_url(center, zoom=13, size="600x300", markers=None, path=None):
    """Generate a URL for a static map image"""
    try:
        if not MAPS_API_KEY:
            return {
                "success": False,
                "error": "Maps API key not available"
            }
            
        # Prepare the URL
        url = "https://maps.googleapis.com/maps/api/staticmap"
        params = {
            "center": center,
            "zoom": zoom,
            "size": size,
            "key": MAPS_API_KEY
        }
        
        # Add markers if provided
        if markers:
            if isinstance(markers, list):
                marker_strs = []
                for marker in markers:
                    if isinstance(marker, dict):
                        marker_str = ""
                        if "color" in marker:
                            marker_str += f"color:{marker['color']}|"
                        if "label" in marker:
                            marker_str += f"label:{marker['label']}|"
                        marker_str += marker["location"]
                        marker_strs.append(marker_str)
                    else:
                        marker_strs.append(marker)
                        
                for i, marker_str in enumerate(marker_strs):
                    params[f"markers{i}"] = marker_str
            else:
                params["markers"] = markers
                
        # Add path if provided
        if path:
            if isinstance(path, dict):
                path_str = ""
                if "color" in path:
                    path_str += f"color:{path['color']}|"
                if "weight" in path:
                    path_str += f"weight:{path['weight']}|"
                
                if "points" in path and isinstance(path["points"], list):
                    path_str += "|".join(path["points"])
                    
                params["path"] = path_str
            else:
                params["path"] = path
                
        # Build the full URL
        static_map_url = f"{url}?{urlencode(params)}"
        
        return {
            "success": True,
            "url": static_map_url
        }
        
    except Exception as e:
        logging.error(f"Error generating static map URL: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def find_nearby_places_by_type(lat, lng, type, radius=5000, limit=5):
    """Find nearby places of a specific type"""
    try:
        result = search_nearby_places(lat, lng, radius=radius, type=type)
        
        if not result["success"]:
            return result
            
        # Limit the number of results
        places = result["places"][:limit]
        
        # Format the places
        formatted_places = []
        for place in places:
            formatted_place = {
                "name": place["name"],
                "address": place.get("vicinity", ""),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"],
                "rating": place.get("rating", 0),
                "place_id": place["place_id"],
                "type": place.get("types", [])[0] if place.get("types") else ""
            }
            formatted_places.append(formatted_place)
            
        return {
            "success": True,
            "places": formatted_places
        }
        
    except Exception as e:
        logging.error(f"Error finding nearby places by type: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }