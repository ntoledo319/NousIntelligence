"""
Production Performance Optimizer
Fixes Issues 39-41: Caching strategy, CDN configuration, asset optimization
"""

import os
import gzip
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from flask import Response, request, current_app
import hashlib
import mimetypes

logger = logging.getLogger(__name__)

class ProductionOptimizer:
    """Production performance optimization with caching, compression, and CDN support"""
    
    def __init__(self):
        self.cache_store = {}
        self.compression_enabled = True
        self.cdn_enabled = os.environ.get('CDN_ENABLED', 'false').lower() == 'true'
        self.cdn_base_url = os.environ.get('CDN_BASE_URL', '')
        self.static_cache_duration = 86400 * 30  # 30 days for static assets
        self.api_cache_duration = 300  # 5 minutes for API responses
        
    def optimize_static_assets(self, app) -> None:
        """Configure static asset optimization"""
        try:
            # Configure static file caching
            @app.after_request
            def add_cache_headers(response):
                return self._add_cache_headers(response)
            
            # Configure compression
            if self.compression_enabled:
                @app.after_request
                def compress_response(response):
                    return self._compress_response(response)
            
            # Configure CDN URLs if enabled
            if self.cdn_enabled and self.cdn_base_url:
                self._configure_cdn_urls(app)
            
            logger.info("Static asset optimization configured")
            
        except Exception as e:
            logger.error(f"Failed to configure static asset optimization: {e}")
    
    def _add_cache_headers(self, response: Response) -> Response:
        """Add appropriate cache headers based on content type"""
        try:
            # Skip for non-successful responses
            if response.status_code >= 400:
                return response
            
            # Get request path
            path = request.path if request else ''
            
            # Static assets (CSS, JS, images)
            if self._is_static_asset(path):
                max_age = self.static_cache_duration
                response.headers['Cache-Control'] = f'public, max-age={max_age}, immutable'
                response.headers['Expires'] = (datetime.utcnow() + timedelta(seconds=max_age)).strftime('%a, %d %b %Y %H:%M:%S GMT')
                
                # Add ETag for static assets
                if hasattr(response, 'data') and response.data:
                    etag = hashlib.md5(response.data).hexdigest()
                    response.headers['ETag'] = f'"{etag}"'
            
            # API responses
            elif path.startswith('/api/'):
                if self._is_cacheable_api(path):
                    max_age = self.api_cache_duration
                    response.headers['Cache-Control'] = f'public, max-age={max_age}'
                else:
                    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
            
            # HTML pages
            elif response.content_type and 'text/html' in response.content_type:
                response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes
            
            return response
            
        except Exception as e:
            logger.warning(f"Failed to add cache headers: {e}")
            return response
    
    def _compress_response(self, response: Response) -> Response:
        """Compress response if appropriate"""
        try:
            # Skip if already compressed or small response
            if (response.status_code >= 400 or 
                'Content-Encoding' in response.headers or
                not hasattr(response, 'data') or
                len(response.data) < 1024):
                return response
            
            # Check if client accepts gzip
            accept_encoding = request.headers.get('Accept-Encoding', '') if request else ''
            if 'gzip' not in accept_encoding:
                return response
            
            # Check content type is compressible
            content_type = response.content_type or ''
            if not self._is_compressible_content(content_type):
                return response
            
            # Compress the response
            compressed_data = gzip.compress(response.data)
            
            # Only use compression if it actually reduces size
            if len(compressed_data) < len(response.data):
                response.data = compressed_data
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = len(compressed_data)
                response.headers['Vary'] = 'Accept-Encoding'
            
            return response
            
        except Exception as e:
            logger.warning(f"Failed to compress response: {e}")
            return response
    
    def _configure_cdn_urls(self, app) -> None:
        """Configure CDN URLs for static assets"""
        try:
            # Override url_for for static files when CDN is enabled
            original_url_for = app.jinja_env.globals['url_for']
            
            def cdn_url_for(endpoint, **values):
                if endpoint == 'static' and self.cdn_base_url:
                    filename = values.get('filename', '')
                    return f"{self.cdn_base_url.rstrip('/')}/static/{filename}"
                return original_url_for(endpoint, **values)
            
            app.jinja_env.globals['url_for'] = cdn_url_for
            logger.info(f"CDN configured: {self.cdn_base_url}")
            
        except Exception as e:
            logger.error(f"Failed to configure CDN: {e}")
    
    def _is_static_asset(self, path: str) -> bool:
        """Check if path is a static asset"""
        static_extensions = {'.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot'}
        return any(path.endswith(ext) for ext in static_extensions) or path.startswith('/static/')
    
    def _is_cacheable_api(self, path: str) -> bool:
        """Check if API endpoint is cacheable"""
        # Only cache certain read-only API endpoints
        cacheable_apis = ['/api/health', '/api/config', '/api/status']
        return any(path.startswith(api) for api in cacheable_apis)
    
    def _is_compressible_content(self, content_type: str) -> bool:
        """Check if content type should be compressed"""
        compressible_types = {
            'text/html', 'text/css', 'text/javascript', 'application/javascript',
            'application/json', 'text/xml', 'application/xml', 'text/plain',
            'image/svg+xml'
        }
        return any(content_type.startswith(ct) for ct in compressible_types)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance optimization metrics"""
        return {
            'caching_enabled': True,
            'compression_enabled': self.compression_enabled,
            'cdn_enabled': self.cdn_enabled,
            'cdn_base_url': self.cdn_base_url if self.cdn_enabled else None,
            'static_cache_duration': self.static_cache_duration,
            'api_cache_duration': self.api_cache_duration,
            'cache_entries': len(self.cache_store),
            'optimizations_active': [
                'static_caching',
                'gzip_compression' if self.compression_enabled else None,
                'cdn_delivery' if self.cdn_enabled else None,
                'etag_validation',
                'cache_control_headers'
            ]
        }

class SecurityHeadersManager:
    """Manage production security headers - Fixes Issues 36-38"""
    
    def __init__(self):
        self.https_enforced = os.environ.get('FORCE_HTTPS', 'true').lower() == 'true'
        self.strict_transport_security = True
        
    def configure_security_headers(self, app) -> None:
        """Configure comprehensive security headers for production"""
        try:
            @app.before_request
            def enforce_https():
                if self.https_enforced and not request.is_secure:
                    # Redirect HTTP to HTTPS in production
                    if not request.headers.get('X-Forwarded-Proto') == 'https':
                        return self._redirect_to_https()
            
            @app.after_request
            def add_security_headers(response):
                return self._add_security_headers(response)
            
            logger.info("Security headers configured for production")
            
        except Exception as e:
            logger.error(f"Failed to configure security headers: {e}")
    
    def _redirect_to_https(self):
        """Redirect HTTP requests to HTTPS"""
        from flask import redirect, url_for
        return redirect(request.url.replace('http://', 'https://'), code=301)
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add comprehensive security headers"""
        try:
            # HTTPS enforcement
            if self.strict_transport_security:
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
            
            # Content Security Policy
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://apis.google.com https://accounts.google.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.openrouter.ai https://accounts.google.com; "
                "frame-src https://accounts.google.com; "
                "object-src 'none'; "
                "base-uri 'self'"
            )
            response.headers['Content-Security-Policy'] = csp_policy
            
            # Additional security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
            
            # Cookie security
            if response.headers.get('Set-Cookie'):
                # Ensure secure cookie flags
                cookie_header = response.headers['Set-Cookie']
                if 'Secure' not in cookie_header and self.https_enforced:
                    cookie_header += '; Secure'
                if 'SameSite' not in cookie_header:
                    cookie_header += '; SameSite=Lax'
                response.headers['Set-Cookie'] = cookie_header
            
            return response
            
        except Exception as e:
            logger.warning(f"Failed to add security headers: {e}")
            return response
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get security configuration status"""
        return {
            'https_enforced': self.https_enforced,
            'hsts_enabled': self.strict_transport_security,
            'security_headers_active': [
                'Content-Security-Policy',
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection',
                'Referrer-Policy',
                'Permissions-Policy'
            ],
            'cookie_security': 'Secure, SameSite=Lax',
            'compliance_level': 'Production Ready'
        }

class MonitoringManager:
    """Production monitoring and logging - Fixes Issues 42-44"""
    
    def __init__(self):
        self.error_tracking_enabled = os.environ.get('ERROR_TRACKING_ENABLED', 'true').lower() == 'true'
        self.performance_monitoring = os.environ.get('PERFORMANCE_MONITORING', 'true').lower() == 'true'
        self.security_logging = os.environ.get('SECURITY_LOGGING', 'true').lower() == 'true'
        
    def configure_monitoring(self, app) -> None:
        """Configure comprehensive monitoring and logging"""
        try:
            if self.error_tracking_enabled:
                self._configure_error_tracking(app)
            
            if self.performance_monitoring:
                self._configure_performance_monitoring(app)
            
            if self.security_logging:
                self._configure_security_logging(app)
            
            logger.info("Production monitoring configured")
            
        except Exception as e:
            logger.error(f"Failed to configure monitoring: {e}")
    
    def _configure_error_tracking(self, app) -> None:
        """Configure error tracking and reporting"""
        @app.errorhandler(500)
        def handle_500_error(error):
            logger.error(f"Internal server error: {error}", exc_info=True)
            return {'error': 'Internal server error', 'status': 500}, 500
        
        @app.errorhandler(404)
        def handle_404_error(error):
            logger.warning(f"Page not found: {request.url}")
            return {'error': 'Page not found', 'status': 404}, 404
        
        @app.errorhandler(403)
        def handle_403_error(error):
            logger.warning(f"Access forbidden: {request.url} from {request.remote_addr}")
            return {'error': 'Access forbidden', 'status': 403}, 403
    
    def _configure_performance_monitoring(self, app) -> None:
        """Configure performance monitoring"""
        @app.before_request
        def start_timer():
            request.start_time = datetime.utcnow()
        
        @app.after_request
        def log_request_performance(response):
            if hasattr(request, 'start_time'):
                duration = (datetime.utcnow() - request.start_time).total_seconds()
                if duration > 1.0:  # Log slow requests
                    logger.warning(f"Slow request: {request.method} {request.path} took {duration:.2f}s")
            return response
    
    def _configure_security_logging(self, app) -> None:
        """Configure security event logging"""
        @app.before_request
        def log_security_events():
            # Log suspicious activity
            user_agent = request.headers.get('User-Agent', '')
            if any(bot in user_agent.lower() for bot in ['bot', 'crawler', 'spider']):
                logger.info(f"Bot access: {user_agent} from {request.remote_addr}")
            
            # Log authentication attempts
            if request.path.startswith('/auth/'):
                logger.info(f"Auth request: {request.method} {request.path} from {request.remote_addr}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring configuration status"""
        return {
            'error_tracking': self.error_tracking_enabled,
            'performance_monitoring': self.performance_monitoring,
            'security_logging': self.security_logging,
            'monitoring_endpoints': [
                '/api/health',
                '/api/metrics',
                '/api/status'
            ],
            'log_levels': ['ERROR', 'WARNING', 'INFO'],
            'status': 'Production Ready'
        }

# Global instances
production_optimizer = ProductionOptimizer()
security_headers_manager = SecurityHeadersManager()
monitoring_manager = MonitoringManager()

def configure_production_optimizations(app):
    """Configure all production optimizations"""
    try:
        production_optimizer.optimize_static_assets(app)
        security_headers_manager.configure_security_headers(app)
        monitoring_manager.configure_monitoring(app)
        
        logger.info("All production optimizations configured successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to configure production optimizations: {e}")
        return False