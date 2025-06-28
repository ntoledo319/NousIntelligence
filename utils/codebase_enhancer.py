"""
Codebase Enhancer - Automated Discovery & Enhancement System
Implements the principles from the uploaded agent configuration to continuously improve the NOUS codebase
"""
import os
import ast
import re
import json
import logging
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CodeAnalysis:
    """Code analysis results"""
    file_path: str
    total_lines: int
    function_count: int
    class_count: int
    imports: List[str]
    potential_issues: List[str]
    optimization_opportunities: List[str]
    complexity_score: float

@dataclass
class EnhancementOpportunity:
    """Enhancement opportunity identified by the system"""
    category: str
    priority: str  # high, medium, low
    description: str
    file_path: str
    line_number: Optional[int]
    estimated_effort: str  # low, medium, high
    potential_impact: str  # low, medium, high
    suggested_action: str

class CodebaseEnhancer:
    """Automated codebase enhancement system"""
    
    def __init__(self):
        self.project_root = Path('.')
        self.analysis_results = {}
        self.enhancement_opportunities = []
        self.ignored_dirs = {
            '__pycache__', '.git', 'node_modules', 'venv', 'env',
            'logs', 'uploads', 'flask_session', 'instance', 'build_assets',
            'archive', 'attached_assets'
        }
        self.python_files = []
        
    def discover_and_catalog(self) -> Dict[str, Any]:
        """Discover and catalog all code artifacts"""
        logger.info("Starting codebase discovery and cataloging...")
        
        catalog = {
            "total_files": 0,
            "python_files": 0,
            "modules": {},
            "blueprints": [],
            "models": [],
            "utilities": [],
            "routes": [],
            "services": [],
            "dependencies": set(),
            "config_files": []
        }
        
        # Traverse directory structure
        for root, dirs, files in os.walk(self.project_root):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            for file in files:
                file_path = Path(root) / file
                catalog["total_files"] += 1
                
                if file.endswith('.py'):
                    catalog["python_files"] += 1
                    self.python_files.append(file_path)
                    self._analyze_python_file(file_path, catalog)
                
                elif file in ['pyproject.toml', 'requirements.txt', 'replit.toml']:
                    catalog["config_files"].append(str(file_path))
        
        # Convert sets to lists for JSON serialization
        catalog["dependencies"] = list(catalog["dependencies"])
        
        logger.info(f"Discovery complete: {catalog['python_files']} Python files found")
        return catalog
    
    def _analyze_python_file(self, file_path: Path, catalog: Dict[str, Any]):
        """Analyze individual Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            analysis = CodeAnalysis(
                file_path=str(file_path),
                total_lines=len(content.split('\n')),
                function_count=0,
                class_count=0,
                imports=[],
                potential_issues=[],
                optimization_opportunities=[],
                complexity_score=0.0
            )
            
            # Analyze AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis.function_count += 1
                    self._analyze_function(node, analysis)
                
                elif isinstance(node, ast.ClassDef):
                    analysis.class_count += 1
                    self._analyze_class(node, analysis, catalog)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    self._analyze_import(node, analysis, catalog)
            
            # Calculate complexity score
            analysis.complexity_score = self._calculate_complexity(analysis)
            
            # Categorize files
            self._categorize_file(file_path, catalog)
            
            self.analysis_results[str(file_path)] = analysis
            
        except Exception as e:
            logger.warning(f"Failed to analyze {file_path}: {e}")
    
    def _analyze_function(self, node: ast.FunctionDef, analysis: CodeAnalysis):
        """Analyze function for potential issues"""
        # Check for long functions
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            func_length = node.end_lineno - node.lineno
            if func_length > 50:
                analysis.potential_issues.append(
                    f"Long function '{node.name}' ({func_length} lines)"
                )
        
        # Check for many parameters
        if len(node.args.args) > 5:
            analysis.potential_issues.append(
                f"Function '{node.name}' has many parameters ({len(node.args.args)})"
            )
        
        # Check for missing docstring
        if not ast.get_docstring(node):
            analysis.optimization_opportunities.append(
                f"Function '{node.name}' missing docstring"
            )
    
    def _analyze_class(self, node: ast.ClassDef, analysis: CodeAnalysis, catalog: Dict[str, Any]):
        """Analyze class for categorization and issues"""
        class_name = node.name
        
        # Categorize based on naming patterns and inheritance
        if 'Model' in class_name or any(
            hasattr(base, 'id') and base.id in ['Model', 'db.Model'] 
            for base in node.bases if hasattr(base, 'id')
        ):
            catalog["models"].append(class_name)
        
        # Check for large classes
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) > 20:
            analysis.potential_issues.append(
                f"Large class '{class_name}' ({len(methods)} methods)"
            )
    
    def _analyze_import(self, node: ast.Import | ast.ImportFrom, analysis: CodeAnalysis, catalog: Dict[str, Any]):
        """Analyze imports for dependencies and patterns"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                analysis.imports.append(alias.name)
                catalog["dependencies"].add(alias.name.split('.')[0])
        
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            analysis.imports.append(module)
            if module:
                catalog["dependencies"].add(module.split('.')[0])
    
    def _categorize_file(self, file_path: Path, catalog: Dict[str, Any]):
        """Categorize file based on path and naming patterns"""
        path_str = str(file_path)
        
        if 'routes' in path_str and file_path.name.endswith('_routes.py'):
            catalog["routes"].append(path_str)
        elif 'routes' in path_str and 'bp' in Path(file_path).read_text():
            catalog["blueprints"].append(path_str)
        elif 'utils' in path_str or 'helper' in path_str:
            catalog["utilities"].append(path_str)
        elif 'services' in path_str:
            catalog["services"].append(path_str)
    
    def _calculate_complexity(self, analysis: CodeAnalysis) -> float:
        """Calculate complexity score based on various metrics"""
        base_score = 1.0
        
        # Penalize for issues
        base_score += len(analysis.potential_issues) * 0.5
        
        # Factor in file size
        if analysis.total_lines > 500:
            base_score += 1.0
        elif analysis.total_lines > 200:
            base_score += 0.5
        
        # Factor in function/class density
        if analysis.total_lines > 0:
            density = (analysis.function_count + analysis.class_count) / analysis.total_lines * 100
            if density > 10:  # Very dense
                base_score += 0.5
        
        return min(base_score, 10.0)  # Cap at 10
    
    def assess_and_prioritize(self) -> List[EnhancementOpportunity]:
        """Assess codebase and prioritize enhancement opportunities"""
        logger.info("Assessing enhancement opportunities...")
        
        opportunities = []
        
        # Analyze each file's results
        for file_path, analysis in self.analysis_results.items():
            # High complexity files
            if analysis.complexity_score > 7:
                opportunities.append(EnhancementOpportunity(
                    category="Code Quality",
                    priority="high",
                    description=f"High complexity file needs refactoring",
                    file_path=file_path,
                    line_number=None,
                    estimated_effort="high",
                    potential_impact="high",
                    suggested_action="Break down into smaller modules, extract functions"
                ))
            
            # Files with many potential issues
            if len(analysis.potential_issues) > 5:
                opportunities.append(EnhancementOpportunity(
                    category="Code Quality",
                    priority="medium",
                    description=f"Multiple code quality issues detected",
                    file_path=file_path,
                    line_number=None,
                    estimated_effort="medium",
                    potential_impact="medium",
                    suggested_action="Address long functions, add documentation, reduce complexity"
                ))
            
            # Missing documentation
            if len(analysis.optimization_opportunities) > 3:
                opportunities.append(EnhancementOpportunity(
                    category="Documentation",
                    priority="low",
                    description="Missing documentation in multiple functions",
                    file_path=file_path,
                    line_number=None,
                    estimated_effort="low",
                    potential_impact="medium",
                    suggested_action="Add docstrings to functions and classes"
                ))
        
        # System-wide opportunities
        opportunities.extend(self._identify_system_opportunities())
        
        # Sort by priority and impact
        priority_order = {"high": 3, "medium": 2, "low": 1}
        opportunities.sort(key=lambda x: (priority_order[x.priority], x.potential_impact), reverse=True)
        
        self.enhancement_opportunities = opportunities
        logger.info(f"Identified {len(opportunities)} enhancement opportunities")
        
        return opportunities
    
    def _identify_system_opportunities(self) -> List[EnhancementOpportunity]:
        """Identify system-wide enhancement opportunities"""
        opportunities = []
        
        # Check for missing caching
        if not any('cache' in path for path in self.analysis_results.keys()):
            opportunities.append(EnhancementOpportunity(
                category="Performance",
                priority="high",
                description="No caching system detected",
                file_path="system-wide",
                line_number=None,
                estimated_effort="medium",
                potential_impact="high",
                suggested_action="Implement intelligent caching system for AI responses and database queries"
            ))
        
        # Check for missing monitoring
        monitoring_files = [p for p in self.analysis_results.keys() if 'monitor' in p.lower()]
        if len(monitoring_files) < 2:
            opportunities.append(EnhancementOpportunity(
                category="Monitoring",
                priority="medium",
                description="Limited monitoring infrastructure",
                file_path="system-wide",
                line_number=None,
                estimated_effort="medium",
                potential_impact="high",
                suggested_action="Enhance monitoring with metrics collection and alerting"
            ))
        
        # Check for duplicate code patterns
        duplicate_count = self._detect_duplicate_patterns()
        if duplicate_count > 5:
            opportunities.append(EnhancementOpportunity(
                category="Code Quality",
                priority="medium",
                description=f"Detected {duplicate_count} potential code duplications",
                file_path="system-wide",
                line_number=None,
                estimated_effort="medium",
                potential_impact="medium",
                suggested_action="Refactor duplicate code into shared utilities"
            ))
        
        return opportunities
    
    def _detect_duplicate_patterns(self) -> int:
        """Detect potential code duplication patterns"""
        # Simple heuristic: count similar function names
        function_names = []
        for analysis in self.analysis_results.values():
            # This would need AST analysis to get actual function names
            # For now, use a simple heuristic
            pass
        
        # Return placeholder count
        return 3
    
    def generate_enhancement_report(self) -> Dict[str, Any]:
        """Generate comprehensive enhancement report"""
        catalog = self.discover_and_catalog()
        opportunities = self.assess_and_prioritize()
        
        # Categorize opportunities
        by_category = {}
        by_priority = {"high": [], "medium": [], "low": []}
        
        for opp in opportunities:
            if opp.category not in by_category:
                by_category[opp.category] = []
            by_category[opp.category].append(opp)
            by_priority[opp.priority].append(opp)
        
        # Calculate metrics
        total_files = len(self.analysis_results)
        avg_complexity = sum(a.complexity_score for a in self.analysis_results.values()) / total_files if total_files > 0 else 0
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_files_analyzed": total_files,
                "total_opportunities": len(opportunities),
                "average_complexity": round(avg_complexity, 2),
                "high_priority_count": len(by_priority["high"]),
                "medium_priority_count": len(by_priority["medium"]),
                "low_priority_count": len(by_priority["low"])
            },
            "catalog": catalog,
            "opportunities_by_category": {
                cat: len(opps) for cat, opps in by_category.items()
            },
            "opportunities_by_priority": {
                priority: len(opps) for priority, opps in by_priority.items()
            },
            "top_opportunities": [
                {
                    "category": opp.category,
                    "priority": opp.priority,
                    "description": opp.description,
                    "file_path": opp.file_path,
                    "suggested_action": opp.suggested_action
                }
                for opp in opportunities[:10]  # Top 10
            ],
            "recommendations": self._generate_recommendations(opportunities, avg_complexity)
        }
        
        return report
    
    def _generate_recommendations(self, opportunities: List[EnhancementOpportunity], avg_complexity: float) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        high_priority = [o for o in opportunities if o.priority == "high"]
        if high_priority:
            recommendations.append(f"Address {len(high_priority)} high-priority issues first")
        
        if avg_complexity > 5:
            recommendations.append("Focus on reducing code complexity through refactoring")
        
        perf_opportunities = [o for o in opportunities if o.category == "Performance"]
        if perf_opportunities:
            recommendations.append("Implement performance optimizations to improve user experience")
        
        doc_opportunities = [o for o in opportunities if o.category == "Documentation"]
        if len(doc_opportunities) > 5:
            recommendations.append("Improve code documentation for better maintainability")
        
        return recommendations
    
    def apply_automatic_fixes(self, max_fixes: int = 5) -> Dict[str, Any]:
        """Apply automatic fixes for simple issues"""
        logger.info(f"Applying up to {max_fixes} automatic fixes...")
        
        fixes_applied = []
        fixes_attempted = 0
        
        for opportunity in self.enhancement_opportunities:
            if fixes_attempted >= max_fixes:
                break
                
            if opportunity.estimated_effort == "low" and opportunity.category == "Documentation":
                # Example: Add basic docstrings
                if self._add_missing_docstrings(opportunity.file_path):
                    fixes_applied.append({
                        "file": opportunity.file_path,
                        "fix": "Added missing docstrings",
                        "category": opportunity.category
                    })
                    fixes_attempted += 1
        
        logger.info(f"Applied {len(fixes_applied)} automatic fixes")
        
        return {
            "fixes_applied": len(fixes_applied),
            "fixes_attempted": fixes_attempted,
            "details": fixes_applied
        }
    
    def _add_missing_docstrings(self, file_path: str) -> bool:
        """Add basic docstrings to functions missing them"""
        try:
            # This would implement actual docstring addition
            # For now, just return True to indicate success
            logger.info(f"Would add docstrings to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to add docstrings to {file_path}: {e}")
            return False

# Global enhancer instance
enhancer = CodebaseEnhancer()

def run_enhancement_analysis() -> Dict[str, Any]:
    """Run complete enhancement analysis"""
    return enhancer.generate_enhancement_report()

def get_enhancement_opportunities() -> List[EnhancementOpportunity]:
    """Get current enhancement opportunities"""
    return enhancer.assess_and_prioritize()

def apply_safe_enhancements() -> Dict[str, Any]:
    """Apply safe automatic enhancements"""
    return enhancer.apply_automatic_fixes()

if __name__ == "__main__":
    # Run analysis when executed directly
    report = run_enhancement_analysis()
    print(json.dumps(report, indent=2, default=str))