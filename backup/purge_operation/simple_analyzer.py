#!/usr/bin/env python3
"""
Simple Codebase Analyzer for OPERATION: TOTAL CODEBASE PURGE-AND-REBUILD
"""

import os
import ast
import json
import hashlib
from pathlib import Path
from collections import defaultdict
import re

def analyze_codebase():
    """Main analysis function"""
    print("🚀 Starting codebase analysis...")
    
    # File discovery
    source_extensions = {'.py', '.js', '.ts', '.html', '.sql', '.yaml', '.yml', '.mdx'}
    files_data = []
    
    # Scan files
    for file_path in Path('.').rglob('*'):
        if file_path.is_file() and file_path.suffix in source_extensions:
            # Skip backup and cache directories
            if any(part.startswith('.') or part in ['backup', '__pycache__', 'node_modules'] 
                  for part in file_path.parts):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                file_hash = hashlib.md5(content.encode()).hexdigest()
                
                files_data.append({
                    'path': str(file_path),
                    'hash': file_hash,
                    'size': len(content),
                    'type': file_path.suffix,
                    'content': content
                })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    print(f"📁 Found {len(files_data)} source files")
    
    # Analyze Python files for routes and models
    routes = []
    models = []
    chat_handlers = []
    imports_map = {}
    
    for file_data in files_data:
        if file_data['type'] == '.py':
            try:
                tree = ast.parse(file_data['content'])
                file_path = file_data['path']
                
                # Extract routes
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check for route decorators
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Call):
                                if hasattr(decorator.func, 'attr') and decorator.func.attr == 'route':
                                    route_path = ""
                                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                                        route_path = decorator.args[0].value
                                    
                                    routes.append({
                                        'path': route_path,
                                        'function': node.name,
                                        'file': file_path
                                    })
                        
                        # Check for chat handlers
                        if (node.name.startswith(('cmd_', 'handle_', 'chat_')) or 
                            'chat' in node.name.lower()):
                            chat_handlers.append({
                                'function': node.name,
                                'file': file_path,
                                'line': node.lineno
                            })
                
                # Extract models
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's a model
                        for base in node.bases:
                            if (hasattr(base, 'attr') and base.attr == 'Model') or \
                               (hasattr(base, 'id') and base.id in ['Model', 'Base']):
                                models.append({
                                    'name': node.name,
                                    'file': file_path
                                })
                                break
                
                # Extract imports
                file_imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            file_imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            file_imports.append(node.module)
                
                imports_map[file_path] = file_imports
                
            except Exception as e:
                print(f"Error analyzing {file_data['path']}: {e}")
    
    # Find duplicates
    hash_groups = defaultdict(list)
    for file_data in files_data:
        hash_groups[file_data['hash']].append(file_data['path'])
    
    duplicates = {k: v for k, v in hash_groups.items() if len(v) > 1}
    
    # Find dead files (simplified)
    referenced_files = set()
    for route in routes:
        referenced_files.add(route['file'])
    for model in models:
        referenced_files.add(model['file'])
    
    all_files = {f['path'] for f in files_data}
    dead_files = list(all_files - referenced_files)
    
    # Build final graph
    codegraph = {
        'files': len(files_data),
        'routes': routes,
        'models': models,
        'chat_handlers': chat_handlers,
        'duplicates': duplicates,
        'dead_files': dead_files,
        'imports': imports_map,
        'summary': {
            'total_files': len(files_data),
            'python_files': len([f for f in files_data if f['type'] == '.py']),
            'routes_found': len(routes),
            'models_found': len(models),
            'chat_handlers': len(chat_handlers),
            'duplicate_groups': len(duplicates),
            'potentially_dead': len(dead_files)
        }
    }
    
    # Save to /tmp/codegraph.json
    os.makedirs('/tmp', exist_ok=True)
    with open('/tmp/codegraph.json', 'w') as f:
        json.dump(codegraph, f, indent=2)
    
    print("📊 ANALYSIS COMPLETE")
    print(f"📁 Total files: {codegraph['summary']['total_files']}")
    print(f"🐍 Python files: {codegraph['summary']['python_files']}")
    print(f"🛣️  Routes: {codegraph['summary']['routes_found']}")
    print(f"🗄️  Models: {codegraph['summary']['models_found']}")
    print(f"💬 Chat handlers: {codegraph['summary']['chat_handlers']}")
    print(f"🔄 Duplicate groups: {codegraph['summary']['duplicate_groups']}")
    print(f"💀 Potentially dead: {codegraph['summary']['potentially_dead']}")
    
    if duplicates:
        print("\n🔄 DUPLICATE FILES:")
        for hash_val, paths in list(duplicates.items())[:5]:
            print(f"  {hash_val[:8]}... -> {', '.join(paths)}")
    
    if dead_files:
        print("\n💀 POTENTIALLY DEAD FILES (first 10):")
        for dead_file in dead_files[:10]:
            print(f"  {dead_file}")
    
    print(f"\n✅ Code graph saved to /tmp/codegraph.json")
    
    return codegraph

if __name__ == "__main__":
    analyze_codebase()