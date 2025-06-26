"""
Centralized Google API Services Manager
Provides unified access to all Google Services
"""
import os
import logging
from datetime import datetime
from google.oauth2.credentials import Credentials

# Import all service-specific helpers
from utils.gmail_helper import get_gmail_service, search_gmail, get_gmail_threads
from utils.drive_helper import get_drive_service, list_files, search_files, get_file_metadata
from utils.maps_helper import geocode_address, search_places, get_directions
from utils.photos_helper import get_photos_service, list_albums, get_recent_photos
from utils.docs_sheets_helper import (
    get_docs_service, get_sheets_service,
    create_document, create_spreadsheet,
    create_medication_tracker_spreadsheet,
    create_recovery_journal_document,
    create_budget_spreadsheet
)
from utils.youtube_helper import (
    get_youtube_service, search_videos,
    search_recovery_videos,
    create_recovery_playlist,
    search_guided_meditations
)

# Import AI analysis capabilities
from utils.ai_helper import generate_ai_text

def get_user_connection(user_id):
    """Get user Google connection info by user ID

    Args:
        user_id: The user ID to get connection for

    Returns:
        User connection object or None if not found
    """
    # This is a placeholder - needs to be implemented with actual DB logic
    return None

class GoogleApiManager:
    """Centralized manager for all Google API services"""

    def __init__(self, user_connection=None):
        """Initialize the API manager with user OAuth credentials"""
        self.user_connection = user_connection
        self.credentials = None
        self.services = {}

        # Initialize credentials if connection is provided
        if user_connection:
            self._initialize_credentials()

    def _initialize_credentials(self):
        """Initialize Google API credentials from user connection data"""
        try:
            # Create credentials from stored tokens
            self.credentials = Credentials(
                token=self.user_connection.token,
                refresh_token=self.user_connection.refresh_token,
                token_uri=self.user_connection.token_uri,
                client_id=self.user_connection.client_id,
                client_secret=self.user_connection.client_secret,
                scopes=self.user_connection.scopes.split(",") if self.user_connection.scopes else []
            )
            return True
        except Exception as e:
            logging.error(f"Error initializing Google credentials: {str(e)}")
            self.credentials = None
            return False

    def get_service(self, service_name):
        """
        Get a Google service by name

        Args:
            service_name: Name of the service ('gmail', 'drive', 'maps', 'photos', 'docs', 'sheets', 'youtube')

        Returns:
            Service object or None if service is not available
        """
        # Return from cache if already initialized
        if service_name in self.services:
            return self.services[service_name]

        # Check if credentials are available
        if not self.credentials and not self._initialize_credentials():
            logging.error(f"Cannot get {service_name} service: No valid credentials")
            return None

        # Initialize the requested service
        service = None

        try:
            if service_name == 'gmail':
                service = get_gmail_service(self.user_connection)
            elif service_name == 'drive':
                service = get_drive_service(self.user_connection)
            elif service_name == 'photos':
                service = get_photos_service(self.user_connection)
            elif service_name == 'docs':
                service = get_docs_service(self.user_connection)
            elif service_name == 'sheets':
                service = get_sheets_service(self.user_connection)
            elif service_name == 'youtube':
                service = get_youtube_service(self.user_connection)
            else:
                logging.error(f"Unknown service name: {service_name}")
                return None

            # Cache the service
            if service:
                self.services[service_name] = service

            return service

        except Exception as e:
            logging.error(f"Error getting {service_name} service: {str(e)}")
            return None

    # Gmail Helper Functions
    def search_emails(self, query, max_results=20):
        """Search Gmail with a specific query"""
        gmail = self.get_service('gmail')
        if not gmail:
            return {"error": "Gmail service not available"}

        return search_gmail(gmail, query, max_results)

    def get_email_threads(self, query="", max_results=10, include_content=True):
        """Get Gmail threads based on a query"""
        gmail = self.get_service('gmail')
        if not gmail:
            return {"error": "Gmail service not available"}

        return get_gmail_threads(gmail, query, max_results, include_content)

    def analyze_email(self, email_content, openai_client=None):
        """Analyze email content using AI"""
        if not openai_client:
            return {"error": "OpenAI client not available"}

        user_id = self.user_connection.user_id if self.user_connection else 'anonymous'
        return analyze_gmail_content(user_id, email_content, openai_client)

    # Drive Helper Functions
    def list_drive_files(self, query=None, max_results=20):
        """List files in Google Drive"""
        drive = self.get_service('drive')
        if not drive:
            return {"error": "Drive service not available"}

        return list_files(drive, query, max_results)

    def search_drive(self, query_text, file_type=None, max_results=20):
        """Search for files in Google Drive by name or content"""
        drive = self.get_service('drive')
        if not drive:
            return {"error": "Drive service not available"}

        return search_files(drive, query_text, file_type, max_results)

    # Maps Helper Functions
    def geocode(self, address):
        """Convert address to geographical coordinates"""
        # Pass the API key from Google credentials if available
        api_key = None
        if self.credentials:
            api_key = self.credentials.token
            os.environ["MAPS_API_KEY"] = api_key
        return geocode_address(address)

    def search_places_nearby(self, query, location=None, radius=None):
        """Search for places using text search"""
        # Pass the API key from Google credentials if available
        api_key = None
        if self.credentials:
            api_key = self.credentials.token
            os.environ["MAPS_API_KEY"] = api_key
        return search_places(query, location, radius)

    def get_travel_directions(self, origin, destination, mode="driving"):
        """Get directions between two locations"""
        # Pass the API key from Google credentials if available
        api_key = None
        if self.credentials:
            api_key = self.credentials.token
            os.environ["MAPS_API_KEY"] = api_key
        return get_directions(origin, destination, mode)

    # Photos Helper Functions
    def get_photo_albums(self, max_results=20):
        """List user's photo albums"""
        photos = self.get_service('photos')
        if not photos:
            return {"error": "Photos service not available"}

        return list_albums(photos, max_results)

    def get_recent_images(self, max_results=20):
        """Get recently added photos"""
        photos = self.get_service('photos')
        if not photos:
            return {"error": "Photos service not available"}

        return get_recent_photos(photos, max_results)

    # Docs & Sheets Helper Functions
    def create_new_document(self, title, content=None):
        """Create a new Google Doc"""
        docs = self.get_service('docs')
        drive = self.get_service('drive')
        if not docs or not drive:
            return {"error": "Docs or Drive service not available"}

        return create_document(docs, drive, title, content)

    def create_new_spreadsheet(self, title, sheets=None):
        """Create a new Google Sheet"""
        sheets_service = self.get_service('sheets')
        drive = self.get_service('drive')
        if not sheets_service or not drive:
            return {"error": "Sheets or Drive service not available"}

        return create_spreadsheet(sheets_service, drive, title, sheets)

    def create_med_tracker(self, title="Medication Tracker"):
        """Create a medication tracker spreadsheet"""
        sheets_service = self.get_service('sheets')
        drive = self.get_service('drive')
        if not sheets_service or not drive:
            return {"error": "Sheets or Drive service not available"}

        return create_medication_tracker_spreadsheet(sheets_service, drive, title)

    def create_recovery_journal(self, title="Recovery Journal"):
        """Create a recovery journal document"""
        docs = self.get_service('docs')
        drive = self.get_service('drive')
        if not docs or not drive:
            return {"error": "Docs or Drive service not available"}

        return create_recovery_journal_document(docs, drive, title)

    def create_budget_tracker(self, title="Budget Tracker"):
        """Create a budget tracking spreadsheet"""
        sheets_service = self.get_service('sheets')
        drive = self.get_service('drive')
        if not sheets_service or not drive:
            return {"error": "Sheets or Drive service not available"}

        return create_budget_spreadsheet(sheets_service, drive, title)

    def create_travel_planner(self, title="Travel Planning"):
        """Create a travel planning document"""
        docs = self.get_service('docs')
        drive = self.get_service('drive')
        if not docs or not drive:
            return {"error": "Docs or Drive service not available"}

        return create_travel_planning_document(docs, drive, title)

    # YouTube Helper Functions
    def search_youtube(self, query, max_results=10):
        """Search for videos on YouTube"""
        youtube = self.get_service('youtube')
        if not youtube:
            return {"error": "YouTube service not available"}

        return search_videos(youtube, query, max_results)

    def find_recovery_videos(self, max_results=10):
        """Find AA recovery-related videos"""
        youtube = self.get_service('youtube')
        if not youtube:
            return {"error": "YouTube service not available"}

        return search_recovery_videos(youtube, max_results)

    def create_youtube_recovery_playlist(self):
        """Create a playlist with recovery-related videos"""
        youtube = self.get_service('youtube')
        if not youtube:
            return {"error": "YouTube service not available"}

        return create_recovery_playlist(youtube)

    def find_meditation_videos(self, duration_min=None, duration_max=None, max_results=10):
        """Find guided meditation videos"""
        youtube = self.get_service('youtube')
        if not youtube:
            return {"error": "YouTube service not available"}

        return search_guided_meditations(youtube, duration_min, duration_max, max_results)

    # General Helper Functions
    def create_aa_resource_collection(self):
        """Create a comprehensive collection of AA recovery resources across Google services"""
        try:
            resources = {
                "docs": None,
                "spreadsheet": None,
                "playlist": None,
                "success": False
            }

            # Create recovery journal
            journal_result = self.create_recovery_journal("My Recovery Journey")
            if journal_result and journal_result.get("success", False):
                resources["docs"] = journal_result

            # Create medication and sobriety tracker
            tracker_result = self.create_med_tracker("Recovery & Medication Tracker")
            if tracker_result and tracker_result.get("success", False):
                resources["spreadsheet"] = tracker_result

            # Create YouTube recovery playlist
            playlist_result = self.create_youtube_recovery_playlist()
            if playlist_result:
                resources["playlist"] = playlist_result

            # Set success flag if at least one resource was created
            if resources["docs"] or resources["spreadsheet"] or resources["playlist"]:
                resources["success"] = True

            return resources
        except Exception as e:
            logging.error(f"Error creating AA resource collection: {str(e)}")
            return {"error": str(e), "success": False}

    def create_full_travel_package(self, destination):
        """Create a comprehensive travel planning package across Google services"""
        try:
            package = {
                "docs": None,
                "maps": None,
                "playlist": None,
                "success": False
            }

            # Create travel planning document
            travel_doc = self.create_travel_planner(f"Trip to {destination}")
            if travel_doc and travel_doc.get("success", False):
                package["docs"] = travel_doc

            # Get map directions and places
            map_info = {}
            geocode_result = self.geocode(destination)
            if geocode_result and geocode_result.get("success", False):
                map_info["location"] = geocode_result

                # Search for interesting places
                places_result = self.search_places_nearby(f"tourist attractions in {destination}")
                if places_result and places_result.get("success", False):
                    map_info["places"] = places_result

                package["maps"] = map_info

            # Create YouTube travel-themed playlist
            youtube = self.get_service('youtube')
            if youtube:
                from utils.youtube_helper import create_topical_playlist
                playlist_result = create_topical_playlist(
                    youtube,
                    f"Travel to {destination}",
                    f"Videos to inspire and prepare for a trip to {destination}"
                )
                if playlist_result:
                    package["playlist"] = playlist_result

            # Set success flag if at least one resource was created
            if package["docs"] or package["maps"] or package["playlist"]:
                package["success"] = True

            return package
        except Exception as e:
            logging.error(f"Error creating travel package: {str(e)}")
            return {"error": str(e), "success": False}