#!/usr/bin/env python3
"""
Comprehensive Feature Documentation Generator
Scans entire NOUS codebase to identify every feature and function for accurate documentation
"""

import os
import re
import ast
import json
import inspect
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple

class FeatureDocumenter:
    def __init__(self):
        self.features = {}
        self.functions = {}
        self.classes = {}
        self.routes = {}
        self.api_endpoints = {}
        self.models = {}
        self.services = {}
        self.templates = {}
        self.static_assets = {}
        self.configurations = {}
        self.extensions = {}
        
        # Track files to avoid duplicates
        self.processed_files = set()
        
        # Documentation categories
        self.categories = {
            'core_features': [],
            'api_endpoints': [],
            'authentication': [],
            'ai_services': [],
            'health_monitoring': [],
            'analytics': [],
            'intelligence': [],
            'voice_interface': [],
            'financial': [],
            'collaboration': [],
            'search': [],
            'notifications': [],
            'automation': [],
            'security': [],
            'integrations': [],
            'utilities': []
        }
    
    def scan_entire_codebase(self):
        """Comprehensive scan of all codebase components"""
        print("🔍 Starting comprehensive codebase documentation scan...")
        
        # Scan Python files for functions and classes
        self._scan_python_files()
        
        # Scan route definitions
        self._scan_routes()
        
        # Scan API endpoints
        self._scan_api_endpoints()
        
        # Scan database models
        self._scan_models()
        
        # Scan services and utilities
        self._scan_services()
        
        # Scan templates
        self._scan_templates()
        
        # Scan static assets
        self._scan_static_assets()
        
        # Scan configuration files
        self._scan_configurations()
        
        # Scan extensions and plugins
        self._scan_extensions()
        
        # Categorize features
        self._categorize_features()
        
        print(f"✅ Scan complete! Found {len(self.functions)} functions, {len(self.classes)} classes, {len(self.routes)} routes")
    
    def _scan_python_files(self):
        """Scan all Python files for functions and classes"""
        python_files = []
        
        # Define directories to scan
        scan_dirs = [
            'api', 'models', 'routes', 'utils', 'services', 'extensions',
            'nous_tech', 'config', 'core', 'handlers', 'repositories',
            'voice_interface', 'tests'
        ]
        
        # Add root Python files
        for file in os.listdir('.'):
            if file.endswith('.py') and not file.startswith('.'):
                python_files.append(file)
        
        # Add files from subdirectories
        for dir_name in scan_dirs:
            if os.path.isdir(dir_name):
                for root, dirs, files in os.walk(dir_name):
                    # Skip cache and backup directories
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'backup']]
                    
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            python_files.append(file_path)
        
        # Process each Python file
        for file_path in python_files:
            if file_path not in self.processed_files:
                self._analyze_python_file(file_path)
                self.processed_files.add(file_path)
    
    def _analyze_python_file(self, file_path: str):
        """Analyze a single Python file for features"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST for accurate analysis
            try:
                tree = ast.parse(content)
                self._extract_from_ast(tree, file_path)
            except SyntaxError:
                # Fallback to regex parsing
                self._extract_with_regex(content, file_path)
                
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
    
    def _extract_from_ast(self, tree: ast.AST, file_path: str):
        """Extract functions and classes using AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._process_function(node, file_path)
            elif isinstance(node, ast.ClassDef):
                self._process_class(node, file_path)
            elif isinstance(node, ast.Assign):
                self._process_assignment(node, file_path)
    
    def _process_function(self, node: ast.FunctionDef, file_path: str):
        """Process a function definition"""
        func_name = node.name
        
        # Extract docstring
        docstring = ast.get_docstring(node) or "No documentation available"
        
        # Extract function signature
        args = [arg.arg for arg in node.args.args]
        
        # Determine function category
        category = self._categorize_function(func_name, file_path)
        
        function_info = {
            'name': func_name,
            'file': file_path,
            'docstring': docstring,
            'arguments': args,
            'category': category,
            'line_number': node.lineno,
            'is_route': self._is_route_function(node),
            'is_api': self._is_api_function(func_name, file_path),
            'decorators': [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list]
        }
        
        self.functions[f"{file_path}::{func_name}"] = function_info
        
        # Add to appropriate category
        if category in self.categories:
            self.categories[category].append(function_info)
    
    def _process_class(self, node: ast.ClassDef, file_path: str):
        """Process a class definition"""
        class_name = node.name
        docstring = ast.get_docstring(node) or "No documentation available"
        
        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append({
                    'name': item.name,
                    'docstring': ast.get_docstring(item) or "No documentation",
                    'arguments': [arg.arg for arg in item.args.args],
                    'line_number': item.lineno
                })
        
        # Determine if it's a model, service, etc.
        class_type = self._determine_class_type(class_name, file_path)
        
        class_info = {
            'name': class_name,
            'file': file_path,
            'docstring': docstring,
            'methods': methods,
            'type': class_type,
            'line_number': node.lineno,
            'base_classes': [base.id if hasattr(base, 'id') else str(base) for base in node.bases]
        }
        
        self.classes[f"{file_path}::{class_name}"] = class_info
        
        # Store in specific collections
        if class_type == 'model':
            self.models[class_name] = class_info
        elif class_type == 'service':
            self.services[class_name] = class_info
    
    def _scan_routes(self):
        """Scan route definitions across the application"""
        route_files = []
        
        # Find all route files
        if os.path.exists('routes'):
            for root, dirs, files in os.walk('routes'):
                for file in files:
                    if file.endswith('.py'):
                        route_files.append(os.path.join(root, file))
        
        # Also check main app files
        for file in ['app.py', 'main.py']:
            if os.path.exists(file):
                route_files.append(file)
        
        # Process route files
        for file_path in route_files:
            self._extract_routes_from_file(file_path)
    
    def _extract_routes_from_file(self, file_path: str):
        """Extract route definitions from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find route decorators
            route_patterns = [
                r'@\w*\.route\(["\']([^"\']+)["\']([^)]*)\)',
                r'@app\.route\(["\']([^"\']+)["\']([^)]*)\)',
                r'@bp\.route\(["\']([^"\']+)["\']([^)]*)\)',
                r'@.*_bp\.route\(["\']([^"\']+)["\']([^)]*)\)'
            ]
            
            for pattern in route_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    route_path = match[0]
                    route_options = match[1] if len(match) > 1 else ""
                    
                    # Extract HTTP methods
                    methods = re.findall(r'methods=\[([^\]]+)\]', route_options)
                    methods = methods[0].replace('"', '').replace("'", "").split(',') if methods else ['GET']
                    
                    route_info = {
                        'path': route_path,
                        'methods': [m.strip() for m in methods],
                        'file': file_path,
                        'options': route_options,
                        'category': self._categorize_route(route_path)
                    }
                    
                    self.routes[route_path] = route_info
                    
        except Exception as e:
            print(f"⚠️  Error extracting routes from {file_path}: {e}")
    
    def _scan_api_endpoints(self):
        """Scan for API endpoint definitions"""
        # API endpoints are typically routes starting with /api/
        for route_path, route_info in self.routes.items():
            if route_path.startswith('/api/'):
                self.api_endpoints[route_path] = {
                    **route_info,
                    'type': self._determine_api_type(route_path)
                }
    
    def _scan_models(self):
        """Scan database models"""
        model_files = []
        
        if os.path.exists('models'):
            for root, dirs, files in os.walk('models'):
                for file in files:
                    if file.endswith('.py') and file != '__init__.py':
                        model_files.append(os.path.join(root, file))
        
        # Already processed in _scan_python_files, but let's categorize
        # Models are already stored in self.models from class processing
    
    def _scan_services(self):
        """Scan service layer components"""
        # Services are already processed in _scan_python_files
        # Just categorize utilities as services if they follow service patterns
        for func_key, func_info in self.functions.items():
            if 'service' in func_info['file'].lower() or 'helper' in func_info['file'].lower():
                if func_info['category'] == 'utilities':
                    func_info['category'] = 'services'
    
    def _scan_templates(self):
        """Scan HTML templates"""
        if os.path.exists('templates'):
            for root, dirs, files in os.walk('templates'):
                for file in files:
                    if file.endswith('.html'):
                        template_path = os.path.join(root, file)
                        template_name = file.replace('.html', '')
                        
                        self.templates[template_name] = {
                            'name': template_name,
                            'path': template_path,
                            'category': self._categorize_template(template_name)
                        }
    
    def _scan_static_assets(self):
        """Scan static assets"""
        if os.path.exists('static'):
            for root, dirs, files in os.walk('static'):
                for file in files:
                    asset_path = os.path.join(root, file)
                    asset_type = self._determine_asset_type(file)
                    
                    self.static_assets[file] = {
                        'name': file,
                        'path': asset_path,
                        'type': asset_type
                    }
    
    def _scan_configurations(self):
        """Scan configuration files"""
        config_files = [
            'pyproject.toml', 'replit.toml', 'replit.nix',
            'gunicorn.conf.py', 'build.properties'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                self.configurations[config_file] = {
                    'name': config_file,
                    'type': self._determine_config_type(config_file)
                }
    
    def _scan_extensions(self):
        """Scan extensions and plugins"""
        extension_dirs = ['extensions', 'nous_tech']
        
        for ext_dir in extension_dirs:
            if os.path.exists(ext_dir):
                for root, dirs, files in os.walk(ext_dir):
                    for file in files:
                        if file.endswith('.py') and file != '__init__.py':
                            ext_path = os.path.join(root, file)
                            ext_name = file.replace('.py', '')
                            
                            self.extensions[ext_name] = {
                                'name': ext_name,
                                'path': ext_path,
                                'category': 'extension'
                            }
    
    def _categorize_features(self):
        """Categorize all discovered features"""
        # This is already done during processing, but we can refine here
        pass
    
    # Helper methods for categorization
    def _categorize_function(self, func_name: str, file_path: str) -> str:
        """Categorize a function based on name and location"""
        func_lower = func_name.lower()
        file_lower = file_path.lower()
        
        # Route functions
        if 'route' in file_lower or self._is_route_function_name(func_name):
            return 'core_features'
        
        # API functions
        if 'api' in file_lower or func_name.startswith('api_'):
            return 'api_endpoints'
        
        # Authentication
        if any(word in func_lower for word in ['auth', 'login', 'token', 'oauth']):
            return 'authentication'
        
        # AI and intelligence
        if any(word in func_lower for word in ['ai', 'chat', 'intelligence', 'predict', 'analyze']):
            return 'ai_services'
        
        # Health monitoring
        if any(word in func_lower for word in ['health', 'monitor', 'check', 'status']):
            return 'health_monitoring'
        
        # Analytics
        if any(word in func_lower for word in ['analytics', 'metrics', 'insights', 'track']):
            return 'analytics'
        
        # Voice interface
        if any(word in func_lower for word in ['voice', 'speech', 'audio', 'tts', 'stt']):
            return 'voice_interface'
        
        # Financial
        if any(word in func_lower for word in ['financial', 'bank', 'transaction', 'payment']):
            return 'financial'
        
        # Collaboration
        if any(word in func_lower for word in ['collaboration', 'share', 'family', 'group']):
            return 'collaboration'
        
        # Search
        if any(word in func_lower for word in ['search', 'find', 'query', 'index']):
            return 'search'
        
        # Notifications
        if any(word in func_lower for word in ['notification', 'alert', 'notify', 'message']):
            return 'notifications'
        
        # Automation
        if any(word in func_lower for word in ['automation', 'automate', 'workflow', 'trigger']):
            return 'automation'
        
        # Security
        if any(word in func_lower for word in ['security', 'secure', 'encrypt', 'hash']):
            return 'security'
        
        # Integrations
        if any(word in func_lower for word in ['integration', 'api', 'external', 'service']):
            return 'integrations'
        
        return 'utilities'
    
    def _categorize_route(self, route_path: str) -> str:
        """Categorize a route based on its path"""
        if route_path.startswith('/api/'):
            return 'api_endpoints'
        elif any(word in route_path for word in ['/auth', '/login', '/oauth']):
            return 'authentication'
        elif any(word in route_path for word in ['/health', '/status']):
            return 'health_monitoring'
        elif any(word in route_path for word in ['/analytics', '/metrics']):
            return 'analytics'
        else:
            return 'core_features'
    
    def _categorize_template(self, template_name: str) -> str:
        """Categorize a template based on its name"""
        if any(word in template_name for word in ['analytics', 'dashboard']):
            return 'analytics'
        elif any(word in template_name for word in ['voice', 'audio']):
            return 'voice_interface'
        elif any(word in template_name for word in ['financial', 'bank']):
            return 'financial'
        else:
            return 'core_features'
    
    def _determine_class_type(self, class_name: str, file_path: str) -> str:
        """Determine the type of a class"""
        if 'models' in file_path or class_name.endswith('Model'):
            return 'model'
        elif 'services' in file_path or class_name.endswith('Service'):
            return 'service'
        elif any(word in class_name.lower() for word in ['helper', 'manager', 'handler']):
            return 'utility'
        else:
            return 'class'
    
    def _determine_api_type(self, route_path: str) -> str:
        """Determine the type of API endpoint"""
        if '/v1/' in route_path:
            return 'api_v1'
        elif '/v2/' in route_path:
            return 'api_v2'
        elif 'chat' in route_path:
            return 'chat_api'
        elif 'analytics' in route_path:
            return 'analytics_api'
        else:
            return 'general_api'
    
    def _determine_asset_type(self, filename: str) -> str:
        """Determine the type of static asset"""
        ext = filename.split('.')[-1].lower()
        if ext in ['css']:
            return 'stylesheet'
        elif ext in ['js']:
            return 'javascript'
        elif ext in ['png', 'jpg', 'jpeg', 'svg', 'ico']:
            return 'image'
        elif ext in ['json']:
            return 'data'
        else:
            return 'other'
    
    def _determine_config_type(self, filename: str) -> str:
        """Determine the type of configuration file"""
        if filename.endswith('.toml'):
            return 'toml_config'
        elif filename.endswith('.py'):
            return 'python_config'
        elif filename.endswith('.properties'):
            return 'properties_config'
        else:
            return 'config'
    
    def _is_route_function(self, node: ast.FunctionDef) -> bool:
        """Check if a function is a route handler"""
        for decorator in node.decorator_list:
            if hasattr(decorator, 'attr') and decorator.attr == 'route':
                return True
            elif hasattr(decorator, 'id') and 'route' in str(decorator.id):
                return True
        return False
    
    def _is_route_function_name(self, func_name: str) -> bool:
        """Check if function name suggests it's a route"""
        route_indicators = ['route', 'endpoint', 'handler', 'view']
        return any(indicator in func_name.lower() for indicator in route_indicators)
    
    def _is_api_function(self, func_name: str, file_path: str) -> bool:
        """Check if function is an API function"""
        return (func_name.startswith('api_') or 
                'api' in file_path.lower() or 
                func_name.endswith('_api'))
    
    def _extract_with_regex(self, content: str, file_path: str):
        """Fallback regex-based extraction"""
        # Extract function definitions
        func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
        functions = re.findall(func_pattern, content)
        
        for func_name in functions:
            category = self._categorize_function(func_name, file_path)
            function_info = {
                'name': func_name,
                'file': file_path,
                'docstring': "Documentation not available (regex extraction)",
                'arguments': [],
                'category': category,
                'line_number': 0,
                'is_route': False,
                'is_api': self._is_api_function(func_name, file_path),
                'decorators': []
            }
            self.functions[f"{file_path}::{func_name}"] = function_info
        
        # Extract class definitions
        class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:'
        classes = re.findall(class_pattern, content)
        
        for class_name in classes:
            class_type = self._determine_class_type(class_name, file_path)
            class_info = {
                'name': class_name,
                'file': file_path,
                'docstring': "Documentation not available (regex extraction)",
                'methods': [],
                'type': class_type,
                'line_number': 0,
                'base_classes': []
            }
            self.classes[f"{file_path}::{class_name}"] = class_info
    
    def generate_comprehensive_documentation(self):
        """Generate complete feature documentation"""
        docs = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_functions': len(self.functions),
                'total_classes': len(self.classes),
                'total_routes': len(self.routes),
                'total_api_endpoints': len(self.api_endpoints),
                'total_models': len(self.models),
                'total_services': len(self.services),
                'total_templates': len(self.templates),
                'total_static_assets': len(self.static_assets)
            },
            'features_by_category': self.categories,
            'functions': self.functions,
            'classes': self.classes,
            'routes': self.routes,
            'api_endpoints': self.api_endpoints,
            'models': self.models,
            'services': self.services,
            'templates': self.templates,
            'static_assets': self.static_assets,
            'configurations': self.configurations,
            'extensions': self.extensions
        }
        
        return docs
    
    def save_documentation(self, docs: Dict):
        """Save documentation to files"""
        # Save complete JSON documentation
        with open('comprehensive_feature_documentation.json', 'w') as f:
            json.dump(docs, f, indent=2, default=str)
        
        # Generate markdown documentation
        self._generate_markdown_docs(docs)
        
        print("📄 Documentation saved:")
        print("  - comprehensive_feature_documentation.json")
        print("  - docs/COMPLETE_FEATURES.md")
        print("  - docs/API_COMPLETE.md")
        print("  - docs/FUNCTIONS_REFERENCE.md")
    
    def _generate_markdown_docs(self, docs: Dict):
        """Generate markdown documentation files"""
        # Ensure docs directory exists
        os.makedirs('docs', exist_ok=True)
        
        # Generate complete features documentation
        self._generate_features_md(docs)
        
        # Generate complete API documentation
        self._generate_api_md(docs)
        
        # Generate functions reference
        self._generate_functions_md(docs)
    
    def _generate_features_md(self, docs: Dict):
        """Generate complete features markdown"""
        content = f"""# NOUS Complete Features Documentation

Generated: {docs['metadata']['generated_at']}

## Summary
- **Functions**: {docs['metadata']['total_functions']}
- **Classes**: {docs['metadata']['total_classes']}
- **Routes**: {docs['metadata']['total_routes']}
- **API Endpoints**: {docs['metadata']['total_api_endpoints']}
- **Database Models**: {docs['metadata']['total_models']}
- **Services**: {docs['metadata']['total_services']}
- **Templates**: {docs['metadata']['total_templates']}
- **Static Assets**: {docs['metadata']['total_static_assets']}

## Features by Category

"""
        
        for category, features in docs['features_by_category'].items():
            if features:
                content += f"### {category.replace('_', ' ').title()}\n\n"
                for feature in features:
                    content += f"- **{feature['name']}** ({feature['file']})\n"
                    if feature.get('docstring') and feature['docstring'] != "No documentation available":
                        content += f"  - {feature['docstring'][:100]}...\n"
                content += "\n"
        
        # Add routes section
        content += "## Routes\n\n"
        for route_path, route_info in docs['routes'].items():
            methods = ', '.join(route_info['methods'])
            content += f"- **{methods} {route_path}** ({route_info['file']})\n"
        
        # Add models section
        content += "\n## Database Models\n\n"
        for model_name, model_info in docs['models'].items():
            content += f"- **{model_name}** ({model_info['file']})\n"
            if model_info.get('docstring'):
                content += f"  - {model_info['docstring'][:100]}...\n"
        
        with open('docs/COMPLETE_FEATURES.md', 'w') as f:
            f.write(content)
    
    def _generate_api_md(self, docs: Dict):
        """Generate complete API documentation"""
        content = f"""# NOUS Complete API Documentation

Generated: {docs['metadata']['generated_at']}

## API Endpoints ({docs['metadata']['total_api_endpoints']} total)

"""
        
        for endpoint_path, endpoint_info in docs['api_endpoints'].items():
            methods = ', '.join(endpoint_info['methods'])
            content += f"### {methods} {endpoint_path}\n\n"
            content += f"- **File**: {endpoint_info['file']}\n"
            content += f"- **Type**: {endpoint_info['type']}\n"
            content += f"- **Category**: {endpoint_info['category']}\n"
            if endpoint_info.get('options'):
                content += f"- **Options**: {endpoint_info['options']}\n"
            content += "\n"
        
        with open('docs/API_COMPLETE.md', 'w') as f:
            f.write(content)
    
    def _generate_functions_md(self, docs: Dict):
        """Generate functions reference documentation"""
        content = f"""# NOUS Functions Reference

Generated: {docs['metadata']['generated_at']}

## All Functions ({docs['metadata']['total_functions']} total)

"""
        
        current_file = ""
        for func_key, func_info in sorted(docs['functions'].items()):
            if func_info['file'] != current_file:
                current_file = func_info['file']
                content += f"\n## {current_file}\n\n"
            
            content += f"### {func_info['name']}\n\n"
            content += f"- **Category**: {func_info['category']}\n"
            content += f"- **Line**: {func_info['line_number']}\n"
            if func_info['arguments']:
                content += f"- **Arguments**: {', '.join(func_info['arguments'])}\n"
            if func_info['decorators']:
                content += f"- **Decorators**: {', '.join(func_info['decorators'])}\n"
            if func_info.get('docstring') and func_info['docstring'] != "No documentation available":
                content += f"- **Documentation**: {func_info['docstring']}\n"
            content += "\n"
        
        with open('docs/FUNCTIONS_REFERENCE.md', 'w') as f:
            f.write(content)


def main():
    """Run comprehensive feature documentation"""
    documenter = FeatureDocumenter()
    
    print("🚀 Starting comprehensive feature documentation...")
    documenter.scan_entire_codebase()
    
    print("📝 Generating documentation...")
    docs = documenter.generate_comprehensive_documentation()
    
    print("💾 Saving documentation...")
    documenter.save_documentation(docs)
    
    print("\n✅ Complete feature documentation generated successfully!")
    print(f"📊 Summary:")
    print(f"   - Functions: {docs['metadata']['total_functions']}")
    print(f"   - Classes: {docs['metadata']['total_classes']}")
    print(f"   - Routes: {docs['metadata']['total_routes']}")
    print(f"   - API Endpoints: {docs['metadata']['total_api_endpoints']}")
    print(f"   - Models: {docs['metadata']['total_models']}")
    print(f"   - Services: {docs['metadata']['total_services']}")


if __name__ == "__main__":
    main()