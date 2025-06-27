#!/usr/bin/env python3
"""
Simple NOUS Documentation Generator
Creates basic HTML documentation from existing code
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

def scan_python_files():
    """Scan Python files for functions and classes"""
    python_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['.cache', 'backup', '__pycache__', '.git']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                python_files.append(file_path)
    
    return python_files

def extract_docstrings(file_path):
    """Extract basic information from Python files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract module docstring
        lines = content.split('\n')
        module_doc = ""
        if lines and lines[0].strip().startswith('"""'):
            doc_lines = []
            in_doc = True
            for line in lines:
                if '"""' in line and doc_lines:
                    doc_lines.append(line.split('"""')[0])
                    break
                if in_doc:
                    doc_lines.append(line.replace('"""', ''))
            module_doc = '\n'.join(doc_lines).strip()
        
        # Count functions and classes
        func_count = content.count('def ')
        class_count = content.count('class ')
        
        return {
            'file': file_path,
            'module_doc': module_doc,
            'functions': func_count,
            'classes': class_count,
            'lines': len(lines)
        }
        
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e),
            'functions': 0,
            'classes': 0,
            'lines': 0
        }

def generate_simple_docs():
    """Generate simple documentation"""
    print("Scanning Python files...")
    python_files = scan_python_files()
    
    docs_data = {
        'generated_at': datetime.utcnow().isoformat(),
        'total_files': len(python_files),
        'modules': []
    }
    
    for file_path in python_files:
        print(f"Processing: {file_path}")
        file_data = extract_docstrings(file_path)
        docs_data['modules'].append(file_data)
    
    # Generate HTML
    html_content = generate_html(docs_data)
    
    # Ensure output directory exists
    output_dir = Path("docs/_build/html")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write HTML file
    html_file = output_dir / "index.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Write JSON file
    json_file = output_dir / "docs_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(docs_data, f, indent=2)
    
    print(f"Documentation generated:")
    print(f"  HTML: {html_file}")
    print(f"  JSON: {json_file}")
    
    return docs_data

def generate_html(docs_data):
    """Generate HTML documentation"""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOUS Personal Assistant - Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 40px;
            background: #f8f9fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .stats {{
            background: #e8f4f8;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .module {{
            margin: 30px 0;
            padding: 20px;
            border-left: 4px solid #3498db;
            background: #f8f9fa;
        }}
        .module h3 {{
            margin-top: 0;
            color: #34495e;
        }}
        .module-info {{
            font-family: monospace;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        .doc-content {{
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-radius: 3px;
            white-space: pre-wrap;
        }}
        .error {{
            color: #e74c3c;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>NOUS Personal Assistant</h1>
        <h2>Code Documentation</h2>
        
        <div class="stats">
            <h3>Project Statistics</h3>
            <p><strong>Generated:</strong> {docs_data['generated_at']}</p>
            <p><strong>Total Python Files:</strong> {docs_data['total_files']}</p>
            <p><strong>Total Functions:</strong> {sum(m.get('functions', 0) for m in docs_data['modules'])}</p>
            <p><strong>Total Classes:</strong> {sum(m.get('classes', 0) for m in docs_data['modules'])}</p>
            <p><strong>Total Lines:</strong> {sum(m.get('lines', 0) for m in docs_data['modules'])}</p>
        </div>
        
        <h2>Python Modules</h2>
"""
    
    # Sort modules by file path
    sorted_modules = sorted(docs_data['modules'], key=lambda x: x['file'])
    
    for module in sorted_modules:
        file_path = module['file']
        html += f"""
        <div class="module">
            <h3>{file_path}</h3>
            <div class="module-info">
                Functions: {module.get('functions', 0)} | 
                Classes: {module.get('classes', 0)} | 
                Lines: {module.get('lines', 0)}
            </div>
"""
        
        if module.get('error'):
            html += f'<div class="error">Error: {module["error"]}</div>'
        elif module.get('module_doc'):
            html += f'<div class="doc-content">{module["module_doc"]}</div>'
        else:
            html += '<div class="doc-content">No module documentation found</div>'
        
        html += '</div>'
    
    html += """
        </div>
    </div>
</body>
</html>"""
    
    return html

if __name__ == "__main__":
    generate_simple_docs()