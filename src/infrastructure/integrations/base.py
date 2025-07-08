from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class IntegrationError(Exception):
    """Integration-specific error"""
    pass

class IntegrationBase(ABC):
    """Base class for all third-party integrations"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create session with retry logic and timeouts"""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504, 429]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the service"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if service is available"""
        pass
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        try:
            response = self.session.request(
                method,
                f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}",
                timeout=30,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Integration request failed: {e}")
            raise IntegrationError(str(e))

class AIServiceIntegration(IntegrationBase):
    """Base for AI service integrations"""
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count (override in subclasses)"""
        return len(text.split()) * 1.3  # Rough estimate
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate API cost (override in subclasses)"""
        return 0.0
