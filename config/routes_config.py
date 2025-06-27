"""
Unified Route Configuration
Standardizes all API routes under consistent base paths
"""
from config.app_config import AppConfig

class RouteConfig:
    """Route configuration management"""
    
    # ===== ROUTE MAPPINGS =====
    ROUTES = {
        # API v1 routes (primary)
        'api_v1': {
            'prefix': AppConfig.API_BASE_PATH,
            'routes': [
                'chat',
                'user', 
                'health',
                'settings',
                'weather',
                'shopping',
                'tasks',
                'memory',
                'voice',
                'spotify',
                'travel',
                'medications',
                'appointments',
                'budgets',
                'expenses'
            ]
        },
        
        # Legacy API routes (backward compatibility)
        'api_legacy': {
            'prefix': AppConfig.API_LEGACY_PATH,
            'routes': [
                'chat',
                'user',
                'health'
            ]
        },
        
        # Web routes (no prefix)
        'web': {
            'prefix': '',
            'routes': [
                '/',
                '/login',
                '/logout',
                '/app',
                '/dashboard',
                '/settings',
                '/health'
            ]
        }
    }
    
    @classmethod
    def get_route_url(cls, route_type: str, route_name: str) -> str:
        """Get full URL for a route"""
        route_config = cls.ROUTES.get(route_type)
        if not route_config:
            raise ValueError(f"Unknown route type: {route_type}")
        
        prefix = route_config['prefix']
        if route_name.startswith('/'):
            return f"{prefix}{route_name}"
        else:
            return f"{prefix}/{route_name}"
    
    @classmethod
    def get_api_v1_url(cls, endpoint: str) -> str:
        """Get API v1 URL for endpoint"""
        return cls.get_route_url('api_v1', endpoint)
    
    @classmethod
    def get_legacy_api_url(cls, endpoint: str) -> str:
        """Get legacy API URL for endpoint"""
        return cls.get_route_url('api_legacy', endpoint)
    
    @classmethod
    def validate_routes(cls) -> list:
        """Validate route configuration"""
        issues = []
        
        for route_type, config in cls.ROUTES.items():
            if not config.get('prefix', '').startswith('/') and config['prefix']:
                issues.append(f"Route prefix for {route_type} should start with '/'")
            
            if not config.get('routes'):
                issues.append(f"No routes defined for {route_type}")
        
        return issues

# Export commonly used route functions
get_api_v1_url = RouteConfig.get_api_v1_url
get_legacy_api_url = RouteConfig.get_legacy_api_url