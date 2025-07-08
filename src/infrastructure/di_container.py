from typing import Dict, Any, Type, Callable
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
