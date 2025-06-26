#!/usr/bin/env python
"""
API Documentation Generator

This tool generates comprehensive API documentation based on the standardized
route definitions across the NOUS application.

Usage:
    python tools/generate_api_docs.py [--format FORMAT] [--output FILE]

Options:
    --format FORMAT  Output format: html, markdown, openapi (default: html)
    --output FILE    Write output to file instead of stdout
    --help           Show this help message and exit
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path

# Add parent directory to path to import application
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def setup_logging():
    """Configure logging for the documentation generator"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger('api_doc_generator')

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Generate API documentation')
    parser.add_argument('--format', choices=['html', 'markdown', 'openapi'], default='html',
                       help='Output format (default: html)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output file (default: stdout)')
    
    return parser.parse_args()

def create_app_context():
    """Create application context for generating documentation"""
    try:
        # Import app differently based on how the project is structured
        try:
            from app import app
        except ImportError:
            from app import create_app
            app = create_app()
            
        return app
    except Exception as e:
        logger.error(f"Failed to create application context: {str(e)}")
        sys.exit(1)

def generate_openapi_spec(app):
    """Generate OpenAPI specification from the application"""
    try:
        from api_documentation import generate_openapi_spec
        return generate_openapi_spec(app)
    except ImportError:
        logger.error("API documentation generator not found. Make sure api_documentation.py exists.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error generating OpenAPI spec: {str(e)}")
        sys.exit(1)

def generate_markdown_docs(openapi_spec):
    """Convert OpenAPI spec to Markdown documentation"""
    try:
        markdown = ["# NOUS API Documentation\n"]
        
        # Add info section
        info = openapi_spec.get('info', {})
        markdown.append(f"## {info.get('title', 'API Documentation')}\n")
        markdown.append(f"{info.get('description', '')}\n")
        markdown.append(f"**Version:** {info.get('version', '1.0.0')}\n\n")
        
        # Add each endpoint
        markdown.append("## Endpoints\n")
        
        for path, path_item in sorted(openapi_spec.get('paths', {}).items()):
            markdown.append(f"### {path}\n")
            
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    markdown.append(f"#### {method.upper()}\n")
                    markdown.append(f"{operation.get('summary', '')}\n")
                    markdown.append(f"{operation.get('description', '')}\n")
                    
                    # Parameters
                    params = operation.get('parameters', [])
                    if params:
                        markdown.append("\n**Parameters:**\n")
                        for param in params:
                            markdown.append(f"- `{param.get('name', '')}` ({param.get('in', '')}): {param.get('description', '')}\n")
                    
                    # Request body
                    req_body = operation.get('requestBody', {})
                    if req_body:
                        markdown.append("\n**Request Body:**\n")
                        content = req_body.get('content', {})
                        for content_type, content_schema in content.items():
                            markdown.append(f"Content Type: `{content_type}`\n")
                            
                            schema = content_schema.get('schema', {})
                            if schema.get('type') == 'object' and 'properties' in schema:
                                markdown.append("\n```json\n")
                                example = {}
                                for prop_name, prop in schema.get('properties', {}).items():
                                    example[prop_name] = prop.get('example', '')
                                markdown.append(json.dumps(example, indent=2))
                                markdown.append("\n```\n")
                    
                    # Responses
                    responses = operation.get('responses', {})
                    if responses:
                        markdown.append("\n**Responses:**\n")
                        for status, response in responses.items():
                            markdown.append(f"- `{status}`: {response.get('description', '')}\n")
                    
                    markdown.append("\n")
        
        return "\n".join(markdown)
        
    except Exception as e:
        logger.error(f"Error generating Markdown: {str(e)}")
        return f"# Error Generating Documentation\n\nAn error occurred: {str(e)}"

def generate_html_docs(openapi_spec):
    """Convert OpenAPI spec to HTML documentation"""
    try:
        # Use Markdown as an intermediate format and convert to HTML
        markdown_content = generate_markdown_docs(openapi_spec)
        
        # Basic HTML template
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{openapi_spec.get('info', {}).get('title', 'NOUS API Documentation')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
        }}
        header {{
            margin-bottom: 2rem;
            border-bottom: 1px solid #eee;
            padding-bottom: 1rem;
        }}
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        h2 {{
            font-size: 2rem;
            margin-top: 2rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #eee;
        }}
        h3 {{
            font-size: 1.5rem;
            margin-top: 1.5rem;
            background-color: #f8f8f8;
            padding: 0.5rem;
            border-radius: 3px;
        }}
        h4 {{
            font-size: 1.2rem;
            margin-top: 1rem;
            text-transform: uppercase;
            color: #555;
        }}
        code {{
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            background-color: #f0f0f0;
            font-size: 85%;
        }}
        pre {{
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 1rem;
            overflow: auto;
        }}
        blockquote {{
            margin: 1rem 0;
            padding: 0.5rem 1rem;
            border-left: 4px solid #ddd;
            color: #666;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }}
        table, th, td {{
            border: 1px solid #ddd;
        }}
        th, td {{
            padding: 0.5rem;
            text-align: left;
        }}
        th {{
            background-color: #f0f0f0;
        }}
        .method {{
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            font-weight: bold;
            margin-right: 0.5rem;
        }}
        .get {{
            background-color: #e7f0f7;
            color: #0062cc;
        }}
        .post {{
            background-color: #e8f6e8;
            color: #28a745;
        }}
        .put {{
            background-color: #fff6e5;
            color: #ffa000;
        }}
        .delete {{
            background-color: #fcebeb;
            color: #dc3545;
        }}
        .patch {{
            background-color: #e8f0ff;
            color: #6610f2;
        }}
    </style>
</head>
<body>
    <header>
        <h1>{openapi_spec.get('info', {}).get('title', 'NOUS API Documentation')}</h1>
        <p>{openapi_spec.get('info', {}).get('description', '')}</p>
        <p><strong>Version:</strong> {openapi_spec.get('info', {}).get('version', '1.0.0')}</p>
    </header>
    <main>
        <!-- Generated Documentation -->
        {markdown_to_html(markdown_content)}
    </main>
    <footer>
        <p>Generated on {import_datetime().now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </footer>
</body>
</html>
"""
        return html
    except Exception as e:
        logger.error(f"Error generating HTML: {str(e)}")
        return f"<html><body><h1>Error Generating Documentation</h1><p>An error occurred: {str(e)}</p></body></html>"

def markdown_to_html(markdown_content):
    """Convert Markdown to HTML using basic replacements (simplified)"""
    # This is a very simplified conversion - in production you would use a proper markdown parser
    html = markdown_content
    
    # Headers
    html = html.replace("# ", "<h1>").replace("\n## ", "\n<h2>").replace("\n### ", "\n<h3>").replace("\n#### ", "\n<h4>")
    html = html.replace("\n</h1>", "</h1>\n").replace("\n</h2>", "</h2>\n").replace("\n</h3>", "</h3>\n").replace("\n</h4>", "</h4>\n")
    
    # Add header closing tags
    for tag in ['h1', 'h2', 'h3', 'h4']:
        for line in html.split('\n'):
            if line.startswith(f"<{tag}>") and not line.endswith(f"</{tag}>"):
                html = html.replace(line, f"{line}</{tag}>")
    
    # Code blocks
    while "```" in html:
        start = html.find("```")
        end = html.find("```", start + 3)
        if end != -1:
            code_content = html[start+3:end].strip()
            if "\n" in code_content:  # Multi-line code
                language, *code_lines = code_content.split("\n", 1)
                if len(code_lines) > 0:
                    code_content = code_lines[0]
                else:
                    code_content = ""
            html = html[:start] + f"<pre><code>{code_content}</code></pre>" + html[end+3:]
        else:
            break
    
    # Inline code
    while "`" in html:
        start = html.find("`")
        end = html.find("`", start + 1)
        if end != -1:
            code_content = html[start+1:end]
            html = html[:start] + f"<code>{code_content}</code>" + html[end+1:]
        else:
            break
    
    # Lists
    lines = html.split('\n')
    for i in range(len(lines)):
        if lines[i].strip().startswith('- '):
            lines[i] = lines[i].replace('- ', '<li>', 1) + '</li>'
    
    # Wrap lists in <ul> tags
    in_list = False
    for i in range(len(lines)):
        if lines[i].strip().startswith('<li>') and not in_list:
            lines[i] = '<ul>' + lines[i]
            in_list = True
        elif not lines[i].strip().startswith('<li>') and in_list:
            lines[i-1] = lines[i-1] + '</ul>'
            in_list = False
    
    # Close list if it's the last element
    if in_list:
        lines.append('</ul>')
    
    # Bold text
    html = '\n'.join(lines)
    while "**" in html:
        start = html.find("**")
        end = html.find("**", start + 2)
        if end != -1:
            bold_content = html[start+2:end]
            html = html[:start] + f"<strong>{bold_content}</strong>" + html[end+2:]
        else:
            break
    
    # Paragraphs
    html = html.replace("\n\n", "\n<p>\n")
    
    return html

def import_datetime():
    """Import datetime module on demand"""
    import datetime
    return datetime

def output_docs(docs, args):
    """Output the documentation to stdout or file"""
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(docs)
            logger.info(f"Documentation written to {args.output}")
        except Exception as e:
            logger.error(f"Failed to write documentation to {args.output}: {str(e)}")
            sys.exit(1)
    else:
        # Output to stdout
        print(docs)

if __name__ == '__main__':
    # Set up logging
    logger = setup_logging()
    
    # Parse arguments
    args = parse_arguments()
    
    # Create application context
    logger.info("Creating application context...")
    app = create_app_context()
    
    # Generate OpenAPI specification
    logger.info("Generating OpenAPI specification...")
    openapi_spec = generate_openapi_spec(app)
    
    # Generate documentation in requested format
    if args.format == 'openapi':
        logger.info("Using raw OpenAPI specification as output...")
        docs = json.dumps(openapi_spec, indent=2)
    elif args.format == 'markdown':
        logger.info("Converting to Markdown documentation...")
        docs = generate_markdown_docs(openapi_spec)
    else:  # html is default
        logger.info("Converting to HTML documentation...")
        docs = generate_html_docs(openapi_spec)
    
    # Output documentation
    output_docs(docs, args)
    
    logger.info("Documentation generation complete.")