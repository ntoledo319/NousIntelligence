#!/usr/bin/env python3
"""
NOUS API Documentation Generator
Generates HTML documentation from Flask app routes and Python modules
"""

import os
import sys
import inspect
import importlib
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_module_docs(module_name, output_dir):
    """Generate documentation for a Python module"""
    try:
        module = importlib.import_module(module_name)
        
        docs = {
            'module': module_name,
            'docstring': inspect.getdoc(module),
            'file': inspect.getfile(module),
            'functions': [],
            'classes': []
        }
        
        # Get all functions
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if obj.__module__ == module_name:
                func_doc = {
                    'name': name,
                    'docstring': inspect.getdoc(obj),
                    'signature': str(inspect.signature(obj)),
                    'source_file': inspect.getfile(obj)
                }
                docs['functions'].append(func_doc)
        
        # Get all classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module_name:
                class_doc = {
                    'name': name,
                    'docstring': inspect.getdoc(obj),
                    'methods': []
                }
                
                # Get class methods
                for method_name, method_obj in inspect.getmembers(obj, inspect.ismethod):
                    method_doc = {
                        'name': method_name,
                        'docstring': inspect.getdoc(method_obj),
                        'signature': str(inspect.signature(method_obj))
                    }
                    class_doc['methods'].append(method_doc)
                
                docs['classes'].append(class_doc)
        
        return docs
        
    except Exception as e:
        print(f"Error generating docs for {module_name}: {e}")
        return None

def generate_flask_routes_docs():
    """Generate documentation for Flask routes"""
    try:
        from app import create_app
        app = create_app()
        
        routes_docs = {
            'routes': [],
            'generated_at': datetime.utcnow().isoformat()
        }
        
        with app.app_context():
            for rule in app.url_map.iter_rules():
                route_doc = {
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods) if rule.methods else [],
                    'url': str(rule),
                    'function': rule.endpoint
                }
                
                # Try to get the actual function
                try:
                    view_func = app.view_functions.get(rule.endpoint)
                    if view_func:
                        route_doc['docstring'] = inspect.getdoc(view_func)
                        route_doc['source_file'] = inspect.getfile(view_func)
                except:
                    pass
                
                routes_docs['routes'].append(route_doc)
        
        return routes_docs
        
    except Exception as e:
        print(f"Error generating Flask routes docs: {e}")
        return None

def generate_html_docs(docs_data, output_file):
    """Generate HTML documentation from docs data"""
    html_template = """<!DOCTYPE html>
<html>
<head>
    <title>NOUS API Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .module {{ margin-bottom: 40px; padding: 20px; border: 1px solid #ddd; }}
        .function, .class {{ margin: 20px 0; padding: 15px; background: #f9f9f9; }}
        .signature {{ font-family: monospace; background: #e9e9e9; padding: 5px; }}
        .docstring {{ margin: 10px 0; white-space: pre-wrap; }}
        .route {{ margin: 15px 0; padding: 10px; background: #f0f8ff; }}
        .methods {{ color: #007; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>NOUS Personal Assistant - API Documentation</h1>
    <p>Generated on: {timestamp}</p>
    
    <h2>Flask Routes</h2>
    {routes_html}
    
    <h2>Python Modules</h2>
    {modules_html}
</body>
</html>"""
    
    routes_html = ""
    if 'routes' in docs_data:
        for route in docs_data['routes']:
            routes_html += f"""
            <div class="route">
                <h3>{route['endpoint']}</h3>
                <p><strong>URL:</strong> {route['url']}</p>
                <p><strong>Methods:</strong> <span class="methods">{', '.join(route['methods'])}</span></p>
                {f'<div class="docstring">{route.get("docstring", "No documentation available")}</div>' if route.get('docstring') else ''}
            </div>
            """
    
    modules_html = ""
    if 'modules' in docs_data:
        for module_data in docs_data['modules']:
            if module_data:
                modules_html += f"""
                <div class="module">
                    <h3>Module: {module_data['module']}</h3>
                    {f'<div class="docstring">{module_data["docstring"]}</div>' if module_data.get('docstring') else ''}
                    
                    <h4>Functions</h4>
                    {generate_functions_html(module_data.get('functions', []))}
                    
                    <h4>Classes</h4>
                    {generate_classes_html(module_data.get('classes', []))}
                </div>
                """
    
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    html_content = html_template.format(
        timestamp=timestamp,
        routes_html=routes_html,
        modules_html=modules_html
    )
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"HTML documentation generated: {output_file}")

def generate_functions_html(functions):
    """Generate HTML for functions"""
    html = ""
    for func in functions:
        html += f"""
        <div class="function">
            <h5>{func['name']}</h5>
            <div class="signature">{func['signature']}</div>
            {f'<div class="docstring">{func["docstring"]}</div>' if func.get('docstring') else ''}
        </div>
        """
    return html

def generate_classes_html(classes):
    """Generate HTML for classes"""
    html = ""
    for cls in classes:
        html += f"""
        <div class="class">
            <h5>{cls['name']}</h5>
            {f'<div class="docstring">{cls["docstring"]}</div>' if cls.get('docstring') else ''}
            
            <h6>Methods</h6>
            {generate_functions_html(cls.get('methods', []))}
        </div>
        """
    return html

def main():
    """Main documentation generation function"""
    output_dir = Path("docs/_build/html")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate Flask routes documentation
    print("Generating Flask routes documentation...")
    routes_docs = generate_flask_routes_docs()
    
    # Generate module documentation for key modules
    modules_to_document = [
        'app',
        'api.chat',
        'utils.health_monitor',
        'utils.database_optimizer',
        'models.user',
        'models.beta_models'
    ]
    
    print("Generating module documentation...")
    modules_docs = []
    for module_name in modules_to_document:
        print(f"  Documenting {module_name}...")
        module_doc = generate_module_docs(module_name, output_dir)
        if module_doc:
            modules_docs.append(module_doc)
    
    # Combine all documentation
    all_docs = {
        'routes': routes_docs.get('routes', []) if routes_docs else [],
        'modules': modules_docs,
        'generated_at': datetime.utcnow().isoformat()
    }
    
    # Generate HTML documentation
    html_output = output_dir / "index.html"
    generate_html_docs(all_docs, html_output)
    
    # Also save as JSON for programmatic access
    json_output = output_dir / "api_docs.json"
    with open(json_output, 'w') as f:
        json.dump(all_docs, f, indent=2)
    
    print(f"\nDocumentation generated successfully:")
    print(f"  HTML: {html_output}")
    print(f"  JSON: {json_output}")

if __name__ == "__main__":
    main()