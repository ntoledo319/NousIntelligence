"""
Optimization Routes - API endpoints for the Consolidated Optimization Manager
Provides REST API access to all optimization features and system monitoring
"""

import logging
from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import optimization manager with fallback
try:
    from utils.consolidated_optimization_manager import (
        get_optimization_manager,
        run_system_optimization,
        get_optimization_recommendations
    )
except ImportError:
    def get_optimization_manager():
        return None
    def run_system_optimization(user_id=None, level="standard"):
        return {"error": "Optimization manager not available"}
    def get_optimization_recommendations():
        return []

logger = logging.getLogger(__name__)

# Create blueprint
optimization_bp = Blueprint('optimization', __name__, url_prefix='/api/optimization')

@optimization_bp.route('/status', methods=['GET'])
def optimization_status():
    """Get current optimization system status"""
    try:
        manager = get_optimization_manager()
        if not manager:
            return jsonify({
                'status': 'unavailable',
                'message': 'Optimization manager not initialized'
            }), 503
        
        status = manager.get_optimization_status()
        
        return jsonify({
            'status': 'success',
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Optimization status error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@optimization_bp.route('/run', methods=['POST'])
@login_required
def run_optimization():
    """Run comprehensive optimization"""
    try:
        data = request.get_json() or {}
        
        # Get optimization parameters
        optimization_level = data.get('level', 'standard')
        user_id = getattr(current_user, 'id', None) if current_user.is_authenticated else None
        
        # Validate optimization level
        valid_levels = ['light', 'standard', 'aggressive']
        if optimization_level not in valid_levels:
            return jsonify({
                'status': 'error',
                'message': f'Invalid optimization level. Must be one of: {valid_levels}'
            }), 400
        
        # Run optimization
        results = run_system_optimization(user_id=str(user_id) if user_id else None, level=optimization_level)
        
        return jsonify({
            'status': 'success',
            'data': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Optimization run error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@optimization_bp.route('/recommendations', methods=['GET'])
def optimization_recommendations():
    """Get optimization recommendations"""
    try:
        recommendations = get_optimization_recommendations()
        
        return jsonify({
            'status': 'success',
            'data': {
                'recommendations': recommendations,
                'count': len(recommendations)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Optimization recommendations error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@optimization_bp.route('/auto-optimization', methods=['POST'])
@login_required
def toggle_auto_optimization():
    """Enable or disable automatic optimization"""
    try:
        data = request.get_json() or {}
        enabled = data.get('enabled', True)
        
        manager = get_optimization_manager()
        if not manager:
            return jsonify({
                'status': 'error',
                'message': 'Optimization manager not available'
            }), 503
        
        manager.enable_auto_optimization(enabled)
        
        return jsonify({
            'status': 'success',
            'data': {
                'auto_optimization_enabled': enabled,
                'message': f"Auto optimization {'enabled' if enabled else 'disabled'}"
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Auto optimization toggle error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@optimization_bp.route('/modules', methods=['GET'])
def optimization_modules():
    """Get available optimization modules"""
    try:
        manager = get_optimization_manager()
        if not manager:
            return jsonify({
                'status': 'unavailable',
                'data': {
                    'modules': [],
                    'count': 0
                }
            })
        
        status = manager.get_optimization_status()
        modules = status.get('modules_available', [])
        
        # Add module descriptions
        module_descriptions = {
            'ai_cost': 'AI Cost Optimization - Reduces AI service costs by 15-35%',
            'caching': 'Enhanced Caching System - Improves response times and reduces API calls',
            'seed': 'SEED Optimization Engine - Personalizes user experience and therapeutic interventions',
            'database': 'Database Query Optimizer - Optimizes database performance and query efficiency',
            'imports': 'Import Performance Optimizer - Reduces startup time and memory usage'
        }
        
        module_details = []
        for module in modules:
            module_details.append({
                'name': module,
                'description': module_descriptions.get(module, f'{module.title()} optimization module'),
                'status': 'active'
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'modules': module_details,
                'count': len(module_details)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Optimization modules error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@optimization_bp.route('/history', methods=['GET'])
@login_required
def optimization_history():
    """Get optimization history"""
    try:
        manager = get_optimization_manager()
        if not manager:
            return jsonify({
                'status': 'error',
                'message': 'Optimization manager not available'
            }), 503
        
        # Get query parameters
        limit = min(int(request.args.get('limit', 10)), 50)  # Max 50 records
        
        # Get optimization history
        history = manager.optimization_history[-limit:] if manager.optimization_history else []
        
        return jsonify({
            'status': 'success',
            'data': {
                'history': history,
                'count': len(history),
                'total_optimizations': len(manager.optimization_history)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Optimization history error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@optimization_bp.route('/system-health', methods=['GET'])
def system_health():
    """Get current system health metrics"""
    try:
        manager = get_optimization_manager()
        if not manager:
            return jsonify({
                'status': 'unavailable',
                'message': 'Optimization manager not available'
            }), 503
        
        health_metrics = manager._get_system_health()
        
        # Add health status based on metrics
        cpu_status = 'good' if health_metrics.get('cpu_percent', 0) < 70 else 'warning' if health_metrics.get('cpu_percent', 0) < 90 else 'critical'
        memory_status = 'good' if health_metrics.get('memory_percent', 0) < 80 else 'warning' if health_metrics.get('memory_percent', 0) < 95 else 'critical'
        
        health_data = {
            'metrics': health_metrics,
            'status': {
                'cpu': cpu_status,
                'memory': memory_status,
                'overall': 'good' if cpu_status == 'good' and memory_status == 'good' else 'warning'
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': health_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"System health error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@optimization_bp.route('/performance-metrics', methods=['GET'])
def performance_metrics():
    """Get detailed performance metrics"""
    try:
        manager = get_optimization_manager()
        if not manager:
            return jsonify({
                'status': 'unavailable',
                'message': 'Optimization manager not available'
            }), 503
        
        # Collect metrics from various optimization modules
        metrics = {
            'system_health': manager._get_system_health(),
            'optimization_status': manager.get_optimization_status(),
            'recommendations_count': len(manager.get_optimization_recommendations())
        }
        
        # Add module-specific metrics if available
        if 'ai_cost' in manager.optimization_modules:
            try:
                ai_optimizer = manager.optimization_modules['ai_cost']
                if hasattr(ai_optimizer, 'get_optimization_report'):
                    metrics['ai_cost_metrics'] = ai_optimizer.get_optimization_report()
            except Exception:
                pass
        
        if 'caching' in manager.optimization_modules:
            try:
                caching_system = manager.optimization_modules['caching']
                if hasattr(caching_system, 'get_cache_statistics'):
                    metrics['caching_metrics'] = caching_system.get_cache_statistics()
            except Exception:
                pass
        
        return jsonify({
            'status': 'success',
            'data': metrics,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Performance metrics error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@optimization_bp.route('/dashboard', methods=['GET'])
def optimization_dashboard():
    """Serve the optimization dashboard"""
    try:
        from flask import render_template
        return render_template('optimization_dashboard.html')
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return f"<h1>Optimization Dashboard</h1><p>Dashboard not available: {e}</p>"

@optimization_bp.route('/quick-optimize', methods=['POST'])
def quick_optimize():
    """Run quick optimization (light level, no authentication required)"""
    try:
        # Run light optimization without user context
        results = run_system_optimization(user_id=None, level="light")
        
        # Return simplified results
        quick_results = {
            'optimization_completed': True,
            'modules_optimized': results.get('modules_optimized', []),
            'optimization_score': results.get('optimization_score', {}),
            'execution_time': results.get('execution_time', 0)
        }
        
        return jsonify({
            'status': 'success',
            'data': quick_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Quick optimization error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Error handlers
@optimization_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Optimization endpoint not found'
    }), 404

@optimization_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'status': 'error',
        'message': 'Method not allowed for this optimization endpoint'
    }), 405

# Register blueprint function
def register_optimization_routes(app):
    """Register optimization routes with the Flask app"""
    app.register_blueprint(optimization_bp)
    logger.info("Optimization routes registered successfully")