
"""
Routes Package

This package contains all route blueprints for the NOUS application.
Organization follows a domain-driven approach with standardized patterns.
"""

from flask import Blueprint
import os
import importlib
import glob

# Store all registered blueprints for easy access
blueprints = []

def register_all_blueprints(app):
    """
    Automatically registers all blueprint modules in the routes directory
    
    Args:
        app: Flask application instance
    """
    # Register main routes blueprint
    from routes.main import main_bp
    app.register_blueprint(main_bp)
    blueprints.append(main_bp)
    
    # Auto-register all blueprints from route modules
    current_dir = os.path.dirname(os.path.abspath(__file__))
    route_files = glob.glob(os.path.join(current_dir, "*.py"))
    
    for file_path in route_files:
        filename = os.path.basename(file_path)
        if filename.startswith("__") or filename == "main.py":
            continue
            
        module_name = filename[:-3]  # Remove .py extension
        
        try:
            # Import the module
            module = importlib.import_module(f"routes.{module_name}")
            
            # Look for blueprint objects
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, Blueprint) and attr not in blueprints:
                    app.register_blueprint(attr)
                    blueprints.append(attr)
        except (ImportError, AttributeError) as e:
            print(f"Could not register routes from {module_name}: {str(e)}")
    
    # Register API routes from subdirectories
    register_api_routes(app)

def register_api_routes(app):
    """Register all API route blueprints"""
    try:
        # Import and register API v1 routes
        from routes.api.v1.settings import settings_api_v1
        from routes.api.v1.weather import weather_api_v1
        
        app.register_blueprint(settings_api_v1, url_prefix='/api/v1')
        app.register_blueprint(weather_api_v1, url_prefix='/api/v1')
        
        blueprints.extend([settings_api_v1, weather_api_v1])
        
        # Register other API routes
        from routes.api.health import health_api
        from routes.api.shopping import shopping_api
        
        app.register_blueprint(health_api, url_prefix='/api')
        app.register_blueprint(shopping_api, url_prefix='/api')
        
        blueprints.extend([health_api, shopping_api])
        
    except ImportError as e:
        print(f"Could not register API routes: {str(e)}")
