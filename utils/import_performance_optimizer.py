"""
Import Performance Optimizer
Optimizes import statements and module loading for better performance
"""

import sys
import time
import importlib
import logging
from typing import Dict, Any, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class ImportPerformanceOptimizer:
    """Optimizer for import performance"""
    
    def __init__(self):
        self.import_times = {}
        self.heavy_modules = {
            'tensorflow', 'torch', 'cv2', 'pandas', 'numpy', 
            'scipy', 'matplotlib', 'sklearn', 'transformers'
        }
    
    @contextmanager
    def track_import_time(self, module_name: str):
        """Context manager to track import times"""
        start_time = time.time()
        try:
            yield
        finally:
            import_time = time.time() - start_time
            self.import_times[module_name] = import_time
            
            if import_time > 0.1:  # Log slow imports
                logger.info(f"Import {module_name} took {import_time:.3f}s")
    
    def conditional_import(self, module_name: str, condition: bool = True):
        """Conditionally import modules"""
        if not condition:
            return None
        
        try:
            with self.track_import_time(module_name):
                return importlib.import_module(module_name)
        except ImportError as e:
            logger.warning(f"Conditional import failed for {module_name}: {e}")
            return None
    
    def defer_heavy_imports(self, module_names: List[str]):
        """Defer importing of heavy modules"""
        deferred = {}
        for module_name in module_names:
            if module_name in self.heavy_modules:
                # Create a lazy loader
                deferred[module_name] = lambda name=module_name: importlib.import_module(name)
            else:
                # Import immediately for light modules
                try:
                    deferred[module_name] = importlib.import_module(module_name)
                except ImportError:
                    deferred[module_name] = None
        
        return deferred
    
    def optimize_import_order(self, modules: List[str]) -> List[str]:
        """Optimize import order for better performance"""
        # Sort modules by known import times (light first)
        light_modules = [m for m in modules if m not in self.heavy_modules]
        heavy_modules = [m for m in modules if m in self.heavy_modules]
        
        return light_modules + heavy_modules
    
    def get_import_statistics(self) -> Dict[str, Any]:
        """Get import performance statistics"""
        total_time = sum(self.import_times.values())
        slow_imports = {k: v for k, v in self.import_times.items() if v > 0.1}
        
        return {
            'total_modules_imported': len(self.import_times),
            'total_import_time': total_time,
            'average_import_time': total_time / len(self.import_times) if self.import_times else 0,
            'slow_imports': slow_imports,
            'heavy_modules_detected': len([m for m in self.import_times if m in self.heavy_modules])
        }
    
    def suggest_optimizations(self) -> List[str]:
        """Suggest import optimizations"""
        suggestions = []
        
        slow_imports = {k: v for k, v in self.import_times.items() if v > 0.1}
        if slow_imports:
            suggestions.append(f"Consider lazy loading for slow imports: {list(slow_imports.keys())}")
        
        heavy_imports = [m for m in self.import_times if m in self.heavy_modules]
        if heavy_imports:
            suggestions.append(f"Consider deferring heavy imports: {heavy_imports}")
        
        return suggestions

# Global import optimizer
import_optimizer = ImportPerformanceOptimizer()

# Convenience functions
def track_import(module_name: str):
    """Track import performance"""
    return import_optimizer.track_import_time(module_name)

def defer_import(module_name: str, condition: bool = True):
    """Defer module import"""
    return import_optimizer.conditional_import(module_name, condition)
