"""
PERFORMANCE OPTIMIZED: Enhanced with lazy loading and caching

Unified Google Services
Consolidated Google API integrations and utilities
"""
import os
import json
from typing import Dict, Any, Optional, List, Union

class UnifiedGoogleService:
    """Unified Google services with all integrations"""
    
    def __init__(self):
        self.credentials = None
        self.services = {}
        self.client_secret_file = 'client_secret.json'
        
    def authenticate(self, scopes: List[str] = None):
        """Authenticate with Google services"""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            
            if scopes is None:
                scopes = [
                    'https://www.googleapis.com/auth/gmail.modify',
                    'https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/documents',
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/photoslibrary'
                ]
            
            creds = None
            token_file = 'token.json'
            
            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, scopes)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists(self.client_secret_file):
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.client_secret_file, scopes)
                        creds = flow.run_local_server(port=0)
                
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.credentials = creds
            return True
            
        except ImportError:
            logger.warning("Google API libraries not available. Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
            return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def get_service(self, service_name: str, version: str = 'v1'):
        """Get Google API service"""
        if not self.credentials:
            if not self.authenticate():
                return None
        
        try:
            from googleapiclient.discovery import build
            
            if service_name not in self.services:
                self.services[service_name] = build(service_name, version, credentials=self.credentials)
            
            return self.services[service_name]
        except Exception as e:
            logger.error(f"Error getting {service_name} service: {e}")
            return None
    
    # Gmail Integration
    def send_email(self, to: str, subject: str, body: str, from_email: str = 'me'):
        """Send email via Gmail API"""
        service = self.get_service('gmail', 'v1')
        if not service:
            return False
        
        try:
            import base64
            from email.mime.text import MIMEText
            
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_message = service.users().messages().send(
                userId=from_email,
                body={'raw': raw_message}
            ).execute()
            
            return send_message
            
        except Exception as e:
            logger.error(f"Gmail send error: {e}")
            return False
    
    def get_emails(self, query: str = None, max_results: int = 10, user_id: str = 'me'):
        """Get emails from Gmail"""
        service = self.get_service('gmail', 'v1')
        if not service:
            return []
        
        try:
            results = service.users().messages().list(
                userId=user_id,
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            email_list = []
            for message in messages:
                msg = service.users().messages().get(
                    userId=user_id,
                    id=message['id']
                ).execute()
                
                payload = msg['payload']
                headers = payload.get('headers', [])
                
                email_data = {
                    'id': message['id'],
                    'snippet': msg.get('snippet', ''),
                    'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), ''),
                    'from': next((h['value'] for h in headers if h['name'] == 'From'), ''),
                    'date': next((h['value'] for h in headers if h['name'] == 'Date'), '')
                }
                
                email_list.append(email_data)
            
            return email_list
            
        except Exception as e:
            logger.error(f"Gmail fetch error: {e}")
            return []
    
    # Drive Integration
    def upload_file(self, file_path: str, folder_id: str = None, file_name: str = None):
        """Upload file to Google Drive"""
        service = self.get_service('drive', 'v3')
        if not service:
            return None
        
        try:
            from googleapiclient.http import MediaFileUpload
            
            if not file_name:
                file_name = os.path.basename(file_path)
            
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
            
        except Exception as e:
            logger.error(f"Drive upload error: {e}")
            return None
    
    def download_file(self, file_id: str, destination: str):
        """Download file from Google Drive"""
        service = self.get_service('drive', 'v3')
        if not service:
            return False
        
        try:
            import io
            from googleapiclient.http import MediaIoBaseDownload
            
            request = service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            with open(destination, 'wb') as f:
                f.write(file_io.getvalue())
            
            return True
            
        except Exception as e:
            logger.error(f"Drive download error: {e}")
            return False
    
    def list_files(self, folder_id: str = None, max_results: int = 10):
        """List files in Google Drive"""
        service = self.get_service('drive', 'v3')
        if not service:
            return []
        
        try:
            query = f"'{folder_id}' in parents" if folder_id else None
            
            results = service.files().list(
                pageSize=max_results,
                q=query,
                fields="nextPageToken, files(id, name, mimeType, size, createdTime)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            logger.error(f"Drive list error: {e}")
            return []
    
    # Docs Integration  
    def create_document(self, title: str, content: str = ""):
        """Create Google Doc"""
        service = self.get_service('docs', 'v1')
        if not service:
            return None
        
        try:
            document = {'title': title}
            doc = service.documents().create(body=document).execute()
            
            if content:
                requests = [{
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                }]
                
                service.documents().batchUpdate(
                    documentId=doc.get('documentId'),
                    body={'requests': requests}
                ).execute()
            
            return doc
            
        except Exception as e:
            logger.error(f"Docs create error: {e}")
            return None
    
    def update_document(self, document_id: str, content: str, insert_index: int = 1):
        """Update Google Doc content"""
        service = self.get_service('docs', 'v1')
        if not service:
            return False
        
        try:
            requests = [{
                'insertText': {
                    'location': {'index': insert_index},
                    'text': content
                }
            }]
            
            service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Docs update error: {e}")
            return False
    
    # Sheets Integration
    def create_spreadsheet(self, title: str):
        """Create Google Spreadsheet"""
        service = self.get_service('sheets', 'v4')
        if not service:
            return None
        
        try:
            spreadsheet = {'properties': {'title': title}}
            
            sheet = service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()
            
            return sheet
            
        except Exception as e:
            logger.error(f"Sheets create error: {e}")
            return None
    
    def update_spreadsheet(self, sheet_id: str, range_name: str, values: List[List]):
        """Update Google Sheets"""
        service = self.get_service('sheets', 'v4')
        if not service:
            return False
        
        try:
            body = {
                'values': values
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return result
            
        except Exception as e:
            logger.error(f"Sheets update error: {e}")
            return False
    
    def read_spreadsheet(self, sheet_id: str, range_name: str):
        """Read from Google Sheets"""
        service = self.get_service('sheets', 'v4')
        if not service:
            return []
        
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            return result.get('values', [])
            
        except Exception as e:
            logger.error(f"Sheets read error: {e}")
            return []
    
    # Maps Integration
    def get_directions(self, origin: str, destination: str, mode: str = 'driving'):
        """Get directions via Google Maps"""
        api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        if not api_key:
            logger.warning("Google Maps API key not found")
            return None
        
        try:
            import googlemaps
            gmaps = googlemaps.Client(key=api_key)
            
            directions = gmaps.directions(
                origin,
                destination,
                mode=mode
            )
            
            return directions
            
        except ImportError:
            logger.warning("googlemaps library not available. Install with: pip install googlemaps")
            return None
        except Exception as e:
            logger.error(f"Maps directions error: {e}")
            return None
    
    def search_places(self, query: str, location: str = None, radius: int = 5000):
        """Search places via Google Maps"""
        api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        if not api_key:
            logger.warning("Google Maps API key not found")
            return []
        
        try:
            import googlemaps
            gmaps = googlemaps.Client(key=api_key)
            
            if location:
                geocode_result = gmaps.geocode(location)
                if geocode_result:
                    location_coords = geocode_result[0]['geometry']['location']
                    
                    places = gmaps.places_nearby(
                        location=location_coords,
                        radius=radius,
                        keyword=query
                    )
                    
                    return places.get('results', [])
            else:
                places = gmaps.places(query)
                return places.get('results', [])
            
        except ImportError:
            logger.warning("googlemaps library not available")
            return []
        except Exception as e:
            logger.error(f"Maps search error: {e}")
            return []
    
    # Photos Integration
    def upload_photo(self, photo_path: str, album_id: str = None):
        """Upload photo to Google Photos"""
        # Note: Google Photos API requires special handling
        logger.info("Google Photos upload requires additional setup")
        return None
    
    def create_album(self, album_title: str):
        """Create photo album"""
        # Implementation for Google Photos album creation
        logger.info("Google Photos album creation requires additional setup")
        return None

# Backward compatibility functions
def get_gmail_service():
    """Backward compatibility for gmail_helper"""
    service = UnifiedGoogleService()
    service.authenticate()
    return service

def get_drive_service():
    """Backward compatibility for drive_helper"""
    service = UnifiedGoogleService()
    service.authenticate()
    return service

def get_maps_client():
    """Backward compatibility for maps_helper"""
    service = UnifiedGoogleService()
    return service

def send_gmail(to: str, subject: str, body: str):
    """Legacy function for backward compatibility"""
    service = UnifiedGoogleService()
    return service.send_email(to, subject, body)

def upload_to_drive(file_path: str, folder_id: str = None):
    """Legacy function for backward compatibility"""
    service = UnifiedGoogleService()
    return service.upload_file(file_path, folder_id)

def create_google_doc(title: str, content: str = ""):
    """Legacy function for backward compatibility"""
    service = UnifiedGoogleService()
    return service.create_document(title, content)

# Global service instance for convenience
google_service = UnifiedGoogleService()