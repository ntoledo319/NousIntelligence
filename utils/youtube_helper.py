"""
Helper module for YouTube API integration
"""
import os
import logging
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import json

def get_youtube_service(user_connection):
    """Build and return a YouTube service object from user connection data"""
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
        
        # Build the YouTube service
        service = build('youtube', 'v3', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error building YouTube service: {str(e)}")
        return None

def search_videos(service, query, max_results=10, category=None):
    """Search for videos by keyword and category"""
    try:
        # Prepare the request
        request_params = {
            'part': 'snippet',
            'maxResults': max_results,
            'q': query,
            'type': 'video'
        }
        
        # Add category filter if provided
        if category:
            request_params['videoCategoryId'] = category
            
        # Execute the search
        search_response = service.search().list(**request_params).execute()
        
        # Extract video information
        videos = []
        for item in search_response.get('items', []):
            video_info = {
                'id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'channelTitle': item['snippet']['channelTitle'],
                'publishedAt': item['snippet']['publishedAt'],
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            videos.append(video_info)
            
        return videos
    except Exception as e:
        logging.error(f"Error searching YouTube videos: {str(e)}")
        return []

def get_video_details(service, video_id):
    """Get detailed information about a video"""
    try:
        # Get video details
        video_response = service.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute()
        
        # Check if video found
        if not video_response.get('items'):
            return None
            
        video = video_response['items'][0]
        
        # Format video details
        video_details = {
            'id': video['id'],
            'title': video['snippet']['title'],
            'description': video['snippet']['description'],
            'publishedAt': video['snippet']['publishedAt'],
            'channelTitle': video['snippet']['channelTitle'],
            'channelId': video['snippet']['channelId'],
            'thumbnails': video['snippet']['thumbnails'],
            'tags': video['snippet'].get('tags', []),
            'duration': video['contentDetails']['duration'],
            'viewCount': video['statistics'].get('viewCount', '0'),
            'likeCount': video['statistics'].get('likeCount', '0'),
            'commentCount': video['statistics'].get('commentCount', '0'),
            'url': f"https://www.youtube.com/watch?v={video['id']}"
        }
        
        return video_details
    except Exception as e:
        logging.error(f"Error getting video details: {str(e)}")
        return None

def get_channel_info(service, channel_id):
    """Get information about a YouTube channel"""
    try:
        # Get channel details
        channel_response = service.channels().list(
            part='snippet,contentDetails,statistics',
            id=channel_id
        ).execute()
        
        # Check if channel found
        if not channel_response.get('items'):
            return None
            
        channel = channel_response['items'][0]
        
        # Format channel details
        channel_info = {
            'id': channel['id'],
            'title': channel['snippet']['title'],
            'description': channel['snippet']['description'],
            'thumbnails': channel['snippet']['thumbnails'],
            'publishedAt': channel['snippet']['publishedAt'],
            'customUrl': channel['snippet'].get('customUrl', ''),
            'subscriberCount': channel['statistics'].get('subscriberCount', '0'),
            'videoCount': channel['statistics'].get('videoCount', '0'),
            'viewCount': channel['statistics'].get('viewCount', '0'),
            'uploadsPlaylistId': channel['contentDetails']['relatedPlaylists']['uploads'],
            'url': f"https://www.youtube.com/channel/{channel['id']}"
        }
        
        return channel_info
    except Exception as e:
        logging.error(f"Error getting channel info: {str(e)}")
        return None

def get_channel_videos(service, channel_id, max_results=20):
    """Get videos from a channel"""
    try:
        # First, get the uploads playlist ID
        channel_response = service.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()
        
        # Check if channel found
        if not channel_response.get('items'):
            return []
            
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get playlist items
        playlist_items_response = service.playlistItems().list(
            part='snippet',
            maxResults=max_results,
            playlistId=uploads_playlist_id
        ).execute()
        
        # Extract video information
        videos = []
        for item in playlist_items_response.get('items', []):
            video_info = {
                'id': item['snippet']['resourceId']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails'].get('high', {}).get('url', ''),
                'publishedAt': item['snippet']['publishedAt'],
                'url': f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
            }
            videos.append(video_info)
            
        return videos
    except Exception as e:
        logging.error(f"Error getting channel videos: {str(e)}")
        return []

def get_recommended_videos(service, video_id, max_results=10):
    """Get videos related to a specific video"""
    try:
        # Search for related videos
        search_response = service.search().list(
            part='snippet',
            maxResults=max_results,
            relatedToVideoId=video_id,
            type='video'
        ).execute()
        
        # Extract video information
        videos = []
        for item in search_response.get('items', []):
            video_info = {
                'id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'channelTitle': item['snippet']['channelTitle'],
                'publishedAt': item['snippet']['publishedAt'],
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            videos.append(video_info)
            
        return videos
    except Exception as e:
        logging.error(f"Error getting recommended videos: {str(e)}")
        return []

def get_playlists(service, user_id='mine', max_results=25):
    """Get playlists created by the authenticated user"""
    try:
        # Get user playlists
        playlists_response = service.playlists().list(
            part='snippet,contentDetails',
            maxResults=max_results,
            mine=(user_id == 'mine')
        ).execute()
        
        # Extract playlist information
        playlists = []
        for item in playlists_response.get('items', []):
            playlist_info = {
                'id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails'].get('high', {}).get('url', ''),
                'channelTitle': item['snippet']['channelTitle'],
                'itemCount': item['contentDetails']['itemCount'],
                'url': f"https://www.youtube.com/playlist?list={item['id']}"
            }
            playlists.append(playlist_info)
            
        return playlists
    except Exception as e:
        logging.error(f"Error getting playlists: {str(e)}")
        return []

def get_playlist_items(service, playlist_id, max_results=50):
    """Get videos in a playlist"""
    try:
        # Get playlist items
        playlist_items_response = service.playlistItems().list(
            part='snippet',
            maxResults=max_results,
            playlistId=playlist_id
        ).execute()
        
        # Extract video information
        videos = []
        for item in playlist_items_response.get('items', []):
            video_info = {
                'id': item['snippet']['resourceId']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'position': item['snippet']['position'],
                'thumbnail': item['snippet']['thumbnails'].get('high', {}).get('url', ''),
                'channelTitle': item['snippet']['channelTitle'],
                'publishedAt': item['snippet']['publishedAt'],
                'url': f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
            }
            videos.append(video_info)
            
        return videos
    except Exception as e:
        logging.error(f"Error getting playlist items: {str(e)}")
        return []

def create_playlist(service, title, description='', privacy_status='private'):
    """Create a new playlist"""
    try:
        # Create playlist
        playlist_response = service.playlists().insert(
            part='snippet,status',
            body={
                'snippet': {
                    'title': title,
                    'description': description
                },
                'status': {
                    'privacyStatus': privacy_status
                }
            }
        ).execute()
        
        # Format playlist information
        playlist_info = {
            'id': playlist_response['id'],
            'title': playlist_response['snippet']['title'],
            'description': playlist_response['snippet']['description'],
            'privacy_status': playlist_response['status']['privacyStatus'],
            'url': f"https://www.youtube.com/playlist?list={playlist_response['id']}"
        }
        
        return playlist_info
    except Exception as e:
        logging.error(f"Error creating playlist: {str(e)}")
        return None

def add_video_to_playlist(service, playlist_id, video_id):
    """Add a video to a playlist"""
    try:
        # Add video to playlist
        playlist_item_response = service.playlistItems().insert(
            part='snippet',
            body={
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
        ).execute()
        
        return {
            'id': playlist_item_response['id'],
            'video_id': playlist_item_response['snippet']['resourceId']['videoId'],
            'playlist_id': playlist_item_response['snippet']['playlistId'],
            'position': playlist_item_response['snippet']['position']
        }
    except Exception as e:
        logging.error(f"Error adding video to playlist: {str(e)}")
        return None

def search_recovery_videos(service, max_results=10):
    """Search for AA recovery-related videos"""
    try:
        # Search for videos with relevant keywords
        keywords = [
            'AA recovery',
            'Alcoholics Anonymous',
            'sobriety journey',
            'recovery inspiration',
            '12 steps program',
            'addiction recovery',
            'AA speaker'
        ]
        
        # Try different keywords
        all_videos = []
        for keyword in keywords:
            videos = search_videos(service, keyword, max_results=3)
            all_videos.extend(videos)
            
            # Stop if we have enough videos
            if len(all_videos) >= max_results:
                break
                
        # Return only the requested number of videos
        return all_videos[:max_results]
    except Exception as e:
        logging.error(f"Error searching recovery videos: {str(e)}")
        return []

def create_recovery_playlist(service, title="My Recovery Journey", description="Videos to support my recovery"):
    """Create a playlist with recovery-related videos"""
    try:
        # Create the playlist
        playlist = create_playlist(service, title, description)
        
        if not playlist:
            return None
            
        # Search for recovery videos
        recovery_videos = search_recovery_videos(service, max_results=10)
        
        # Add videos to the playlist
        added_videos = []
        for video in recovery_videos:
            result = add_video_to_playlist(service, playlist['id'], video['id'])
            if result:
                added_videos.append(video)
                
        return {
            'playlist': playlist,
            'videos': added_videos
        }
    except Exception as e:
        logging.error(f"Error creating recovery playlist: {str(e)}")
        return None

def search_guided_meditations(service, duration_min=None, duration_max=None, max_results=10):
    """Search for guided meditation videos with optional duration filters"""
    try:
        # Search for meditation videos
        meditation_videos = search_videos(service, "guided meditation for recovery", max_results=20)
        
        # If duration filters are provided, get more details and filter
        if duration_min is not None or duration_max is not None:
            filtered_videos = []
            
            for video in meditation_videos:
                details = get_video_details(service, video['id'])
                
                if details:
                    # Parse the duration string (ISO 8601 format)
                    duration_str = details['duration']
                    
                    # Extract minutes from the duration string
                    import re
                    minutes = 0
                    minutes_match = re.search(r'(\d+)M', duration_str)
                    if minutes_match:
                        minutes = int(minutes_match.group(1))
                        
                    # Extract hours from the duration string
                    hours = 0
                    hours_match = re.search(r'(\d+)H', duration_str)
                    if hours_match:
                        hours = int(hours_match.group(1))
                        
                    # Calculate total minutes
                    total_minutes = hours * 60 + minutes
                    
                    # Apply filters
                    if duration_min is not None and total_minutes < duration_min:
                        continue
                        
                    if duration_max is not None and total_minutes > duration_max:
                        continue
                        
                    # Add duration information to the video
                    video['duration_minutes'] = total_minutes
                    filtered_videos.append(video)
                    
                    # Stop if we have enough videos
                    if len(filtered_videos) >= max_results:
                        break
                        
            return filtered_videos[:max_results]
        else:
            # If no duration filters, just return the first max_results videos
            return meditation_videos[:max_results]
    except Exception as e:
        logging.error(f"Error searching guided meditations: {str(e)}")
        return []

def analyze_video_content(service, video_id, openai_client=None):
    """Analyze the content and comments of a video using AI"""
    try:
        # Get video details
        video_details = get_video_details(service, video_id)
        
        if not video_details:
            return {
                "success": False,
                "error": "Video not found"
            }
            
        # Get video comments
        comments = get_video_comments(service, video_id, max_results=10)
        
        # If OpenAI client is not available, just return the data
        if not openai_client:
            return {
                "success": True,
                "video": video_details,
                "comments": comments
            }
            
        # Prepare content for analysis
        video_data = {
            "title": video_details['title'],
            "description": video_details['description'],
            "tags": video_details.get('tags', []),
            "comments": [comment['text'] for comment in comments]
        }
        
        data_str = json.dumps(video_data, indent=2)
        
        try:
            # Analyze using OpenAI
            response = openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {
                        "role": "system",
                        "content": "You are a video content analyst. Analyze the video information and viewer comments provided."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this YouTube video's content including title, description, tags, and user comments. Provide insights on theme, sentiment, audience reaction, relevance to recovery topics, and overall helpfulness. Format your response as JSON."
                    },
                    {
                        "role": "user",
                        "content": data_str
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "video": video_details,
                "comments": comments,
                "analysis": analysis
            }
        except Exception as e:
            logging.error(f"Error in AI analysis of video: {str(e)}")
            return {
                "success": False,
                "error": f"AI analysis failed: {str(e)}"
            }
            
    except Exception as e:
        logging.error(f"Error analyzing video content: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_video_comments(service, video_id, max_results=20):
    """Get comments for a video"""
    try:
        # Get comments
        comments_response = service.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_results,
            order='relevance'
        ).execute()
        
        # Extract comment information
        comments = []
        for item in comments_response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']
            comment_info = {
                'id': item['id'],
                'text': comment['textDisplay'],
                'author': comment['authorDisplayName'],
                'authorProfileImageUrl': comment['authorProfileImageUrl'],
                'authorChannelUrl': comment['authorChannelUrl'],
                'likeCount': comment['likeCount'],
                'publishedAt': comment['publishedAt']
            }
            comments.append(comment_info)
            
        return comments
    except Exception as e:
        logging.error(f"Error getting video comments: {str(e)}")
        return []

def create_topical_playlist(service, topic, description=None, max_videos=10):
    """Create a playlist based on a specific topic"""
    try:
        # Create playlist title and description
        title = f"{topic} - Curated Playlist"
        if not description:
            description = f"A collection of videos about {topic}"
            
        # Create the playlist
        playlist = create_playlist(service, title, description)
        
        if not playlist:
            return None
            
        # Search for videos on the topic
        videos = search_videos(service, topic, max_results=max_videos)
        
        # Add videos to the playlist
        added_videos = []
        for video in videos:
            result = add_video_to_playlist(service, playlist['id'], video['id'])
            if result:
                added_videos.append(video)
                
        return {
            'playlist': playlist,
            'videos': added_videos
        }
    except Exception as e:
        logging.error(f"Error creating topical playlist: {str(e)}")
        return None