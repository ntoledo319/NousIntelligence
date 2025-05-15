"""
Helper module for Google Photos integration
"""
import os
import logging
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import io
import base64
import requests
import json

def get_photos_service(user_connection):
    """Build and return a Google Photos service object from user connection data"""
    try:
        # Create credentials from stored tokens
        creds = Credentials(
            token=user_connection.token,
            refresh_token=user_connection.refresh_token,
            token_uri=user_connection.token_uri,
            client_id=user_connection.client_id,
            client_secret=user_connection.client_secret,
            scopes=user_connection.scopes.split(",") if user_connection.scopes else []
        )
        
        # Build the Photos service
        service = build('photoslibrary', 'v1', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error building Photos service: {str(e)}")
        return None

def list_albums(service, max_results=20):
    """List user's photo albums"""
    try:
        # Execute the request
        results = service.albums().list(pageSize=max_results).execute()
        albums = results.get('albums', [])
        
        # Format each album with useful information
        formatted_albums = []
        for album in albums:
            album_info = {
                'id': album.get('id'),
                'title': album.get('title'),
                'productUrl': album.get('productUrl'),
                'coverPhotoBaseUrl': album.get('coverPhotoBaseUrl'),
                'mediaItemsCount': album.get('mediaItemsCount')
            }
            formatted_albums.append(album_info)
            
        return formatted_albums
    except Exception as e:
        logging.error(f"Error listing photo albums: {str(e)}")
        return []

def get_album_contents(service, album_id, max_results=100):
    """Get photos and videos in an album"""
    try:
        # Prepare request body
        request_body = {
            'albumId': album_id,
            'pageSize': max_results
        }
        
        # Execute the request
        results = service.mediaItems().search(body=request_body).execute()
        items = results.get('mediaItems', [])
        
        # Format each media item with useful information
        formatted_items = []
        for item in items:
            item_info = {
                'id': item.get('id'),
                'productUrl': item.get('productUrl'),
                'baseUrl': item.get('baseUrl'),
                'mimeType': item.get('mimeType'),
                'mediaMetadata': item.get('mediaMetadata'),
                'filename': item.get('filename')
            }
            formatted_items.append(item_info)
            
        return formatted_items
    except Exception as e:
        logging.error(f"Error getting album contents: {str(e)}")
        return []

def search_media_items(service, search_criteria, max_results=100):
    """Search for media items based on criteria"""
    try:
        # Prepare the request body
        request_body = {
            'pageSize': max_results
        }
        
        # Add search criteria
        if 'filters' in search_criteria:
            request_body['filters'] = search_criteria['filters']
            
        # Execute the request
        results = service.mediaItems().search(body=request_body).execute()
        items = results.get('mediaItems', [])
        
        # Format each media item with useful information
        formatted_items = []
        for item in items:
            item_info = {
                'id': item.get('id'),
                'productUrl': item.get('productUrl'),
                'baseUrl': item.get('baseUrl'),
                'mimeType': item.get('mimeType'),
                'mediaMetadata': item.get('mediaMetadata'),
                'filename': item.get('filename')
            }
            formatted_items.append(item_info)
            
        return formatted_items
    except Exception as e:
        logging.error(f"Error searching media items: {str(e)}")
        return []

def create_album(service, title):
    """Create a new album"""
    try:
        # Prepare the request body
        request_body = {
            'album': {
                'title': title
            }
        }
        
        # Execute the request
        album = service.albums().create(body=request_body).execute()
        
        return {
            'id': album.get('id'),
            'title': album.get('title'),
            'productUrl': album.get('productUrl'),
            'isWriteable': album.get('isWriteable', False)
        }
    except Exception as e:
        logging.error(f"Error creating album: {str(e)}")
        return None

def get_recent_photos(service, max_results=20):
    """Get recently added photos"""
    try:
        # Prepare request body with date filter for recent items
        request_body = {
            'pageSize': max_results,
            'filters': {
                'mediaTypeFilter': {
                    'mediaTypes': ['PHOTO']
                }
            }
        }
        
        # Execute the request
        results = service.mediaItems().search(body=request_body).execute()
        items = results.get('mediaItems', [])
        
        # Format each media item with useful information
        formatted_items = []
        for item in items:
            item_info = {
                'id': item.get('id'),
                'productUrl': item.get('productUrl'),
                'baseUrl': item.get('baseUrl'),
                'mimeType': item.get('mimeType'),
                'mediaMetadata': item.get('mediaMetadata'),
                'filename': item.get('filename')
            }
            formatted_items.append(item_info)
            
        return formatted_items
    except Exception as e:
        logging.error(f"Error getting recent photos: {str(e)}")
        return []

def get_media_item(service, media_item_id):
    """Get a specific media item by ID"""
    try:
        # Execute the request
        item = service.mediaItems().get(mediaItemId=media_item_id).execute()
        
        return {
            'id': item.get('id'),
            'productUrl': item.get('productUrl'),
            'baseUrl': item.get('baseUrl'),
            'mimeType': item.get('mimeType'),
            'mediaMetadata': item.get('mediaMetadata'),
            'filename': item.get('filename')
        }
    except Exception as e:
        logging.error(f"Error getting media item: {str(e)}")
        return None

def download_photo(service, media_item_id, destination_path=None):
    """Download a photo by ID"""
    try:
        # Get the media item
        item = get_media_item(service, media_item_id)
        
        if not item:
            return {
                "success": False,
                "error": "Media item not found"
            }
            
        # Get the download URL - appending '=d' to the baseUrl
        download_url = item['baseUrl'] + '=d'
        
        # Download the photo
        response = requests.get(download_url)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Download failed with status code {response.status_code}"
            }
            
        # Set destination path if not provided
        if not destination_path:
            filename = item['filename'] or f"photo_{media_item_id}.jpg"
            destination_path = os.path.join('/tmp', filename)
            
        # Save the file
        with open(destination_path, 'wb') as f:
            f.write(response.content)
            
        return {
            "success": True,
            "path": destination_path,
            "filename": os.path.basename(destination_path),
            "media_item": item
        }
    except Exception as e:
        logging.error(f"Error downloading photo: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def analyze_photo_content(service, media_item_id, openai_client):
    """Analyze the content of a photo using AI"""
    try:
        # Get the media item
        item = get_media_item(service, media_item_id)
        
        if not item:
            return {
                "success": False,
                "error": "Media item not found"
            }
            
        # Get the image URL - use a size that's not too large but sufficient for analysis
        image_url = item['baseUrl'] + '=w800-h800'
        
        # Download the image
        response = requests.get(image_url)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Image download failed with status code {response.status_code}"
            }
            
        # Convert image to base64
        image_data = base64.b64encode(response.content).decode('utf-8')
        
        # Analyze the image using OpenAI
        if not openai_client:
            return {
                "success": False,
                "error": "OpenAI client not available"
            }
            
        try:
            # Analyze using OpenAI Vision
            response = openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this image in detail. Include information about people, objects, location, activities, and any notable elements. Also provide any insights that might be relevant."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            description = response.choices[0].message.content
            
            # Get additional AI analysis for categorization
            category_response = openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {
                        "role": "system",
                        "content": "You are an image categorization assistant. Provide categorical information for the image."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Categorize this image. Provide your response as a JSON object with the following keys: 'categories' (list of 1-3 category names), 'location_type' (indoor/outdoor/urban/nature), 'event_type' (if applicable), 'objects' (list of main objects), 'people_count' (approximate), 'season' (if detectable), 'time_of_day' (if detectable), 'mood' (e.g. happy, serious, etc.)"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            categorization = json.loads(category_response.choices[0].message.content)
            
            # Combine the results
            return {
                "success": True,
                "media_item": {
                    "id": item.get('id'),
                    "filename": item.get('filename'),
                    "productUrl": item.get('productUrl'),
                },
                "analysis": {
                    "description": description,
                    "categories": categorization.get("categories", []),
                    "location_type": categorization.get("location_type", ""),
                    "event_type": categorization.get("event_type", ""),
                    "objects": categorization.get("objects", []),
                    "people_count": categorization.get("people_count", 0),
                    "season": categorization.get("season", ""),
                    "time_of_day": categorization.get("time_of_day", ""),
                    "mood": categorization.get("mood", "")
                }
            }
            
        except Exception as e:
            logging.error(f"Error in AI analysis of image: {str(e)}")
            return {
                "success": False,
                "error": f"AI analysis failed: {str(e)}"
            }
            
    except Exception as e:
        logging.error(f"Error analyzing photo: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def search_photos_by_content(service, query, max_results=20, openai_client=None):
    """Search for photos matching a content description using AI analysis"""
    try:
        if not openai_client:
            return {
                "success": False,
                "error": "OpenAI client not available"
            }
            
        # First, get recent photos
        recent_photos = get_recent_photos(service, max_results=50)  # Get more to allow filtering
        
        if not recent_photos:
            return {
                "success": False,
                "error": "No recent photos found"
            }
            
        # Process photos in batches to avoid rate limiting
        matches = []
        batch_size = 5
        
        for i in range(0, min(len(recent_photos), 20), batch_size):
            batch = recent_photos[i:i+batch_size]
            
            for photo in batch:
                # Download a smaller version of the image
                image_url = photo['baseUrl'] + '=w400-h400'
                response = requests.get(image_url)
                
                if response.status_code != 200:
                    continue
                    
                # Convert image to base64
                image_data = base64.b64encode(response.content).decode('utf-8')
                
                # Check if image matches the query using OpenAI
                try:
                    match_response = openai_client.chat.completions.create(
                        model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                        messages=[
                            {
                                "role": "system",
                                "content": f"Determine if this image matches the user's search query: '{query}'. Respond with a JSON object with the following keys: 'matches' (boolean), 'match_confidence' (float 0-1), 'reason' (string explanation)"
                            },
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_data}"
                                        }
                                    }
                                ]
                            }
                        ],
                        response_format={"type": "json_object"}
                    )
                    
                    match_result = json.loads(match_response.choices[0].message.content)
                    
                    if match_result.get("matches", False) and match_result.get("match_confidence", 0) > 0.7:
                        # Add to matches
                        photo['match_confidence'] = match_result.get("match_confidence", 0)
                        photo['match_reason'] = match_result.get("reason", "")
                        matches.append(photo)
                        
                        # Stop once we've found enough matches
                        if len(matches) >= max_results:
                            break
                            
                except Exception as e:
                    logging.error(f"Error analyzing photo for search: {str(e)}")
                    continue
                    
            # Stop processing batches if we've found enough matches
            if len(matches) >= max_results:
                break
                
        # Sort matches by confidence
        matches.sort(key=lambda x: x.get('match_confidence', 0), reverse=True)
        
        return {
            "success": True,
            "query": query,
            "matches": matches
        }
        
    except Exception as e:
        logging.error(f"Error searching photos by content: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }