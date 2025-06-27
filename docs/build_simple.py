#!/usr/bin/env python3
"""
Simple documentation builder that converts RST to HTML without Sphinx dependencies
"""

import os
import shutil
from pathlib import Path

def convert_rst_to_html(rst_content, title):
    """Convert RST content to basic HTML."""
    
    # Simple RST to HTML conversion
    lines = rst_content.split('\n')
    html_lines = []
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith('.. code-block::'):
            html_lines.append('<pre><code>')
            in_code_block = True
            continue
        
        if in_code_block and not line.startswith('   ') and line.strip():
            html_lines.append('</code></pre>')
            in_code_block = False
        
        if in_code_block:
            # Remove 4 spaces of indentation
            content = line[4:] if line.startswith('    ') else line
            html_lines.append(content)
        else:
            # Convert headers
            if line and len(lines) > lines.index(line) + 1:
                next_line = lines[lines.index(line) + 1] if lines.index(line) + 1 < len(lines) else ""
                if next_line.startswith('='):
                    html_lines.append(f'<h1>{line}</h1>')
                    continue
                elif next_line.startswith('-'):
                    html_lines.append(f'<h2>{line}</h2>')
                    continue
                elif next_line.startswith('~'):
                    html_lines.append(f'<h3>{line}</h3>')
                    continue
            
            # Skip underline characters
            if line.strip() and all(c in '=-~^' for c in line.strip()):
                continue
            
            # Convert inline code
            if '``' in line:
                line = line.replace('``', '<code>').replace('``', '</code>')
            
            # Convert emphasis
            if '*' in line:
                line = line.replace('**', '<strong>').replace('**', '</strong>')
                line = line.replace('*', '<em>').replace('*', '</em>')
            
            # Add paragraph tags for non-empty lines
            if line.strip() and not line.startswith('<'):
                html_lines.append(f'<p>{line}</p>')
            elif line.strip().startswith('<'):
                html_lines.append(line)
            else:
                html_lines.append('<br>')
    
    if in_code_block:
        html_lines.append('</code></pre>')
    
    html_content = '\n'.join(html_lines)
    
    # Create full HTML document
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - NOUS Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
            background: #fafafa;
        }}
        
        .content {{
            background: white;
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        
        h1 {{
            color: #2563eb;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 0.5rem;
            margin-top: 0;
        }}
        
        h2 {{
            color: #1e40af;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 0.3rem;
            margin-top: 2rem;
        }}
        
        h3 {{
            color: #1f2937;
            margin-top: 1.5rem;
        }}
        
        code {{
            background: #f3f4f6;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.875rem;
        }}
        
        pre {{
            background: #f8f9fa;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.5rem;
            overflow-x: auto;
            margin: 1.5rem 0;
        }}
        
        pre code {{
            background: none;
            padding: 0;
        }}
        
        p {{
            margin: 1rem 0;
        }}
        
        strong {{
            color: #374151;
            font-weight: 600;
        }}
        
        em {{
            color: #6b7280;
            font-style: italic;
        }}
        
        .navigation {{
            background: #2563eb;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }}
        
        .navigation a {{
            color: white;
            text-decoration: none;
            margin-right: 1rem;
        }}
        
        .navigation a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="navigation">
        <a href="index.html">Home</a>
        <a href="overview.html">Overview</a>
        <a href="installation.html">Installation</a>
        <a href="api_reference.html">API Reference</a>
        <a href="architecture.html">Architecture</a>
        <a href="development.html">Development</a>
        <a href="deployment.html">Deployment</a>
        <a href="troubleshooting.html">Troubleshooting</a>
        <a href="changelog.html">Changelog</a>
    </div>
    
    <div class="content">
        {html_content}
    </div>
</body>
</html>"""

def build_documentation():
    """Build HTML documentation from RST files."""
    
    print("Building NOUS documentation...")
    
    # Create build directory
    build_dir = Path("_build/html")
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # RST files to convert
    rst_files = [
        'index.rst',
        'overview.rst',
        'api_reference.rst', 
        'architecture.rst',
        'installation.rst',
        'development.rst',
        'deployment.rst',
        'troubleshooting.rst',
        'changelog.rst'
    ]
    
    # Convert each RST file
    for rst_file in rst_files:
        if os.path.exists(rst_file):
            with open(rst_file, 'r', encoding='utf-8') as f:
                rst_content = f.read()
            
            # Extract title from first line
            title = rst_content.split('\n')[0].strip()
            if not title:
                title = rst_file.replace('.rst', '').replace('_', ' ').title()
            
            # Convert to HTML
            html_content = convert_rst_to_html(rst_content, title)
            
            # Write HTML file
            html_file = rst_file.replace('.rst', '.html')
            with open(build_dir / html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Converted {rst_file} -> {html_file}")
        else:
            print(f"⚠️  File not found: {rst_file}")
    
    # Copy static files
    static_dir = Path("_static")
    if static_dir.exists():
        target_static = build_dir / "_static"
        if target_static.exists():
            shutil.rmtree(target_static)
        shutil.copytree(static_dir, target_static)
        print("✅ Copied static files")
    
    # Create documentation index
    create_main_index(build_dir)
    
    print(f"\n🎉 Documentation built successfully!")
    print(f"📂 Output directory: {build_dir.absolute()}")
    print(f"🌐 Open: {build_dir / 'index.html'}")

def create_main_index(build_dir):
    """Create main documentation index page."""
    
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOUS Personal Assistant Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 3rem;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.25rem;
            opacity: 0.9;
        }
        
        .docs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }
        
        .doc-card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .doc-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }
        
        .doc-card h3 {
            color: #2563eb;
            margin-top: 0;
            font-size: 1.5rem;
        }
        
        .doc-card p {
            color: #6b7280;
            line-height: 1.6;
        }
        
        .doc-card a {
            display: inline-block;
            background: #2563eb;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.2s ease;
        }
        
        .doc-card a:hover {
            background: #1d4ed8;
        }
        
        .footer {
            text-align: center;
            color: white;
            margin-top: 3rem;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NOUS Personal Assistant</h1>
            <p>Comprehensive Documentation Portal</p>
        </div>
        
        <div class="docs-grid">
            <div class="doc-card">
                <h3>📖 System Overview</h3>
                <p>Learn about NOUS architecture, features, and core concepts.</p>
                <a href="overview.html">Read Overview</a>
            </div>
            
            <div class="doc-card">
                <h3>🚀 Installation Guide</h3>
                <p>Step-by-step instructions for setting up NOUS in any environment.</p>
                <a href="installation.html">Get Started</a>
            </div>
            
            <div class="doc-card">
                <h3>🔧 Development Guide</h3>
                <p>Developer documentation, coding standards, and contribution guidelines.</p>
                <a href="development.html">Start Developing</a>
            </div>
            
            <div class="doc-card">
                <h3>📚 API Reference</h3>
                <p>Complete API documentation with examples and schema definitions.</p>
                <a href="api_reference.html">Browse API</a>
            </div>
            
            <div class="doc-card">
                <h3>🏗️ Architecture</h3>
                <p>In-depth system architecture and design patterns.</p>
                <a href="architecture.html">View Architecture</a>
            </div>
            
            <div class="doc-card">
                <h3>🚢 Deployment</h3>
                <p>Production deployment strategies and configuration guides.</p>
                <a href="deployment.html">Deploy Now</a>
            </div>
            
            <div class="doc-card">
                <h3>🔍 Troubleshooting</h3>
                <p>Common issues, solutions, and debugging techniques.</p>
                <a href="troubleshooting.html">Get Help</a>
            </div>
            
            <div class="doc-card">
                <h3>📝 Changelog</h3>
                <p>Version history, new features, and breaking changes.</p>
                <a href="changelog.html">View Changes</a>
            </div>
        </div>
        
        <div class="footer">
            <p>NOUS Personal Assistant v1.0.0 • Built with ❤️ for the community</p>
        </div>
    </div>
</body>
</html>"""
    
    with open(build_dir / "documentation_index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print("✅ Created documentation portal")

if __name__ == "__main__":
    build_documentation()