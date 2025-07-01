#!/usr/bin/env python3
"""
Comprehensive Test Coverage Analyzer
Analyzes codebase for 100% test coverage and generates detailed reports
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime
import importlib.util
import sys
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FunctionInfo:
    """Information about a function"""
    name: str
    file_path: str
    line_number: int
    is_method: bool = False
    class_name: Optional[str] = None
    docstring: Optional[str] = None
    parameters: List[str] = None
    is_tested: bool = False
    test_files: List[str] = None
    complexity_score: int = 0

@dataclass
class ClassInfo:
    """Information about a class"""
    name: str
    file_path: str
    line_number: int
    docstring: Optional[str] = None
    methods: List[str] = None
    is_tested: bool = False
    test_files: List[str] = None

@dataclass
class RouteInfo:
    """Information about a route"""
    path: str
    methods: List[str]
    function_name: str
    file_path: str
    line_number: int
    is_tested: bool = False
    test_files: List[str] = None

@dataclass
class CoverageReport:
    """Comprehensive coverage report"""
    total_functions: int
    tested_functions: int
    total_classes: int
    tested_classes: int
    total_routes: int
    tested_routes: int
    function_coverage_percent: float
    class_coverage_percent: float 
    route_coverage_percent: float
    overall_coverage_percent: float
    untested_functions: List[str]
    untested_classes: List[str]
    untested_routes: List[str]
    missing_test_files: List[str]
    recommendations: List[str]

class ComprehensiveCoverageAnalyzer:
    """Analyzes codebase for comprehensive test coverage"""
    
    def __init__(self):
        self.project_root = Path('.')
        self.functions: Dict[str, FunctionInfo] = {}
        self.classes: Dict[str, ClassInfo] = {}
        self.routes: Dict[str, RouteInfo] = {}
        self.test_files: Set[str] = set()
        self.coverage_report: Optional[CoverageReport] = None
        
        # Skip patterns
        self.skip_patterns = [
            '__pycache__',
            '.git',
            'node_modules',
            'venv',
            '.pytest_cache',
            'build',
            'dist',
            '.egg-info',
            'backup',
            'archive',
            'security_fixes_backup',
            'attached_assets'
        ]
        
    def analyze_comprehensive_coverage(self) -> CoverageReport:
        """Perform comprehensive coverage analysis"""
        logger.info("🔍 Starting comprehensive coverage analysis...")
        
        # Phase 1: Scan all Python files
        logger.info("📁 Phase 1: Scanning Python files...")
        self._scan_python_files()
        
        # Phase 2: Analyze test files
        logger.info("🧪 Phase 2: Analyzing test files...")
        self._analyze_test_files()
        
        # Phase 3: Calculate coverage metrics
        logger.info("📊 Phase 3: Calculating coverage metrics...")
        self._calculate_coverage_metrics()
        
        # Phase 4: Generate recommendations
        logger.info("💡 Phase 4: Generating recommendations...")
        self._generate_recommendations()
        
        # Phase 5: Create comprehensive report
        logger.info("📋 Phase 5: Creating comprehensive report...")
        self._create_coverage_report()
        
        return self.coverage_report
    
    def _scan_python_files(self):
        """Scan all Python files in the project"""
        python_files = list(self.project_root.rglob('*.py'))
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
                
            try:
                self._analyze_python_file(file_path)
            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")
                
        logger.info(f"📁 Scanned {len(python_files)} Python files")
        logger.info(f"🔧 Found {len(self.functions)} functions")
        logger.info(f"🏗️ Found {len(self.classes)} classes")
        logger.info(f"🌐 Found {len(self.routes)} routes")
    
    def _analyze_python_file(self, file_path: Path):
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Extract functions, classes, and routes
            self._extract_functions_from_ast(tree, file_path, content)
            self._extract_classes_from_ast(tree, file_path, content)
            self._extract_routes_from_content(content, file_path)
            
        except Exception as e:
            logger.debug(f"Error parsing {file_path}: {e}")
    
    def _extract_functions_from_ast(self, tree: ast.AST, file_path: Path, content: str):
        """Extract function information from AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = FunctionInfo(
                    name=node.name,
                    file_path=str(file_path),
                    line_number=node.lineno,
                    docstring=ast.get_docstring(node),
                    parameters=[arg.arg for arg in node.args.args],
                    complexity_score=self._calculate_complexity(node),
                    test_files=[]
                )
                
                # Check if it's a method
                for parent in ast.walk(tree):
                    if isinstance(parent, ast.ClassDef):
                        for child in ast.walk(parent):
                            if child is node:
                                func_info.is_method = True
                                func_info.class_name = parent.name
                                break
                
                func_key = f"{file_path}::{node.name}"
                self.functions[func_key] = func_info
    
    def _extract_classes_from_ast(self, tree: ast.AST, file_path: Path, content: str):
        """Extract class information from AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        methods.append(child.name)
                
                class_info = ClassInfo(
                    name=node.name,
                    file_path=str(file_path),
                    line_number=node.lineno,
                    docstring=ast.get_docstring(node),
                    methods=methods,
                    test_files=[]
                )
                
                class_key = f"{file_path}::{node.name}"
                self.classes[class_key] = class_info
    
    def _extract_routes_from_content(self, content: str, file_path: Path):
        """Extract Flask route information from file content"""
        # Pattern to match Flask routes
        route_pattern = r'@\w*\.route\(["\']([^"\']+)["\'](?:,\s*methods\s*=\s*\[([^\]]+)\])?\)'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            match = re.search(route_pattern, line)
            if match:
                route_path = match.group(1)
                methods_str = match.group(2) if match.group(2) else '"GET"'
                methods = [m.strip().strip('"\'') for m in methods_str.split(',')]
                
                # Find the function name (next non-decorator line)
                func_name = None
                for j in range(i + 1, min(i + 5, len(lines))):
                    func_match = re.search(r'def\s+(\w+)\s*\(', lines[j])
                    if func_match:
                        func_name = func_match.group(1)
                        break
                
                if func_name:
                    route_info = RouteInfo(
                        path=route_path,
                        methods=methods,
                        function_name=func_name,
                        file_path=str(file_path),
                        line_number=i + 1,
                        test_files=[]
                    )
                    
                    route_key = f"{route_path}::{func_name}"
                    self.routes[route_key] = route_info
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate complexity score for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity
    
    def _analyze_test_files(self):
        """Analyze test files to determine what's tested"""
        test_files = list(self.project_root.rglob('test_*.py')) + list(self.project_root.rglob('*_test.py'))
        test_files.extend(list((self.project_root / 'tests').rglob('*.py')))
        
        for test_file in test_files:
            if self._should_skip_file(test_file):
                continue
                
            self.test_files.add(str(test_file))
            
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                self._analyze_test_content(content, test_file)
                
            except Exception as e:
                logger.debug(f"Error analyzing test file {test_file}: {e}")
        
        logger.info(f"🧪 Analyzed {len(self.test_files)} test files")
    
    def _analyze_test_content(self, content: str, test_file: Path):
        """Analyze test file content to identify what's being tested"""
        # Look for imports and function calls that indicate testing
        
        # Check for function testing
        for func_key, func_info in self.functions.items():
            if func_info.name in content:
                func_info.is_tested = True
                func_info.test_files.append(str(test_file))
        
        # Check for class testing
        for class_key, class_info in self.classes.items():
            if class_info.name in content:
                class_info.is_tested = True
                class_info.test_files.append(str(test_file))
        
        # Check for route testing (HTTP client calls)
        for route_key, route_info in self.routes.items():
            if route_info.path in content or route_info.function_name in content:
                route_info.is_tested = True
                route_info.test_files.append(str(test_file))
    
    def _calculate_coverage_metrics(self):
        """Calculate coverage metrics"""
        # Function coverage
        tested_functions = sum(1 for f in self.functions.values() if f.is_tested)
        function_coverage = (tested_functions / len(self.functions)) * 100 if self.functions else 0
        
        # Class coverage
        tested_classes = sum(1 for c in self.classes.values() if c.is_tested)
        class_coverage = (tested_classes / len(self.classes)) * 100 if self.classes else 0
        
        # Route coverage
        tested_routes = sum(1 for r in self.routes.values() if r.is_tested)
        route_coverage = (tested_routes / len(self.routes)) * 100 if self.routes else 0
        
        # Overall coverage (weighted average)
        total_items = len(self.functions) + len(self.classes) + len(self.routes)
        tested_items = tested_functions + tested_classes + tested_routes
        overall_coverage = (tested_items / total_items) * 100 if total_items else 0
        
        logger.info(f"📊 Function Coverage: {function_coverage:.1f}% ({tested_functions}/{len(self.functions)})")
        logger.info(f"📊 Class Coverage: {class_coverage:.1f}% ({tested_classes}/{len(self.classes)})")
        logger.info(f"📊 Route Coverage: {route_coverage:.1f}% ({tested_routes}/{len(self.routes)})")
        logger.info(f"📊 Overall Coverage: {overall_coverage:.1f}%")
    
    def _generate_recommendations(self):
        """Generate recommendations for improving coverage"""
        recommendations = []
        
        # High-priority untested functions
        untested_functions = [f for f in self.functions.values() if not f.is_tested]
        high_complexity_untested = [f for f in untested_functions if f.complexity_score > 3]
        
        if high_complexity_untested:
            recommendations.append(f"PRIORITY: Test {len(high_complexity_untested)} high-complexity functions")
        
        # Critical routes without tests
        untested_routes = [r for r in self.routes.values() if not r.is_tested]
        api_routes = [r for r in untested_routes if '/api/' in r.path]
        
        if api_routes:
            recommendations.append(f"CRITICAL: Test {len(api_routes)} API routes")
        
        # Classes without tests
        untested_classes = [c for c in self.classes.values() if not c.is_tested]
        model_classes = [c for c in untested_classes if 'model' in c.file_path.lower()]
        
        if model_classes:
            recommendations.append(f"IMPORTANT: Test {len(model_classes)} model classes")
        
        # Missing test files for modules
        module_files = set()
        for func in self.functions.values():
            module_files.add(Path(func.file_path).stem)
        
        test_file_modules = set()
        for test_file in self.test_files:
            test_file_modules.add(Path(test_file).stem.replace('test_', '').replace('_test', ''))
        
        missing_test_modules = module_files - test_file_modules
        if missing_test_modules:
            recommendations.append(f"CREATE: Test files for {len(missing_test_modules)} modules")
        
        self.recommendations = recommendations
    
    def _create_coverage_report(self):
        """Create comprehensive coverage report"""
        tested_functions = sum(1 for f in self.functions.values() if f.is_tested)
        tested_classes = sum(1 for c in self.classes.values() if c.is_tested)
        tested_routes = sum(1 for r in self.routes.values() if r.is_tested)
        
        untested_functions = [f"{f.file_path}::{f.name}" for f in self.functions.values() if not f.is_tested]
        untested_classes = [f"{c.file_path}::{c.name}" for c in self.classes.values() if not c.is_tested]
        untested_routes = [f"{r.path} ({r.function_name})" for r in self.routes.values() if not r.is_tested]
        
        # Calculate coverage percentages
        function_coverage = (tested_functions / len(self.functions)) * 100 if self.functions else 0
        class_coverage = (tested_classes / len(self.classes)) * 100 if self.classes else 0
        route_coverage = (tested_routes / len(self.routes)) * 100 if self.routes else 0
        
        total_items = len(self.functions) + len(self.classes) + len(self.routes)
        tested_items = tested_functions + tested_classes + tested_routes
        overall_coverage = (tested_items / total_items) * 100 if total_items else 0
        
        self.coverage_report = CoverageReport(
            total_functions=len(self.functions),
            tested_functions=tested_functions,
            total_classes=len(self.classes),
            tested_classes=tested_classes,
            total_routes=len(self.routes),
            tested_routes=tested_routes,
            function_coverage_percent=function_coverage,
            class_coverage_percent=class_coverage,
            route_coverage_percent=route_coverage,
            overall_coverage_percent=overall_coverage,
            untested_functions=untested_functions[:20],  # Limit to first 20
            untested_classes=untested_classes[:20],
            untested_routes=untested_routes[:20],
            missing_test_files=list(self.test_files),
            recommendations=self.recommendations
        )
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        path_str = str(file_path)
        return any(pattern in path_str for pattern in self.skip_patterns)
    
    def generate_detailed_report(self) -> str:
        """Generate detailed coverage report"""
        if not self.coverage_report:
            return "No coverage report available"
        
        report = f"""
# Comprehensive Test Coverage Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Coverage Summary
- **Overall Coverage**: {self.coverage_report.overall_coverage_percent:.1f}%
- **Function Coverage**: {self.coverage_report.function_coverage_percent:.1f}% ({self.coverage_report.tested_functions}/{self.coverage_report.total_functions})
- **Class Coverage**: {self.coverage_report.class_coverage_percent:.1f}% ({self.coverage_report.tested_classes}/{self.coverage_report.total_classes})
- **Route Coverage**: {self.coverage_report.route_coverage_percent:.1f}% ({self.coverage_report.tested_routes}/{self.coverage_report.total_routes})

## Priority Recommendations
"""
        
        for i, rec in enumerate(self.coverage_report.recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += f"""
## Untested Functions (Top 20)
"""
        for func in self.coverage_report.untested_functions:
            report += f"- {func}\n"
        
        report += f"""
## Untested Classes (Top 20)
"""
        for cls in self.coverage_report.untested_classes:
            report += f"- {cls}\n"
        
        report += f"""
## Untested Routes (Top 20)
"""
        for route in self.coverage_report.untested_routes:
            report += f"- {route}\n"
        
        return report
    
    def save_report(self, filename: str = None):
        """Save coverage report to file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'coverage_report_{timestamp}.json'
        
        report_data = {
            'coverage_report': asdict(self.coverage_report),
            'detailed_functions': {k: asdict(v) for k, v in self.functions.items()},
            'detailed_classes': {k: asdict(v) for k, v in self.classes.items()},
            'detailed_routes': {k: asdict(v) for k, v in self.routes.items()},
            'test_files': list(self.test_files),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"📋 Coverage report saved to {filename}")
        
        # Also save markdown report
        md_filename = filename.replace('.json', '.md')
        with open(md_filename, 'w') as f:
            f.write(self.generate_detailed_report())
        
        logger.info(f"📋 Detailed report saved to {md_filename}")

def main():
    """Main function"""
    print("🔍 Comprehensive Test Coverage Analyzer")
    print("=" * 60)
    
    analyzer = ComprehensiveCoverageAnalyzer()
    
    try:
        # Perform analysis
        coverage_report = analyzer.analyze_comprehensive_coverage()
        
        # Generate and save reports
        analyzer.save_report()
        
        # Print summary
        print("\n📊 COVERAGE ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"Overall Coverage: {coverage_report.overall_coverage_percent:.1f}%")
        print(f"Functions: {coverage_report.tested_functions}/{coverage_report.total_functions}")
        print(f"Classes: {coverage_report.tested_classes}/{coverage_report.total_classes}")
        print(f"Routes: {coverage_report.tested_routes}/{coverage_report.total_routes}")
        
        if coverage_report.overall_coverage_percent < 100:
            print(f"\n🎯 TO ACHIEVE 100% COVERAGE:")
            for rec in coverage_report.recommendations:
                print(f"  • {rec}")
        else:
            print(f"\n🎉 CONGRATULATIONS! 100% COVERAGE ACHIEVED!")
        
        return coverage_report.overall_coverage_percent >= 100
        
    except Exception as e:
        logger.error(f"Error in coverage analysis: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)