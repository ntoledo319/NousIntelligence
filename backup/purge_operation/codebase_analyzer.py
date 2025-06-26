#!/usr/bin/env python3
"""
Codebase Analyzer for OPERATION: TOTAL CODEBASE PURGE-AND-REBUILD
Recursively scans and builds AST graph mapping for comprehensive refactoring
"""

import os
import ast
import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple
from dataclasses import dataclass, asdict
import re

@dataclass
class FileInfo:
    path: str
    hash: str
    size: int
    modified: float
    type: str
    
@dataclass 
class RouteInfo:
    path: str
    methods: List[str]
    function: str
    blueprint: str
    file: str
    
@dataclass
class ModelInfo:
    name: str
    table: str
    fields: List[str]
    file: str
    
@dataclass
class CodeGraph:
    files: List[FileInfo]
    routes: List[RouteInfo]
    models: List[ModelInfo]
    duplicates: Dict[str, List[str]]
    dead_files: List[str]
    chat_handlers: List[Dict[str, Any]]
    imports: Dict[str, List[str]]

class CodebaseAnalyzer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.graph = CodeGraph([], [], [], {}, [], [], {})
        self.source_extensions = {'.py', '.js', '.ts', '.html', '.sql', '.yaml', '.yml', '.mdx'}
        
    def scan_files(self) -> None:
        """Recursively scan all source files"""
        print("🔍 Scanning source files...")
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.source_extensions:
                # Skip backup and cache directories
                if any(part.startswith('.') or part in ['backup', '__pycache__', 'node_modules'] 
                      for part in file_path.parts):
                    continue
                    
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    file_hash = hashlib.md5(content.encode()).hexdigest()
                    
                    file_info = FileInfo(
                        path=str(file_path.relative_to(self.root_path)),
                        hash=file_hash,
                        size=len(content),
                        modified=file_path.stat().st_mtime,
                        type=file_path.suffix
                    )
                    self.graph.files.append(file_info)
                    
                except Exception as e:
                    print(f"⚠️  Error reading {file_path}: {e}")
                    
        print(f"📁 Found {len(self.graph.files)} source files")
        
    def analyze_python_files(self) -> None:
        """Analyze Python files for routes, models, and handlers"""
        print("🐍 Analyzing Python files...")
        
        for file_info in self.graph.files:
            if file_info.type != '.py':
                continue
                
            try:
                file_path = self.root_path / file_info.path
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Parse AST
                tree = ast.parse(content)
                
                # Find routes
                self._extract_routes(tree, file_info.path, content)
                
                # Find models
                self._extract_models(tree, file_info.path)
                
                # Find chat handlers
                self._extract_chat_handlers(tree, file_info.path, content)
                
                # Extract imports
                self._extract_imports(tree, file_info.path)
                
            except Exception as e:
                print(f"⚠️  Error analyzing {file_info.path}: {e}")
                
    def _extract_routes(self, tree: ast.AST, file_path: str, content: str) -> None:
        """Extract Flask routes from AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for route decorators
                for decorator in node.decorator_list:
                    route_info = self._parse_route_decorator(decorator, node.name, file_path, content)
                    if route_info:
                        self.graph.routes.append(route_info)
                        
    def _parse_route_decorator(self, decorator: ast.AST, func_name: str, file_path: str, content: str) -> RouteInfo:
        """Parse route decorator to extract route info"""
        try:
            if isinstance(decorator, ast.Call):
                if hasattr(decorator.func, 'attr') and decorator.func.attr == 'route':
                    # Extract route path
                    path = ""
                    methods = ["GET"]
                    
                    if decorator.args:
                        if isinstance(decorator.args[0], ast.Constant):
                            path = decorator.args[0].value
                            
                    # Extract methods from keywords
                    for keyword in decorator.keywords:
                        if keyword.arg == 'methods':
                            if isinstance(keyword.value, ast.List):
                                methods = [elt.value for elt in keyword.value 
                                         if isinstance(elt, ast.Constant)]
                                         
                    # Determine blueprint
                    blueprint = self._extract_blueprint_name(content, file_path)
                    
                    return RouteInfo(
                        path=path,
                        methods=methods,
                        function=func_name,
                        blueprint=blueprint,
                        file=file_path
                    )
        except Exception:
            pass
        return None
        
    def _extract_blueprint_name(self, content: str, file_path: str) -> str:
        """Extract blueprint name from file content"""
        # Look for Blueprint creation
        blueprint_pattern = r'(\w+)\s*=\s*Blueprint\s*\('
        match = re.search(blueprint_pattern, content)
        if match:
            return match.group(1)
        
        # Fallback to file-based naming
        return Path(file_path).stem
        
    def _extract_models(self, tree: ast.AST, file_path: str) -> None:
        """Extract SQLAlchemy models from AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a model (inherits from db.Model or similar)
                for base in node.bases:
                    if (hasattr(base, 'attr') and base.attr == 'Model') or \
                       (hasattr(base, 'id') and base.id in ['Model', 'Base']):
                        
                        fields = []
                        table_name = ""
                        
                        # Extract fields and table name
                        for class_node in node.body:
                            if isinstance(class_node, ast.Assign):
                                for target in class_node.targets:
                                    if isinstance(target, ast.Name):
                                        if target.id == '__tablename__':
                                            if isinstance(class_node.value, ast.Constant):
                                                table_name = class_node.value.value
                                        elif hasattr(class_node.value, 'func'):
                                            # This is likely a Column
                                            fields.append(target.id)
                                            
                        model_info = ModelInfo(
                            name=node.name,
                            table=table_name or node.name.lower(),
                            fields=fields,
                            file=file_path
                        )
                        self.graph.models.append(model_info)
                        
    def _extract_chat_handlers(self, tree: ast.AST, file_path: str, content: str) -> None:
        """Extract potential chat handlers"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for chat handler patterns
                is_handler = False
                handler_type = ""
                
                # Check decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        if 'chat' in decorator.id.lower():
                            is_handler = True
                            handler_type = "decorator"
                            
                # Check function name patterns
                if node.name.startswith(('cmd_', 'handle_', 'chat_')):
                    is_handler = True
                    handler_type = "naming"
                    
                if is_handler:
                    self.graph.chat_handlers.append({
                        'function': node.name,
                        'file': file_path,
                        'type': handler_type,
                        'line': node.lineno
                    })
                    
    def _extract_imports(self, tree: ast.AST, file_path: str) -> None:
        """Extract import dependencies"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
                    
        self.graph.imports[file_path] = imports
        
    def find_duplicates(self) -> None:
        """Find duplicate files by hash"""
        print("🔍 Finding duplicate files...")
        
        hash_map = {}
        for file_info in self.graph.files:
            if file_info.hash not in hash_map:
                hash_map[file_info.hash] = []
            hash_map[file_info.hash].append(file_info.path)
            
        # Find files with >90% similarity (for now, exact hash matches)
        for file_hash, file_paths in hash_map.items():
            if len(file_paths) > 1:
                self.graph.duplicates[file_hash] = file_paths
                
        print(f"🔄 Found {len(self.graph.duplicates)} duplicate groups")
        
    def find_dead_files(self) -> None:
        """Find files never referenced anywhere"""
        print("🗑️  Finding dead files...")
        
        referenced_files = set()
        
        # Files referenced in imports
        for file_path, imports in self.graph.imports.items():
            for imp in imports:
                # Convert import to potential file path
                potential_paths = [
                    f"{imp.replace('.', '/')}.py",
                    f"{imp.replace('.', '/')/__init__.py"
                ]
                for potential in potential_paths:
                    if any(f.path == potential for f in self.graph.files):
                        referenced_files.add(potential)
                        
        # Files with routes are likely referenced
        for route in self.graph.routes:
            referenced_files.add(route.file)
            
        # Models are likely referenced
        for model in self.graph.models:
            referenced_files.add(model.file)
            
        # Mark unreferenced files as dead
        all_files = {f.path for f in self.graph.files}
        self.graph.dead_files = list(all_files - referenced_files)
        
        print(f"💀 Found {len(self.graph.dead_files)} potentially dead files")
        
    def save_graph(self, output_path: str = "/tmp/codegraph.json") -> None:
        """Save code graph to JSON"""
        print(f"💾 Saving code graph to {output_path}")
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(asdict(self.graph), f, indent=2, default=str)
            print("✅ Code graph saved successfully")
        except Exception as e:
            print(f"❌ Error saving code graph: {e}")
            
    def print_summary(self) -> None:
        """Print analysis summary"""
        print("\n" + "="*60)
        print("📊 CODEBASE ANALYSIS SUMMARY")
        print("="*60)
        print(f"📁 Total files: {len(self.graph.files)}")
        print(f"🛣️  Routes found: {len(self.graph.routes)}")
        print(f"🗄️  Models found: {len(self.graph.models)}")
        print(f"💬 Chat handlers: {len(self.graph.chat_handlers)}")
        print(f"🔄 Duplicate groups: {len(self.graph.duplicates)}")
        print(f"💀 Dead files: {len(self.graph.dead_files)}")
        
        if self.graph.duplicates:
            print("\n🔄 DUPLICATES:")
            for hash_val, paths in self.graph.duplicates.items():
                print(f"  {hash_val[:8]}... -> {', '.join(paths)}")
                
        if self.graph.dead_files:
            print("\n💀 POTENTIALLY DEAD FILES:")
            for dead_file in self.graph.dead_files[:10]:  # Show first 10
                print(f"  {dead_file}")
            if len(self.graph.dead_files) > 10:
                print(f"  ... and {len(self.graph.dead_files) - 10} more")

def main():
    analyzer = CodebaseAnalyzer()
    
    print("🚀 Starting TOTAL CODEBASE PURGE-AND-REBUILD analysis...")
    
    # Step 1: Scan all files
    analyzer.scan_files()
    
    # Step 2: Analyze Python files for routes, models, etc.
    analyzer.analyze_python_files()
    
    # Step 3: Find duplicates
    analyzer.find_duplicates()
    
    # Step 4: Find dead files
    analyzer.find_dead_files()
    
    # Step 5: Save graph
    analyzer.save_graph()
    
    # Step 6: Print summary
    analyzer.print_summary()
    
    print("\n✅ GLOBAL CRAWL COMPLETE")

if __name__ == "__main__":
    main()