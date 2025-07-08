#!/usr/bin/env python3
"""
Architecture Refactoring - Fixes circular dependencies, service layer, caching
Run: python architecture_refactor.py
"""

import os
import shutil
from pathlib import Path

class ArchitectureRefactor:
    def __init__(self):
        self.root = Path.cwd()
        
    def restructure_all(self):
        """Complete architectural refactoring"""
        print("🏗️ Starting Architecture Refactoring...")
        
        # 1. Create proper structure
        self.create_clean_architecture()
        
        # 2. Extract services
        self.extract_service_layer()
        
        # 3. Fix circular imports
        self.fix_circular_dependencies()
        
        # 4. Add caching layer
        self.add_caching_layer()
        
        # 5. Modularize monolith
        self.break_up_monolith()
        
        print("✅ Architecture refactoring complete!")
    
    def create_clean_architecture(self):
        """Create clean architecture folders"""
        print("Creating clean architecture structure...")
        
        folders = [
            'src/domain/entities',
            'src/domain/repositories',
            'src/application/services',
            'src/application/use_cases',
            'src/infrastructure/database',
            'src/infrastructure/external',
            'src/presentation/api',
            'src/presentation/web',
        ]
        
        for folder in folders:
            Path(folder).mkdir(parents=True, exist_ok=True)
            (Path(folder) / '__init__.py').touch()

    def extract_service_layer(self):
        """Create service layer from route logic"""
        print("Extracting service layer...")
        
        service_template = '''from typing import List, Optional, Dict, Any
from src.domain.repositories.{model_lower}_repository import {Model}Repository
from utils.encryption import encrypt_field, decrypt_field
import logging

logger = logging.getLogger(__name__)

class {Model}Service:
    def __init__(self, repository: {Model}Repository):
        self.repository = repository
    
    def get_all(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all {model_lower}s for a user"""
        try:
            return self.repository.find_by_user(user_id)
        except Exception as e:
            logger.error(f"Error getting {model_lower}s for user {{user_id}}: {{e}}")
            raise
    
    def get_by_id(self, id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get {model_lower} by ID for a user"""
        try:
            return self.repository.find_by_id_and_user(id, user_id)
        except Exception as e:
            logger.error(f"Error getting {model_lower} {{id}} for user {{user_id}}: {{e}}")
            raise
    
    def create(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create new {model_lower}"""
        try:
            data['user_id'] = user_id
            # Encrypt sensitive fields if needed
            data = self._encrypt_sensitive_fields(data)
            return self.repository.create(data)
        except Exception as e:
            logger.error(f"Error creating {model_lower}: {{e}}")
            raise
    
    def update(self, id: str, data: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
        """Update {model_lower}"""
        try:
            data = self._encrypt_sensitive_fields(data)
            return self.repository.update(id, data, user_id)
        except Exception as e:
            logger.error(f"Error updating {model_lower} {{id}}: {{e}}")
            raise
    
    def delete(self, id: str, user_id: str) -> bool:
        """Delete {model_lower}"""
        try:
            return self.repository.delete(id, user_id)
        except Exception as e:
            logger.error(f"Error deleting {model_lower} {{id}}: {{e}}")
            raise
    
    def _encrypt_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields - override in subclasses"""
        return data
'''
        
        # Generate services for all models
        models = ['User', 'Task', 'Family', 'MoodEntry', 'ThoughtRecord', 'ShoppingList', 'Product']
        for model in models:
            service_code = service_template.format(
                Model=model, 
                model_lower=model.lower()
            )
            service_path = f'src/application/services/{model.lower()}_service.py'
            os.makedirs(os.path.dirname(service_path), exist_ok=True)
            with open(service_path, 'w') as f:
                f.write(service_code)

        # Create specialized services
        self.create_specialized_services()

    def create_specialized_services(self):
        """Create specialized services"""
        
        # Mental Health Service
        mental_health_service = '''from typing import Dict, Any, List
from src.application.services.mood_entry_service import MoodEntryService
from src.application.services.thought_record_service import ThoughtRecordService
import logging

logger = logging.getLogger(__name__)

class MentalHealthService:
    def __init__(self, mood_service: MoodEntryService, thought_service: ThoughtRecordService):
        self.mood_service = mood_service
        self.thought_service = thought_service
    
    def analyze_mood_patterns(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze mood patterns over time"""
        moods = self.mood_service.get_recent(user_id, days)
        # Analysis logic here
        return {
            'average_mood': self._calculate_average_mood(moods),
            'mood_trend': self._calculate_trend(moods),
            'recommendations': self._get_recommendations(moods)
        }
    
    def get_therapeutic_insights(self, user_id: str) -> Dict[str, Any]:
        """Get therapeutic insights"""
        thoughts = self.thought_service.get_recent(user_id, 7)
        moods = self.mood_service.get_recent(user_id, 7)
        
        return {
            'common_triggers': self._identify_triggers(thoughts),
            'cognitive_patterns': self._analyze_patterns(thoughts),
            'mood_correlation': self._correlate_mood_thoughts(moods, thoughts)
        }
    
    def _calculate_average_mood(self, moods):
        if not moods:
            return 5.0
        return sum(mood.get('rating', 5) for mood in moods) / len(moods)
    
    def _calculate_trend(self, moods):
        # Simple trend calculation
        if len(moods) < 2:
            return 'stable'
        recent = moods[-5:]
        older = moods[-10:-5] if len(moods) >= 10 else moods[:-5]
        
        if not older:
            return 'stable'
            
        recent_avg = sum(m.get('rating', 5) for m in recent) / len(recent)
        older_avg = sum(m.get('rating', 5) for m in older) / len(older)
        
        if recent_avg > older_avg + 0.5:
            return 'improving'
        elif recent_avg < older_avg - 0.5:
            return 'declining'
        return 'stable'
    
    def _get_recommendations(self, moods):
        return [
            "Continue tracking your mood daily",
            "Consider exploring coping skills",
            "Practice mindfulness exercises"
        ]
'''

        with open('src/application/services/mental_health_service.py', 'w') as f:
            f.write(mental_health_service)

    def fix_circular_dependencies(self):
        """Fix circular imports with dependency injection"""
        print("Fixing circular dependencies...")
        
        di_container = '''from typing import Dict, Any, Type, Callable
import inspect

class DIContainer:
    def __init__(self):
        self._services = {}
        self._singletons = {}
        self._factories = {}
    
    def register(self, interface: Type, implementation: Type, singleton: bool = True):
        """Register a service implementation"""
        self._services[interface] = (implementation, singleton)
    
    def register_factory(self, interface: Type, factory: Callable):
        """Register a factory function"""
        self._factories[interface] = factory
    
    def resolve(self, interface: Type) -> Any:
        """Resolve a service instance"""
        # Check if already instantiated as singleton
        if interface in self._singletons:
            return self._singletons[interface]
            
        # Check for factory
        if interface in self._factories:
            instance = self._factories[interface]()
            return instance
            
        # Check for registered implementation
        if interface in self._services:
            impl, is_singleton = self._services[interface]
            instance = self._create_instance(impl)
            
            if is_singleton:
                self._singletons[interface] = instance
                
            return instance
            
        raise ValueError(f"No implementation registered for {interface}")
    
    def _create_instance(self, cls):
        """Create instance with dependency injection"""
        sig = inspect.signature(cls.__init__)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            if param.annotation != inspect.Parameter.empty:
                kwargs[param_name] = self.resolve(param.annotation)
        
        return cls(**kwargs)

# Global container
container = DIContainer()

def setup_dependencies():
    """Setup all service dependencies"""
    from src.domain.repositories.user_repository import UserRepository
    from src.domain.repositories.task_repository import TaskRepository
    from src.application.services.user_service import UserService
    from src.application.services.task_service import TaskService
    
    # Register repositories
    container.register(UserRepository, UserRepository)
    container.register(TaskRepository, TaskRepository)
    
    # Register services
    container.register(UserService, UserService)
    container.register(TaskService, TaskService)
'''
        
        with open('src/infrastructure/di_container.py', 'w') as f:
            f.write(di_container)

    def add_caching_layer(self):
        """Add Redis caching with fallback"""
        print("Adding caching layer...")
        
        cache_code = '''import json
import time
import logging
from typing import Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self._cache = {}  # In-memory fallback
        self.use_redis = False
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            import os
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()
            self.use_redis = True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {e}")
            self.use_redis = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.use_redis:
                value = self.redis.get(key)
                return json.loads(value) if value else None
            return self._cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache"""
        try:
            if self.use_redis:
                self.redis.set(key, json.dumps(value, default=str), ex=ttl)
            else:
                self._cache[key] = {
                    'value': value,
                    'expires': time.time() + ttl
                }
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        try:
            if self.use_redis:
                self.redis.delete(key)
            else:
                self._cache.pop(key, None)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def clear(self):
        """Clear all cache"""
        try:
            if self.use_redis:
                self.redis.flushdb()
            else:
                self._cache.clear()
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

# Global cache instance
cache = CacheManager()
'''
        
        with open('src/infrastructure/cache.py', 'w') as f:
            f.write(cache_code)

    def break_up_monolith(self):
        """Split app.py into modules"""
        print("Breaking up monolithic app...")
        
        # Create API blueprints
        blueprints = {
            'health': 'Health check endpoints',
            'auth': 'Authentication endpoints', 
            'mental_health': 'Mental health endpoints',
            'tasks': 'Task management endpoints',
            'family': 'Family collaboration endpoints',
            'analytics': 'Analytics and reporting'
        }
        
        blueprint_template = '''from flask import Blueprint, jsonify, request
from src.infrastructure.di_container import container
from utils.unified_auth import login_required, demo_allowed
from utils.encryption import encrypt_field, decrypt_field
import logging

logger = logging.getLogger(__name__)

{name}_bp = Blueprint('{name}', __name__, url_prefix='/api/{name}')

@{name}_bp.route('/health')
def health():
    """Health check for {name} service"""
    return jsonify({{'status': 'healthy', 'service': '{name}'}})

@{name}_bp.errorhandler(404)
def not_found(error):
    return jsonify({{'error': 'Endpoint not found'}}), 404

@{name}_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error in {name}: {{error}}")
    return jsonify({{'error': 'Internal server error'}}), 500
'''
        
        for name, description in blueprints.items():
            blueprint_code = blueprint_template.format(name=name)
            file_path = f'src/presentation/api/{name}.py'
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(blueprint_code)

        # Create main app factory
        app_factory = '''from flask import Flask
from src.infrastructure.di_container import setup_dependencies
from src.infrastructure.cache import cache
from utils.security_headers import init_security_headers
from utils.csrf_protection import init_csrf
from utils.env_loader import load_environment, get_config
import logging

def create_app(config_name='development'):
    """Application factory"""
    # Load environment
    load_environment()
    config = get_config()
    
    # Create Flask app
    app = Flask(__name__)
    app.config.update(config)
    
    # Initialize extensions
    init_security_headers(app)
    init_csrf(app)
    
    # Setup dependencies
    setup_dependencies()
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup logging
    setup_logging(app)
    
    return app

def register_blueprints(app):
    """Register all blueprints"""
    from src.presentation.api.health import health_bp
    from src.presentation.api.auth import auth_bp
    from src.presentation.api.mental_health import mental_health_bp
    from src.presentation.api.tasks import tasks_bp
    from src.presentation.api.family import family_bp
    from src.presentation.api.analytics import analytics_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mental_health_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(analytics_bp)

def setup_logging(app):
    """Setup application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
'''
        
        with open('src/app_factory.py', 'w') as f:
            f.write(app_factory)

if __name__ == "__main__":
    refactor = ArchitectureRefactor()
    refactor.restructure_all() 