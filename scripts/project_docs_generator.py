#!/usr/bin/env python3
"""
NOUS Project Documentation Generator - Project Files Only
"""

import os
import json
from datetime import datetime
from pathlib import Path

def get_project_files():
    """Get only project Python files, excluding dependencies"""
    project_files = []
    
    # Define project directories to include
    project_dirs = [
        'api',
        'models', 
        'routes',
        'utils',
        'scripts',
        'tests',
        'config',
        'core'
    ]
    
    # Add root level Python files
    for file in os.listdir('.'):
        if file.endswith('.py'):
            project_files.append(file)
    
    # Add files from project directories
    for dir_name in project_dirs:
        if os.path.isdir(dir_name):
            for root, dirs, files in os.walk(dir_name):
                for file in files:
                    if file.endswith('.py'):
                        project_files.append(os.path.join(root, file))
    
    return sorted(project_files)

def analyze_file(file_path):
    """Analyze a Python file for documentation"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Extract module docstring
        module_doc = ""
        if lines and lines[0].strip().startswith('"""'):
            doc_lines = []
            in_doc = False
            for i, line in enumerate(lines):
                if '"""' in line:
                    if not in_doc:
                        in_doc = True
                        doc_lines.append(line.replace('"""', ''))
                    else:
                        doc_lines.append(line.split('"""')[0])
                        break
                elif in_doc:
                    doc_lines.append(line)
            module_doc = '\n'.join(doc_lines).strip()
        
        # Count various elements
        functions = []
        classes = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('def '):
                func_name = stripped.split('(')[0].replace('def ', '')
                functions.append(func_name)
            elif stripped.startswith('class '):
                class_name = stripped.split('(')[0].replace('class ', '').replace(':', '')
                classes.append(class_name)
        
        return {
            'file': file_path,
            'module_doc': module_doc,
            'functions': functions,
            'classes': classes,
            'total_lines': len(lines),
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e),
            'status': 'error'
        }

def generate_docs():
    """Generate project documentation"""
    print("Generating NOUS Project Documentation...")
    
    project_files = get_project_files()
    print(f"Found {len(project_files)} project files")
    
    docs_data = {
        'project_name': 'NOUS Personal Assistant',
        'generated_at': datetime.utcnow().isoformat(),
        'total_files': len(project_files),
        'files': []
    }
    
    for file_path in project_files:
        print(f"  Analyzing: {file_path}")
        file_data = analyze_file(file_path)
        docs_data['files'].append(file_data)
    
    # Calculate summary statistics
    successful_files = [f for f in docs_data['files'] if f['status'] == 'success']
    total_functions = sum(len(f.get('functions', [])) for f in successful_files)
    total_classes = sum(len(f.get('classes', [])) for f in successful_files)
    total_lines = sum(f.get('total_lines', 0) for f in successful_files)
    
    docs_data['summary'] = {
        'successful_files': len(successful_files),
        'total_functions': total_functions,
        'total_classes': total_classes,
        'total_lines': total_lines
    }
    
    # Generate HTML documentation
    html_content = generate_html_docs(docs_data)
    
    # Ensure output directory exists
    output_dir = Path("docs/_build/html")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write files
    html_file = output_dir / "index.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    json_file = output_dir / "project_docs.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(docs_data, f, indent=2)
    
    print(f"\nDocumentation generated successfully!")
    print(f"  HTML: {html_file}")
    print(f"  JSON: {json_file}")
    print(f"  Files analyzed: {docs_data['total_files']}")
    print(f"  Functions found: {total_functions}")
    print(f"  Classes found: {total_classes}")
    
    return html_file

def generate_html_docs(docs_data):
    """Generate HTML documentation"""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{docs_data['project_name']} - Documentation</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background: #f5f7fa;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
            text-align: center;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        .stats {{
            background: white;
            margin: 30px 0;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .stat-card {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .file-section {{
            background: white;
            margin: 20px 0;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .file-header {{
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .file-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .file-meta {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .doc-content {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 15px 0;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
        }}
        .items-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }}
        .item {{
            background: #e8f4f8;
            padding: 8px 12px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .error {{
            color: #e74c3c;
            background: #fdf2f2;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #e74c3c;
        }}
        .toc {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
        .toc ul {{
            list-style: none;
            padding: 0;
        }}
        .toc li {{
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }}
        .toc a {{
            text-decoration: none;
            color: #667eea;
        }}
        .toc a:hover {{
            color: #764ba2;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>{docs_data['project_name']}</h1>
            <p>Code Documentation - Generated {docs_data['generated_at']}</p>
        </div>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{docs_data['summary']['successful_files']}</div>
                <div>Python Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{docs_data['summary']['total_functions']}</div>
                <div>Functions</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{docs_data['summary']['total_classes']}</div>
                <div>Classes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{docs_data['summary']['total_lines']:,}</div>
                <div>Lines of Code</div>
            </div>
        </div>
        
        <div class="toc">
            <h2>Table of Contents</h2>
            <ul>
"""
    
    # Generate table of contents
    for file_data in docs_data['files']:
        if file_data['status'] == 'success':
            file_id = file_data['file'].replace('/', '_').replace('.', '_')
            html += f'<li><a href="#{file_id}">{file_data["file"]}</a></li>'
    
    html += """
            </ul>
        </div>
        
        <h2>File Documentation</h2>
"""
    
    # Generate file documentation
    for file_data in docs_data['files']:
        file_id = file_data['file'].replace('/', '_').replace('.', '_')
        html += f'<div class="file-section" id="{file_id}">'
        
        if file_data['status'] == 'error':
            html += f"""
            <div class="file-header">
                <div class="file-title">{file_data['file']}</div>
                <div class="file-meta">Error processing file</div>
            </div>
            <div class="error">Error: {file_data['error']}</div>
            """
        else:
            html += f"""
            <div class="file-header">
                <div class="file-title">{file_data['file']}</div>
                <div class="file-meta">
                    {len(file_data.get('functions', []))} functions, 
                    {len(file_data.get('classes', []))} classes, 
                    {file_data.get('total_lines', 0)} lines
                </div>
            </div>
            """
            
            if file_data.get('module_doc'):
                html += f'<div class="doc-content">{file_data["module_doc"]}</div>'
            
            if file_data.get('functions'):
                html += '<h4>Functions</h4><div class="items-list">'
                for func in file_data['functions']:
                    html += f'<div class="item">{func}</div>'
                html += '</div>'
            
            if file_data.get('classes'):
                html += '<h4>Classes</h4><div class="items-list">'
                for cls in file_data['classes']:
                    html += f'<div class="item">{cls}</div>'
                html += '</div>'
        
        html += '</div>'
    
    html += """
        </div>
    </div>
</body>
</html>"""
    
    return html

if __name__ == "__main__":
    generate_docs()