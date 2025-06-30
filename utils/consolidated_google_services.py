"""
Consolidated Google Services Helper
Combines Google Tasks, Drive, Docs/Sheets, Maps, Photos, and Meet functionality
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ConsolidatedGoogleServices:
    """Unified Google Services interface combining all Google integrations"""
    
    def __init__(self):
        self.services = {}
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all Google services with fallback handling"""
        try:
            # Initialize each service component with graceful fallbacks
            self.services['tasks'] = self._init_tasks_service()
            self.services['drive'] = self._init_drive_service()
            self.services['docs'] = self._init_docs_service()
            self.services['maps'] = self._init_maps_service()
            self.services['photos'] = self._init_photos_service()
            self.services['meet'] = self._init_meet_service()
        except Exception as e:
            logger.warning(f"Google services initialization warning: {e}")
    
    # Google Tasks functionality
    def _init_tasks_service(self):
        """Initialize Google Tasks service"""
        try:
            from utils.google_tasks_helper import GoogleTasksHelper
            return GoogleTasksHelper()
        except ImportError:
            logger.warning("Google Tasks helper not available, using fallback")
            return self._create_fallback_service('tasks')
    
    def create_task(self, title: str, description: str = "", due_date: str = None) -> Dict[str, Any]:
        """Create a new Google Task"""
        if 'tasks' in self.services:
            try:
                return self.services['tasks'].create_task(title, description, due_date)
            except Exception as e:
                logger.error(f"Task creation failed: {e}")
        
        return {'success': False, 'error': 'Tasks service not available'}
    
    def list_tasks(self, task_list_id: str = None) -> Dict[str, Any]:
        """List Google Tasks"""
        if 'tasks' in self.services:
            try:
                return self.services['tasks'].list_tasks(task_list_id)
            except Exception as e:
                logger.error(f"Task listing failed: {e}")
        
        return {'success': False, 'tasks': [], 'error': 'Tasks service not available'}
    
    # Google Drive functionality
    def _init_drive_service(self):
        """Initialize Google Drive service"""
        try:
            from utils.drive_helper import DriveHelper
            return DriveHelper()
        except ImportError:
            logger.warning("Drive helper not available, using fallback")
            return self._create_fallback_service('drive')
    
    def upload_file(self, file_path: str, folder_id: str = None) -> Dict[str, Any]:
        """Upload file to Google Drive"""
        if 'drive' in self.services:
            try:
                return self.services['drive'].upload_file(file_path, folder_id)
            except Exception as e:
                logger.error(f"File upload failed: {e}")
        
        return {'success': False, 'error': 'Drive service not available'}
    
    def list_files(self, folder_id: str = None, query: str = None) -> Dict[str, Any]:
        """List files in Google Drive"""
        if 'drive' in self.services:
            try:
                return self.services['drive'].list_files(folder_id, query)
            except Exception as e:
                logger.error(f"File listing failed: {e}")
        
        return {'success': False, 'files': [], 'error': 'Drive service not available'}
    
    # Google Docs/Sheets functionality
    def _init_docs_service(self):
        """Initialize Google Docs/Sheets service"""
        try:
            from utils.docs_sheets_helper import DocsHelper
            return DocsHelper()
        except ImportError:
            logger.warning("Docs/Sheets helper not available, using fallback")
            return self._create_fallback_service('docs')
    
    def create_document(self, title: str, content: str = "") -> Dict[str, Any]:
        """Create a new Google Document"""
        if 'docs' in self.services:
            try:
                return self.services['docs'].create_document(title, content)
            except Exception as e:
                logger.error(f"Document creation failed: {e}")
        
        return {'success': False, 'error': 'Docs service not available'}
    
    def create_spreadsheet(self, title: str, data: List[List[str]] = None) -> Dict[str, Any]:
        """Create a new Google Spreadsheet"""
        if 'docs' in self.services:
            try:
                return self.services['docs'].create_spreadsheet(title, data)
            except Exception as e:
                logger.error(f"Spreadsheet creation failed: {e}")
        
        return {'success': False, 'error': 'Docs service not available'}
    
    # Google Maps functionality
    def _init_maps_service(self):
        """Initialize Google Maps service"""
        try:
            from utils.maps_helper import MapsHelper
            return MapsHelper()
        except ImportError:
            logger.warning("Maps helper not available, using fallback")
            return self._create_fallback_service('maps')
    
    def get_directions(self, origin: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
        """Get directions between two locations"""
        if 'maps' in self.services:
            try:
                return self.services['maps'].get_directions(origin, destination, mode)
            except Exception as e:
                logger.error(f"Directions request failed: {e}")
        
        return {'success': False, 'error': 'Maps service not available'}
    
    def search_places(self, query: str, location: str = None) -> Dict[str, Any]:
        """Search for places using Google Maps"""
        if 'maps' in self.services:
            try:
                return self.services['maps'].search_places(query, location)
            except Exception as e:
                logger.error(f"Places search failed: {e}")
        
        return {'success': False, 'places': [], 'error': 'Maps service not available'}
    
    # Google Photos functionality
    def _init_photos_service(self):
        """Initialize Google Photos service"""
        try:
            from utils.photos_helper import PhotosHelper
            return PhotosHelper()
        except ImportError:
            logger.warning("Photos helper not available, using fallback")
            return self._create_fallback_service('photos')
    
    def upload_photo(self, file_path: str, album_id: str = None) -> Dict[str, Any]:
        """Upload photo to Google Photos"""
        if 'photos' in self.services:
            try:
                return self.services['photos'].upload_photo(file_path, album_id)
            except Exception as e:
                logger.error(f"Photo upload failed: {e}")
        
        return {'success': False, 'error': 'Photos service not available'}
    
    def list_albums(self) -> Dict[str, Any]:
        """List Google Photos albums"""
        if 'photos' in self.services:
            try:
                return self.services['photos'].list_albums()
            except Exception as e:
                logger.error(f"Albums listing failed: {e}")
        
        return {'success': False, 'albums': [], 'error': 'Photos service not available'}
    
    # Google Meet functionality
    def _init_meet_service(self):
        """Initialize Google Meet service"""
        try:
            from utils.meet_helper import MeetHelper
            return MeetHelper()
        except ImportError:
            logger.warning("Meet helper not available, using fallback")
            return self._create_fallback_service('meet')
    
    def create_meeting(self, title: str, start_time: str, duration: int = 60) -> Dict[str, Any]:
        """Create a Google Meet meeting"""
        if 'meet' in self.services:
            try:
                return self.services['meet'].create_meeting(title, start_time, duration)
            except Exception as e:
                logger.error(f"Meeting creation failed: {e}")
        
        return {'success': False, 'error': 'Meet service not available'}
    
    def _create_fallback_service(self, service_name: str):
        """Create a fallback service object"""
        class FallbackService:
            def __init__(self, name):
                self.name = name
            
            def __getattr__(self, method_name):
                def fallback_method(*args, **kwargs):
                    return {
                        'success': False,
                        'error': f'{self.name.title()} service not available',
                        'fallback': True
                    }
                return fallback_method
        
        return FallbackService(service_name)
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all Google services"""
        health_status = {}
        
        for service_name, service in self.services.items():
            try:
                # Try a simple operation to check service health
                if hasattr(service, 'health_check'):
                    health_status[service_name] = service.health_check()
                else:
                    health_status[service_name] = {'status': 'available', 'service': service_name}
            except Exception as e:
                health_status[service_name] = {'status': 'error', 'error': str(e)}
        
        return {
            'overall_status': 'healthy' if all(s.get('status') != 'error' for s in health_status.values()) else 'degraded',
            'services': health_status
        }

# Global instance
_google_services = None

def get_google_services() -> ConsolidatedGoogleServices:
    """Get the global Google services instance"""
    global _google_services
    if _google_services is None:
        _google_services = ConsolidatedGoogleServices()
    return _google_services

# Backward compatibility functions
def create_task(title: str, description: str = "", due_date: str = None) -> Dict[str, Any]:
    """Backward compatibility for Google Tasks"""
    return get_google_services().create_task(title, description, due_date)

def upload_file(file_path: str, folder_id: str = None) -> Dict[str, Any]:
    """Backward compatibility for Google Drive"""
    return get_google_services().upload_file(file_path, folder_id)

def get_directions(origin: str, destination: str, mode: str = "driving") -> Dict[str, Any]:
    """Backward compatibility for Google Maps"""
    return get_google_services().get_directions(origin, destination, mode)

def create_meeting(title: str, start_time: str, duration: int = 60) -> Dict[str, Any]:
    """Backward compatibility for Google Meet"""
    return get_google_services().create_meeting(title, start_time, duration)