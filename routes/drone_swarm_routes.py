"""
SEED Drone Swarm API Routes
Provides API endpoints for monitoring and controlling the autonomous drone swarm
"""

import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
from typing import Dict, Any

# Import drone swarm components
try:
    from services.seed_drone_swarm import (
        get_drone_swarm, start_drone_swarm, stop_drone_swarm,
        DroneType, DroneTask
    )
except ImportError:
    get_drone_swarm = None
    start_drone_swarm = None
    stop_drone_swarm = None
    DroneType = None
    DroneTask = None

logger = logging.getLogger(__name__)

# Create blueprint
drone_swarm_bp = Blueprint('drone_swarm', __name__, url_prefix='/api/drone-swarm')

@drone_swarm_bp.route('/status', methods=['GET'])
def get_swarm_status():
    """Get comprehensive drone swarm status"""
    try:
        if not get_drone_swarm:
            return jsonify({
                'success': False,
                'error': 'Drone swarm not available',
                'swarm_status': 'unavailable'
            }), 503
        
        swarm = get_drone_swarm()
        status = swarm.get_swarm_status()
        
        return jsonify({
            'success': True,
            'swarm_status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Swarm status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'swarm_status': 'error'
        }), 500

@drone_swarm_bp.route('/start', methods=['POST'])
def start_swarm():
    """Start the drone swarm"""
    try:
        if not start_drone_swarm:
            return jsonify({
                'success': False,
                'error': 'Drone swarm not available'
            }), 503
        
        swarm = start_drone_swarm()
        
        return jsonify({
            'success': True,
            'message': 'Drone swarm started successfully',
            'swarm_id': id(swarm),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Swarm start error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@drone_swarm_bp.route('/stop', methods=['POST'])
def stop_swarm():
    """Stop the drone swarm"""
    try:
        if not stop_drone_swarm:
            return jsonify({
                'success': False,
                'error': 'Drone swarm not available'
            }), 503
        
        stop_drone_swarm()
        
        return jsonify({
            'success': True,
            'message': 'Drone swarm stopped successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Swarm stop error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@drone_swarm_bp.route('/tasks', methods=['GET'])
def get_recent_results():
    """Get recent task results from drones"""
    try:
        if not get_drone_swarm:
            return jsonify({
                'success': False,
                'error': 'Drone swarm not available',
                'results': []
            }), 503
        
        limit = request.args.get('limit', 20, type=int)
        swarm = get_drone_swarm()
        results = swarm.get_recent_results(limit=limit)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Recent results error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'results': []
        }), 500

@drone_swarm_bp.route('/tasks/add', methods=['POST'])
def add_task():
    """Add a task to the drone swarm queue"""
    try:
        if not get_drone_swarm or not DroneType:
            return jsonify({
                'success': False,
                'error': 'Drone swarm not available'
            }), 503
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No task data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['drone_type', 'priority', 'payload']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate drone type
        try:
            drone_type = DroneType(data['drone_type'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid drone type: {data["drone_type"]}'
            }), 400
        
        # Validate priority
        priority = data['priority']
        if not isinstance(priority, int) or priority < 1 or priority > 10:
            return jsonify({
                'success': False,
                'error': 'Priority must be an integer between 1 and 10'
            }), 400
        
        swarm = get_drone_swarm()
        task_id = swarm.add_task(
            drone_type=drone_type,
            priority=priority,
            payload=data['payload'],
            task_id=data.get('task_id'),
            deadline=data.get('deadline')
        )
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Task added to swarm queue',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Add task error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@drone_swarm_bp.route('/verification/trigger', methods=['POST'])
def trigger_verification():
    """Trigger a system verification task"""
    try:
        if not get_drone_swarm or not DroneType:
            return jsonify({
                'success': False,
                'error': 'Drone swarm not available'
            }), 503
        
        data = request.get_json() or {}
        verification_type = data.get('verification_type', 'full_system')
        
        swarm = get_drone_swarm()
        task_id = swarm.add_task(
            drone_type=DroneType.VERIFICATION_DRONE,
            priority=7,
            payload={'verification_type': verification_type},
            task_id=f"manual_verification_{int(datetime.now().timestamp())}"
        )
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'verification_type': verification_type,
            'message': 'Verification task queued',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Trigger verification error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@drone_swarm_bp.route('/optimization/trigger', methods=['POST'])
def trigger_optimization():
    """Trigger a system optimization task"""
    try:
        if not get_drone_swarm or not DroneType:
            return jsonify({
                'success': False,
                'error': 'Drone swarm not available'
            }), 503
        
        data = request.get_json() or {}
        optimization_type = data.get('optimization_type', 'general')
        user_id = data.get('user_id')
        
        payload = {'optimization_type': optimization_type}
        if user_id:
            payload['user_id'] = user_id
        
        swarm = get_drone_swarm()
        task_id = swarm.add_task(
            drone_type=DroneType.OPTIMIZATION_DRONE,
            priority=5,
            payload=payload,
            task_id=f"manual_optimization_{int(datetime.now().timestamp())}"
        )
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'optimization_type': optimization_type,
            'message': 'Optimization task queued',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Trigger optimization error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@drone_swarm_bp.route('/data-collection/trigger', methods=['POST'])
def trigger_data_collection():
    """Trigger a data collection task"""
    try:
        if not get_drone_swarm or not DroneType:
            return jsonify({
                'success': False,
                'error': 'Drone swarm not available'
            }), 503
        
        data = request.get_json() or {}
        collection_type = data.get('collection_type', 'system_metrics')
        
        # Validate collection type
        valid_types = ['system_metrics', 'user_analytics', 'therapeutic_data', 'ai_usage_patterns']
        if collection_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid collection type. Valid types: {valid_types}'
            }), 400
        
        swarm = get_drone_swarm()
        task_id = swarm.add_task(
            drone_type=DroneType.DATA_COLLECTION_DRONE,
            priority=4,
            payload={'collection_type': collection_type},
            task_id=f"manual_data_collection_{int(datetime.now().timestamp())}"
        )
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'collection_type': collection_type,
            'message': 'Data collection task queued',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Trigger data collection error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@drone_swarm_bp.route('/healing/trigger', methods=['POST'])
def trigger_healing():
    """Trigger a self-healing task"""
    try:
        if not get_drone_swarm or not DroneType:
            return jsonify({
                'success': False,
                'error': 'Drone swarm not available'
            }), 503
        
        data = request.get_json() or {}
        healing_type = data.get('healing_type', 'general')
        issues = data.get('issues', [])
        
        # Validate healing type
        valid_types = ['database_repair', 'log_cleanup', 'cache_cleanup', 'general']
        if healing_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid healing type. Valid types: {valid_types}'
            }), 400
        
        swarm = get_drone_swarm()
        task_id = swarm.add_task(
            drone_type=DroneType.SELF_HEALING_DRONE,
            priority=8,
            payload={
                'healing_type': healing_type,
                'issues': issues
            },
            task_id=f"manual_healing_{int(datetime.now().timestamp())}"
        )
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'healing_type': healing_type,
            'message': 'Self-healing task queued',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Trigger healing error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@drone_swarm_bp.route('/drones', methods=['GET'])
def get_drone_performance():
    """Get individual drone performance metrics"""
    try:
        if not get_drone_swarm:
            return jsonify({
                'success': False,
                'error': 'Drone swarm not available',
                'drones': []
            }), 503
        
        swarm = get_drone_swarm()
        status = swarm.get_swarm_status()
        
        return jsonify({
            'success': True,
            'drones': status.get('drone_performance', []),
            'total_drones': status.get('total_active_drones', 0),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Drone performance error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'drones': []
        }), 500

@drone_swarm_bp.route('/health', methods=['GET'])
def swarm_health():
    """Health check for the drone swarm system"""
    try:
        health_status = {
            'drone_swarm_available': get_drone_swarm is not None,
            'timestamp': datetime.now().isoformat()
        }
        
        if get_drone_swarm:
            try:
                swarm = get_drone_swarm()
                swarm_status = swarm.get_swarm_status()
                health_status.update({
                    'swarm_running': swarm_status.get('swarm_running', False),
                    'active_drones': swarm_status.get('total_active_drones', 0),
                    'pending_tasks': swarm_status.get('pending_tasks', 0)
                })
            except Exception as e:
                health_status['swarm_error'] = str(e)
        
        status_code = 200 if health_status.get('drone_swarm_available', False) else 503
        
        return jsonify({
            'success': True,
            'health': health_status
        }), status_code
        
    except Exception as e:
        logger.error(f"Swarm health check error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'health': {'drone_swarm_available': False}
        }), 500

# Error handlers
@drone_swarm_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/api/drone-swarm/status',
            '/api/drone-swarm/start',
            '/api/drone-swarm/stop',
            '/api/drone-swarm/tasks',
            '/api/drone-swarm/tasks/add',
            '/api/drone-swarm/verification/trigger',
            '/api/drone-swarm/optimization/trigger',
            '/api/drone-swarm/data-collection/trigger',
            '/api/drone-swarm/healing/trigger',
            '/api/drone-swarm/drones',
            '/api/drone-swarm/health'
        ]
    }), 404

@drone_swarm_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred in the drone swarm system'
    }), 500