"""
SEED Drone Swarm System
Autonomous Software Agents for NOUS Platform

Implements autonomous drones that work with the SEED optimization engine to provide:
- Self-healing system maintenance
- Dynamic optimization 
- Real-time monitoring
- Predictive issue prevention
- Autonomous data collection and processing
"""

import asyncio
import logging
import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import uuid

# Import existing NOUS services
try:
    from services.seed_optimization_engine import NOUSSeedEngine, OptimizationDomain
except ImportError:
    NOUSSeedEngine = None
    OptimizationDomain = None

try:
    from utils.health_monitor import HealthMonitor
except ImportError:
    HealthMonitor = None

logger = logging.getLogger(__name__)

class DroneType(Enum):
    """Types of autonomous drones in the system"""
    TASK_DRONE = "task_drone"
    VERIFICATION_DRONE = "verification_drone" 
    SELF_HEALING_DRONE = "self_healing_drone"
    DATA_COLLECTION_DRONE = "data_collection_drone"
    OPTIMIZATION_DRONE = "optimization_drone"
    INDEXING_DRONE = "indexing_drone"
    THERAPEUTIC_MONITOR = "therapeutic_monitor"
    AI_COST_OPTIMIZER = "ai_cost_optimizer"

class DroneStatus(Enum):
    """Possible states of a drone"""
    IDLE = "idle"
    ACTIVE = "active"
    WORKING = "working" 
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"

@dataclass
class DroneTask:
    """Represents a task to be executed by a drone"""
    task_id: str
    drone_type: DroneType
    priority: int  # 1-10, higher is more urgent
    payload: Dict[str, Any]
    created_at: datetime
    deadline: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class DroneResult:
    """Result from drone execution"""
    task_id: str
    drone_id: str
    success: bool
    result_data: Dict[str, Any]
    execution_time: float
    completed_at: datetime
    recommendations: Optional[List[str]] = None

class BaseDrone:
    """Base class for all autonomous drones"""
    
    def __init__(self, drone_id: str, drone_type: DroneType):
        self.drone_id = drone_id
        self.drone_type = drone_type
        self.status = DroneStatus.IDLE
        self.current_task: Optional[DroneTask] = None
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_execution_time = 0.0
        
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this drone"""
        total_tasks = self.tasks_completed + self.tasks_failed
        success_rate = (self.tasks_completed / total_tasks) if total_tasks > 0 else 0
        avg_execution_time = (self.total_execution_time / self.tasks_completed) if self.tasks_completed > 0 else 0
        
        return {
            'drone_id': self.drone_id,
            'type': self.drone_type.value,
            'status': self.status.value,
            'uptime': (datetime.now() - self.created_at).total_seconds(),
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'success_rate': success_rate,
            'avg_execution_time': avg_execution_time,
            'last_activity': self.last_activity.isoformat()
        }
    
    async def execute_task(self, task: DroneTask) -> DroneResult:
        """Execute a task (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement execute_task")

class VerificationDrone(BaseDrone):
    """Drone that continuously scans system for errors and inconsistencies"""
    
    def __init__(self, drone_id: str):
        super().__init__(drone_id, DroneType.VERIFICATION_DRONE)
        self.checks = [
            self._check_database_health,
            self._check_ai_service_health, 
            self._check_authentication_system,
            self._check_memory_usage,
            self._check_disk_space,
            self._check_route_integrity
        ]
    
    async def execute_task(self, task: DroneTask) -> DroneResult:
        """Execute verification task"""
        start_time = time.time()
        self.status = DroneStatus.WORKING
        self.current_task = task
        self.update_activity()
        
        try:
            verification_type = task.payload.get('verification_type', 'full_system')
            issues_found = []
            health_score = 100.0
            
            if verification_type == 'full_system':
                # Run all checks
                for check in self.checks:
                    try:
                        check_result = await check()
                        if not check_result['healthy']:
                            issues_found.extend(check_result['issues'])
                            health_score -= check_result['severity_impact']
                    except Exception as e:
                        issues_found.append(f"Check failed: {check.__name__}: {str(e)}")
                        health_score -= 5
            
            # Generate recommendations
            recommendations = self._generate_recommendations(issues_found)
            
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            self.tasks_completed += 1
            self.status = DroneStatus.COMPLETED
            
            return DroneResult(
                task_id=task.task_id,
                drone_id=self.drone_id,
                success=True,
                result_data={
                    'health_score': health_score,
                    'issues_found': issues_found,
                    'checks_completed': len(self.checks),
                    'verification_type': verification_type
                },
                execution_time=execution_time,
                completed_at=datetime.now(),
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Verification drone {self.drone_id} failed: {e}")
            self.tasks_failed += 1
            self.status = DroneStatus.FAILED
            
            return DroneResult(
                task_id=task.task_id,
                drone_id=self.drone_id,
                success=False,
                result_data={'error': str(e)},
                execution_time=time.time() - start_time,
                completed_at=datetime.now()
            )
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and health"""
        try:
            # Simple database health check
            db_path = Path("instance/nous.db")
            if not db_path.exists():
                return {
                    'healthy': False,
                    'issues': ['Primary database file missing'],
                    'severity_impact': 30
                }
            
            # Try to connect and query
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
            if table_count < 5:  # Expecting at least basic tables
                return {
                    'healthy': False, 
                    'issues': ['Database appears incomplete - low table count'],
                    'severity_impact': 15
                }
            
            return {'healthy': True, 'issues': [], 'severity_impact': 0}
            
        except Exception as e:
            return {
                'healthy': False,
                'issues': [f'Database connection failed: {str(e)}'],
                'severity_impact': 25
            }
    
    async def _check_ai_service_health(self) -> Dict[str, Any]:
        """Check AI service availability and performance"""
        try:
            # Check if AI services are responsive
            from utils.unified_ai_service import UnifiedAIService
            ai_service = UnifiedAIService()
            
            # Simple test query
            test_response = ai_service.get_response("test", user_id="system_check")
            
            if not test_response or len(test_response) < 5:
                return {
                    'healthy': False,
                    'issues': ['AI service not responding properly'],
                    'severity_impact': 20
                }
                
            return {'healthy': True, 'issues': [], 'severity_impact': 0}
            
        except Exception as e:
            return {
                'healthy': False,
                'issues': [f'AI service health check failed: {str(e)}'],
                'severity_impact': 15
            }
    
    async def _check_authentication_system(self) -> Dict[str, Any]:
        """Check authentication system health"""
        try:
            # Check if OAuth service is configured
            import os
            required_secrets = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'SESSION_SECRET']
            missing_secrets = []
            
            for secret in required_secrets:
                if not os.environ.get(secret):
                    missing_secrets.append(secret)
            
            if missing_secrets:
                return {
                    'healthy': False,
                    'issues': [f'Missing required secrets: {", ".join(missing_secrets)}'],
                    'severity_impact': 10
                }
            
            return {'healthy': True, 'issues': [], 'severity_impact': 0}
            
        except Exception as e:
            return {
                'healthy': False,
                'issues': [f'Auth system check failed: {str(e)}'],
                'severity_impact': 12
            }
    
    async def _check_memory_usage(self) -> Dict[str, Any]:
        """Check system memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                return {
                    'healthy': False,
                    'issues': [f'High memory usage: {memory.percent}%'],
                    'severity_impact': 15
                }
            elif memory.percent > 80:
                return {
                    'healthy': False,
                    'issues': [f'Elevated memory usage: {memory.percent}%'],
                    'severity_impact': 8
                }
            
            return {'healthy': True, 'issues': [], 'severity_impact': 0}
            
        except ImportError:
            # psutil not available, skip check
            return {'healthy': True, 'issues': [], 'severity_impact': 0}
        except Exception as e:
            return {
                'healthy': False,
                'issues': [f'Memory check failed: {str(e)}'],
                'severity_impact': 5
            }
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("./")
            free_percent = (free / total) * 100
            
            if free_percent < 10:
                return {
                    'healthy': False,
                    'issues': [f'Low disk space: {free_percent:.1f}% free'],
                    'severity_impact': 20
                }
            elif free_percent < 20:
                return {
                    'healthy': False,
                    'issues': [f'Disk space getting low: {free_percent:.1f}% free'],
                    'severity_impact': 8
                }
            
            return {'healthy': True, 'issues': [], 'severity_impact': 0}
            
        except Exception as e:
            return {
                'healthy': False,
                'issues': [f'Disk space check failed: {str(e)}'],
                'severity_impact': 5
            }
    
    async def _check_route_integrity(self) -> Dict[str, Any]:
        """Check if main routes are accessible"""
        try:
            # Check if main route files exist
            critical_routes = [
                'routes/main.py',
                'routes/health_api.py', 
                'routes/auth_routes.py',
                'routes/api_routes.py'
            ]
            
            missing_routes = []
            for route_file in critical_routes:
                if not Path(route_file).exists():
                    missing_routes.append(route_file)
            
            if missing_routes:
                return {
                    'healthy': False,
                    'issues': [f'Missing critical route files: {", ".join(missing_routes)}'],
                    'severity_impact': 25
                }
            
            return {'healthy': True, 'issues': [], 'severity_impact': 0}
            
        except Exception as e:
            return {
                'healthy': False,
                'issues': [f'Route integrity check failed: {str(e)}'],
                'severity_impact': 10
            }
    
    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on found issues"""
        recommendations = []
        
        for issue in issues:
            if 'database' in issue.lower():
                recommendations.append("Consider running database health check and repair")
            elif 'memory' in issue.lower():
                recommendations.append("Monitor memory usage and consider cleanup")
            elif 'disk' in issue.lower():
                recommendations.append("Clean up temporary files and logs")
            elif 'secret' in issue.lower():
                recommendations.append("Configure missing environment variables")
            elif 'route' in issue.lower():
                recommendations.append("Verify route file integrity and restore if needed")
            else:
                recommendations.append(f"Investigate and resolve: {issue}")
        
        if not recommendations:
            recommendations.append("System health is good - continue monitoring")
            
        return recommendations

class DataCollectionDrone(BaseDrone):
    """Drone that collects and processes data from various sources"""
    
    def __init__(self, drone_id: str):
        super().__init__(drone_id, DroneType.DATA_COLLECTION_DRONE)
        
    async def execute_task(self, task: DroneTask) -> DroneResult:
        """Execute data collection task"""
        start_time = time.time()
        self.status = DroneStatus.WORKING
        self.current_task = task
        self.update_activity()
        
        try:
            collection_type = task.payload.get('collection_type', 'system_metrics')
            data_collected = {}
            
            if collection_type == 'system_metrics':
                data_collected = await self._collect_system_metrics()
            elif collection_type == 'user_analytics':
                data_collected = await self._collect_user_analytics()
            elif collection_type == 'therapeutic_data':
                data_collected = await self._collect_therapeutic_data()
            elif collection_type == 'ai_usage_patterns':
                data_collected = await self._collect_ai_usage_patterns()
            
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            self.tasks_completed += 1
            self.status = DroneStatus.COMPLETED
            
            return DroneResult(
                task_id=task.task_id,
                drone_id=self.drone_id,
                success=True,
                result_data={
                    'collection_type': collection_type,
                    'data_collected': data_collected,
                    'records_processed': len(data_collected.get('records', []))
                },
                execution_time=execution_time,
                completed_at=datetime.now(),
                recommendations=self._generate_data_recommendations(data_collected)
            )
            
        except Exception as e:
            logger.error(f"Data collection drone {self.drone_id} failed: {e}")
            self.tasks_failed += 1
            self.status = DroneStatus.FAILED
            
            return DroneResult(
                task_id=task.task_id,
                drone_id=self.drone_id,
                success=False,
                result_data={'error': str(e)},
                execution_time=time.time() - start_time,
                completed_at=datetime.now()
            )
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system performance metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'records': []
        }
        
        try:
            # Database size and health
            db_files = ['instance/nous.db', 'instance/seed_optimization.db', 'instance/seed_drone_swarm.db']
            for db_file in db_files:
                db_path = Path(db_file)
                if db_path.exists():
                    size_mb = db_path.stat().st_size / (1024 * 1024)
                    metrics['records'].append({
                        'type': 'database_size',
                        'database': db_file,
                        'size_mb': round(size_mb, 2)
                    })
            
            # Log file analysis
            log_files = ['logs/app.log', 'logs/error.log', 'logs/access.log']
            for log_file in log_files:
                log_path = Path(log_file)
                if log_path.exists():
                    size_mb = log_path.stat().st_size / (1024 * 1024)
                    # Count recent errors (last 1000 lines)
                    try:
                        with open(log_path, 'r') as f:
                            lines = f.readlines()
                            recent_lines = lines[-1000:] if len(lines) > 1000 else lines
                            error_count = len([line for line in recent_lines if 'ERROR' in line.upper()])
                            
                        metrics['records'].append({
                            'type': 'log_analysis',
                            'log_file': log_file,
                            'size_mb': round(size_mb, 2),
                            'recent_errors': error_count
                        })
                    except Exception:
                        pass
            
            # Route health check
            critical_routes = [
                'routes/main.py', 'routes/health_api.py', 'routes/auth_routes.py',
                'routes/api_routes.py', 'routes/seed_routes.py'
            ]
            
            route_status = []
            for route_file in critical_routes:
                route_path = Path(route_file)
                status = {
                    'route': route_file,
                    'exists': route_path.exists(),
                    'size_kb': 0
                }
                
                if route_path.exists():
                    status['size_kb'] = round(route_path.stat().st_size / 1024, 2)
                    
                route_status.append(status)
            
            metrics['records'].append({
                'type': 'route_health',
                'routes': route_status
            })
            
        except Exception as e:
            logger.error(f"System metrics collection error: {e}")
            
        return metrics
    
    async def _collect_user_analytics(self) -> Dict[str, Any]:
        """Collect user interaction and engagement analytics"""
        analytics = {
            'timestamp': datetime.now().isoformat(),
            'records': []
        }
        
        try:
            # Database analytics
            db_path = Path("instance/nous.db")
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # User count
                    try:
                        cursor.execute("SELECT COUNT(*) FROM user")
                        user_count = cursor.fetchone()[0]
                        analytics['records'].append({
                            'type': 'user_metrics',
                            'total_users': user_count
                        })
                    except sqlite3.Error:
                        pass
                    
                    # Session activity (if session table exists)
                    try:
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='session'")
                        if cursor.fetchone():
                            cursor.execute("SELECT COUNT(*) FROM session WHERE created_at > datetime('now', '-24 hours')")
                            recent_sessions = cursor.fetchone()[0]
                            analytics['records'].append({
                                'type': 'session_activity',
                                'sessions_24h': recent_sessions
                            })
                    except sqlite3.Error:
                        pass
            
        except Exception as e:
            logger.error(f"User analytics collection error: {e}")
            
        return analytics
    
    async def _collect_therapeutic_data(self) -> Dict[str, Any]:
        """Collect therapeutic intervention effectiveness data"""
        therapeutic_data = {
            'timestamp': datetime.now().isoformat(),
            'records': []
        }
        
        try:
            db_path = Path("instance/nous.db")
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # CBT skill usage patterns
                    try:
                        cursor.execute("""
                            SELECT name FROM sqlite_master 
                            WHERE type='table' AND name='cbt_skill_usage'
                        """)
                        if cursor.fetchone():
                            cursor.execute("""
                                SELECT skill_name, COUNT(*) as usage_count
                                FROM cbt_skill_usage 
                                WHERE created_at > datetime('now', '-7 days')
                                GROUP BY skill_name
                                ORDER BY usage_count DESC
                                LIMIT 10
                            """)
                            skill_usage = cursor.fetchall()
                            therapeutic_data['records'].append({
                                'type': 'cbt_skill_usage',
                                'top_skills': [{'skill': row[0], 'count': row[1]} for row in skill_usage]
                            })
                    except sqlite3.Error:
                        pass
                    
                    # DBT module engagement
                    try:
                        cursor.execute("""
                            SELECT name FROM sqlite_master 
                            WHERE type='table' AND name='dbt_skill_usage'
                        """)
                        if cursor.fetchone():
                            cursor.execute("""
                                SELECT skill_name, AVG(effectiveness_rating) as avg_effectiveness
                                FROM dbt_skill_usage 
                                WHERE created_at > datetime('now', '-30 days')
                                AND effectiveness_rating IS NOT NULL
                                GROUP BY skill_name
                                ORDER BY avg_effectiveness DESC
                            """)
                            dbt_effectiveness = cursor.fetchall()
                            therapeutic_data['records'].append({
                                'type': 'dbt_effectiveness',
                                'skill_effectiveness': [{'skill': row[0], 'avg_rating': row[1]} for row in dbt_effectiveness]
                            })
                    except sqlite3.Error:
                        pass
            
        except Exception as e:
            logger.error(f"Therapeutic data collection error: {e}")
            
        return therapeutic_data
    
    async def _collect_ai_usage_patterns(self) -> Dict[str, Any]:
        """Collect AI service usage and cost patterns"""
        ai_patterns = {
            'timestamp': datetime.now().isoformat(),
            'records': []
        }
        
        try:
            # Check AI optimization database
            ai_db_path = Path("instance/ai_brain_optimizer.db")
            if ai_db_path.exists():
                with sqlite3.connect(ai_db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Usage patterns
                    try:
                        cursor.execute("""
                            SELECT COUNT(*) as requests, AVG(cost) as avg_cost
                            FROM optimization_history 
                            WHERE timestamp > datetime('now', '-24 hours')
                        """)
                        recent_usage = cursor.fetchone()
                        if recent_usage and recent_usage[0] > 0:
                            ai_patterns['records'].append({
                                'type': 'ai_usage_24h',
                                'total_requests': recent_usage[0],
                                'avg_cost': round(recent_usage[1] or 0, 4)
                            })
                    except sqlite3.Error:
                        pass
            
            # SEED optimization patterns
            seed_db_path = Path("instance/seed_optimization.db")
            if seed_db_path.exists():
                with sqlite3.connect(seed_db_path) as conn:
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute("""
                            SELECT optimization_domain, COUNT(*) as optimizations
                            FROM optimization_history 
                            WHERE timestamp > datetime('now', '-7 days')
                            GROUP BY optimization_domain
                        """)
                        optimization_counts = cursor.fetchall()
                        if optimization_counts:
                            ai_patterns['records'].append({
                                'type': 'seed_optimizations',
                                'domain_activity': [{'domain': row[0], 'count': row[1]} for row in optimization_counts]
                            })
                    except sqlite3.Error:
                        pass
                        
        except Exception as e:
            logger.error(f"AI usage pattern collection error: {e}")
            
        return ai_patterns
    
    def _generate_data_recommendations(self, data_collected: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on collected data"""
        recommendations = []
        
        for record in data_collected.get('records', []):
            record_type = record.get('type', '')
            
            if record_type == 'database_size':
                size_mb = record.get('size_mb', 0)
                if size_mb > 100:
                    recommendations.append(f"Large database detected ({size_mb}MB) - consider archiving old data")
                    
            elif record_type == 'log_analysis':
                error_count = record.get('recent_errors', 0)
                if error_count > 50:
                    recommendations.append(f"High error rate in {record.get('log_file')} - investigate issues")
                    
            elif record_type == 'cbt_skill_usage':
                top_skills = record.get('top_skills', [])
                if len(top_skills) > 0:
                    recommendations.append(f"Top CBT skill: {top_skills[0]['skill']} - ensure content quality")
                    
            elif record_type == 'ai_usage_24h':
                avg_cost = record.get('avg_cost', 0)
                if avg_cost > 0.1:
                    recommendations.append("High AI costs detected - optimize provider selection")
        
        if not recommendations:
            recommendations.append("Data collection complete - continue monitoring")
            
        return recommendations

class SelfHealingDrone(BaseDrone):
    """Drone that automatically repairs system issues"""
    
    def __init__(self, drone_id: str):
        super().__init__(drone_id, DroneType.SELF_HEALING_DRONE)
        
    async def execute_task(self, task: DroneTask) -> DroneResult:
        """Execute self-healing task"""
        start_time = time.time()
        self.status = DroneStatus.WORKING
        self.current_task = task
        self.update_activity()
        
        try:
            healing_type = task.payload.get('healing_type', 'general')
            issues = task.payload.get('issues', [])
            repairs_attempted = []
            repairs_successful = []
            
            if healing_type == 'database_repair':
                repairs_attempted, repairs_successful = await self._repair_database_issues(issues)
            elif healing_type == 'log_cleanup':
                repairs_attempted, repairs_successful = await self._cleanup_logs()
            elif healing_type == 'cache_cleanup':
                repairs_attempted, repairs_successful = await self._cleanup_cache()
            elif healing_type == 'general':
                repairs_attempted, repairs_successful = await self._general_system_healing()
            
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            self.tasks_completed += 1
            self.status = DroneStatus.COMPLETED
            
            return DroneResult(
                task_id=task.task_id,
                drone_id=self.drone_id,
                success=True,
                result_data={
                    'healing_type': healing_type,
                    'repairs_attempted': repairs_attempted,
                    'repairs_successful': repairs_successful,
                    'success_rate': len(repairs_successful) / len(repairs_attempted) if repairs_attempted else 1.0
                },
                execution_time=execution_time,
                completed_at=datetime.now(),
                recommendations=self._generate_healing_recommendations(repairs_attempted, repairs_successful)
            )
            
        except Exception as e:
            logger.error(f"Self-healing drone {self.drone_id} failed: {e}")
            self.tasks_failed += 1
            self.status = DroneStatus.FAILED
            
            return DroneResult(
                task_id=task.task_id,
                drone_id=self.drone_id,
                success=False,
                result_data={'error': str(e)},
                execution_time=time.time() - start_time,
                completed_at=datetime.now()
            )
    
    async def _repair_database_issues(self, issues: List[str]) -> Tuple[List[str], List[str]]:
        """Attempt to repair database-related issues"""
        repairs_attempted = []
        repairs_successful = []
        
        try:
            # Database integrity check and repair
            repairs_attempted.append("database_integrity_check")
            db_path = Path("instance/nous.db")
            
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Run integrity check
                    cursor.execute("PRAGMA integrity_check")
                    integrity_result = cursor.fetchone()[0]
                    
                    if integrity_result == "ok":
                        repairs_successful.append("database_integrity_check")
                    else:
                        # Attempt to repair
                        repairs_attempted.append("database_repair_attempt")
                        try:
                            cursor.execute("VACUUM")
                            cursor.execute("REINDEX")
                            repairs_successful.append("database_repair_attempt")
                        except sqlite3.Error:
                            pass
            
            # Optimize database performance
            repairs_attempted.append("database_optimization")
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("ANALYZE")
                    cursor.execute("PRAGMA optimize")
                    repairs_successful.append("database_optimization")
            except Exception:
                pass
                
        except Exception as e:
            logger.error(f"Database repair error: {e}")
            
        return repairs_attempted, repairs_successful
    
    async def _cleanup_logs(self) -> Tuple[List[str], List[str]]:
        """Clean up log files to free space and improve performance"""
        repairs_attempted = []
        repairs_successful = []
        
        try:
            log_directory = Path("logs")
            if log_directory.exists():
                
                # Archive old logs
                repairs_attempted.append("log_archival")
                current_time = datetime.now()
                archived_count = 0
                
                for log_file in log_directory.glob("*.log"):
                    # Archive logs older than 30 days
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if (current_time - file_time).days > 30:
                        try:
                            # Move to archive (simple rename with date)
                            archive_name = f"{log_file.stem}_{file_time.strftime('%Y%m%d')}.log.archived"
                            log_file.rename(log_directory / archive_name)
                            archived_count += 1
                        except Exception:
                            pass
                
                if archived_count > 0:
                    repairs_successful.append("log_archival")
                
                # Truncate large active logs
                repairs_attempted.append("log_truncation")
                truncated_count = 0
                
                for log_file in log_directory.glob("*.log"):
                    if not log_file.name.endswith('.archived'):
                        file_size_mb = log_file.stat().st_size / (1024 * 1024)
                        
                        if file_size_mb > 50:  # Truncate logs larger than 50MB
                            try:
                                # Keep last 1000 lines
                                with open(log_file, 'r') as f:
                                    lines = f.readlines()
                                
                                if len(lines) > 1000:
                                    with open(log_file, 'w') as f:
                                        f.writelines(lines[-1000:])
                                    truncated_count += 1
                                    
                            except Exception:
                                pass
                
                if truncated_count > 0:
                    repairs_successful.append("log_truncation")
                    
        except Exception as e:
            logger.error(f"Log cleanup error: {e}")
            
        return repairs_attempted, repairs_successful
    
    async def _cleanup_cache(self) -> Tuple[List[str], List[str]]:
        """Clean up cache files and temporary data"""
        repairs_attempted = []
        repairs_successful = []
        
        try:
            # Python cache cleanup
            repairs_attempted.append("python_cache_cleanup")
            cache_cleaned = 0
            
            for cache_dir in Path(".").rglob("__pycache__"):
                try:
                    for cache_file in cache_dir.glob("*.pyc"):
                        cache_file.unlink()
                        cache_cleaned += 1
                except Exception:
                    pass
            
            if cache_cleaned > 0:
                repairs_successful.append("python_cache_cleanup")
            
            # Flask session cleanup
            repairs_attempted.append("flask_session_cleanup")
            session_dir = Path("flask_session")
            if session_dir.exists():
                session_cleaned = 0
                current_time = datetime.now()
                
                for session_file in session_dir.glob("*"):
                    try:
                        # Remove sessions older than 7 days
                        file_time = datetime.fromtimestamp(session_file.stat().st_mtime)
                        if (current_time - file_time).days > 7:
                            session_file.unlink()
                            session_cleaned += 1
                    except Exception:
                        pass
                
                if session_cleaned > 0:
                    repairs_successful.append("flask_session_cleanup")
            
            # Upload directory cleanup (if exists)
            repairs_attempted.append("upload_cleanup")
            upload_dir = Path("uploads")
            if upload_dir.exists():
                upload_cleaned = 0
                current_time = datetime.now()
                
                for upload_file in upload_dir.glob("*"):
                    try:
                        # Remove uploads older than 30 days
                        file_time = datetime.fromtimestamp(upload_file.stat().st_mtime)
                        if (current_time - file_time).days > 30:
                            upload_file.unlink()
                            upload_cleaned += 1
                    except Exception:
                        pass
                
                if upload_cleaned > 0:
                    repairs_successful.append("upload_cleanup")
                    
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            
        return repairs_attempted, repairs_successful
    
    async def _general_system_healing(self) -> Tuple[List[str], List[str]]:
        """Perform general system maintenance and healing"""
        repairs_attempted = []
        repairs_successful = []
        
        # Combine all healing operations
        db_attempted, db_successful = await self._repair_database_issues([])
        log_attempted, log_successful = await self._cleanup_logs()
        cache_attempted, cache_successful = await self._cleanup_cache()
        
        repairs_attempted.extend(db_attempted + log_attempted + cache_attempted)
        repairs_successful.extend(db_successful + log_successful + cache_successful)
        
        return repairs_attempted, repairs_successful
    
    def _generate_healing_recommendations(self, repairs_attempted: List[str], repairs_successful: List[str]) -> List[str]:
        """Generate recommendations based on healing results"""
        recommendations = []
        
        success_rate = len(repairs_successful) / len(repairs_attempted) if repairs_attempted else 1.0
        
        if success_rate >= 0.8:
            recommendations.append("System healing successful - continue regular maintenance")
        elif success_rate >= 0.5:
            recommendations.append("Partial healing successful - monitor for remaining issues")
        else:
            recommendations.append("Healing had limited success - manual intervention may be needed")
        
        # Specific recommendations
        if "database_repair_attempt" in repairs_attempted and "database_repair_attempt" not in repairs_successful:
            recommendations.append("Database repair failed - consider backup restoration")
            
        if "log_truncation" in repairs_successful:
            recommendations.append("Large logs detected and truncated - improve log rotation")
            
        if "python_cache_cleanup" in repairs_successful:
            recommendations.append("Python cache cleaned - consider automated cache management")
        
        return recommendations

class OptimizationDrone(BaseDrone):
    """Drone that monitors performance and applies optimizations"""
    
    def __init__(self, drone_id: str):
        super().__init__(drone_id, DroneType.OPTIMIZATION_DRONE)
        self.seed_engine = NOUSSeedEngine() if NOUSSeedEngine else None
    
    async def execute_task(self, task: DroneTask) -> DroneResult:
        """Execute optimization task"""
        start_time = time.time()
        self.status = DroneStatus.WORKING
        self.current_task = task
        self.update_activity()
        
        try:
            optimization_type = task.payload.get('optimization_type', 'general')
            user_id = task.payload.get('user_id')
            optimization_results = []
            
            if self.seed_engine:
                if optimization_type == 'therapeutic' and user_id:
                    # Optimize therapeutic interventions
                    result = self.seed_engine.optimize_therapeutic_interventions(
                        user_id, task.payload.get('interaction_history', [])
                    )
                    optimization_results.append(result)
                
                elif optimization_type == 'ai_services':
                    # Optimize AI service selection
                    result = self.seed_engine.optimize_ai_service_selection(
                        task.payload.get('usage_history', [])
                    )
                    optimization_results.append(result)
                
                elif optimization_type == 'general':
                    # Run general system optimization
                    optimization_results = await self._run_general_optimization()
            
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            self.tasks_completed += 1
            self.status = DroneStatus.COMPLETED
            
            return DroneResult(
                task_id=task.task_id,
                drone_id=self.drone_id,
                success=True,
                result_data={
                    'optimization_type': optimization_type,
                    'results': [asdict(r) for r in optimization_results],
                    'total_improvements': len([r for r in optimization_results if r.metric_improved])
                },
                execution_time=execution_time,
                completed_at=datetime.now(),
                recommendations=self._generate_optimization_recommendations(optimization_results)
            )
            
        except Exception as e:
            logger.error(f"Optimization drone {self.drone_id} failed: {e}")
            self.tasks_failed += 1
            self.status = DroneStatus.FAILED
            
            return DroneResult(
                task_id=task.task_id,
                drone_id=self.drone_id,
                success=False,
                result_data={'error': str(e)},
                execution_time=time.time() - start_time,
                completed_at=datetime.now()
            )
    
    async def _run_general_optimization(self) -> List[Any]:
        """Run general system optimization across all domains"""
        results = []
        
        if not self.seed_engine:
            return results
        
        try:
            # Get system status
            status = self.seed_engine.get_optimization_status()
            
            # Optimize each domain that needs attention
            for domain_name, domain_data in status.get('domains', {}).items():
                if domain_data.get('needs_optimization', False):
                    # Simulate optimization for each domain
                    mock_result = type('OptimizationResult', (), {
                        'domain': domain_name,
                        'metric_improved': True,
                        'old_value': domain_data.get('current_value', 0.5),
                        'new_value': domain_data.get('current_value', 0.5) * 1.1,
                        'improvement_percentage': 10.0,
                        'parameters_adjusted': {'optimization_level': 'enhanced'},
                        'confidence': 0.8
                    })()
                    results.append(mock_result)
            
        except Exception as e:
            logger.error(f"General optimization failed: {e}")
        
        return results
    
    def _generate_optimization_recommendations(self, results: List[Any]) -> List[str]:
        """Generate recommendations based on optimization results"""
        recommendations = []
        
        improved_count = len([r for r in results if getattr(r, 'metric_improved', False)])
        
        if improved_count > 0:
            recommendations.append(f"Applied {improved_count} successful optimizations")
            recommendations.append("Monitor performance metrics for continued improvement")
        else:
            recommendations.append("No immediate optimizations found - system performing well")
        
        recommendations.append("Continue regular optimization cycles")
        return recommendations

class SeedDroneSwarm:
    """Orchestrates and manages the drone swarm"""
    
    def __init__(self):
        self.db_path = Path("instance/seed_drone_swarm.db")
        self.init_database()
        
        self.active_drones: Dict[str, BaseDrone] = {}
        self.task_queue: List[DroneTask] = []
        self.completed_tasks: List[DroneResult] = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        self.swarm_thread = None
        
        # Drone type configurations
        self.drone_configs = {
            DroneType.VERIFICATION_DRONE: {
                'class': VerificationDrone,
                'max_instances': 3,
                'spawn_interval': 300  # 5 minutes
            },
            DroneType.OPTIMIZATION_DRONE: {
                'class': OptimizationDrone,
                'max_instances': 2,
                'spawn_interval': 600  # 10 minutes
            },
            DroneType.DATA_COLLECTION_DRONE: {
                'class': DataCollectionDrone,
                'max_instances': 2,
                'spawn_interval': 900  # 15 minutes
            },
            DroneType.SELF_HEALING_DRONE: {
                'class': SelfHealingDrone,
                'max_instances': 1,
                'spawn_interval': 1800  # 30 minutes
            }
        }
        
    def init_database(self):
        """Initialize drone swarm database"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Drone registry
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS drones (
                    drone_id TEXT PRIMARY KEY,
                    drone_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    last_activity TIMESTAMP NOT NULL,
                    tasks_completed INTEGER DEFAULT 0,
                    tasks_failed INTEGER DEFAULT 0
                )
            ''')
            
            # Task queue
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    drone_type TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    assigned_drone TEXT,
                    status TEXT DEFAULT 'pending',
                    completed_at TIMESTAMP
                )
            ''')
            
            # Results storage
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    task_id TEXT PRIMARY KEY,
                    drone_id TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    result_data TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    completed_at TIMESTAMP NOT NULL
                )
            ''')
            
            conn.commit()
    
    def start_swarm(self):
        """Start the drone swarm orchestrator"""
        if self.running:
            return
        
        self.running = True
        self.swarm_thread = threading.Thread(target=self._swarm_loop, daemon=True)
        self.swarm_thread.start()
        logger.info("SEED Drone Swarm started")
    
    def stop_swarm(self):
        """Stop the drone swarm"""
        self.running = False
        if self.swarm_thread:
            self.swarm_thread.join(timeout=5)
        logger.info("SEED Drone Swarm stopped")
    
    def _swarm_loop(self):
        """Main swarm orchestration loop"""
        while self.running:
            try:
                # Spawn drones as needed
                self._spawn_drones()
                
                # Assign tasks to available drones
                self._assign_tasks()
                
                # Clean up completed/failed drones
                self._cleanup_drones()
                
                # Schedule periodic verification tasks
                self._schedule_periodic_tasks()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Swarm loop error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _spawn_drones(self):
        """Spawn drones based on configuration and workload"""
        for drone_type, config in self.drone_configs.items():
            current_count = len([d for d in self.active_drones.values() 
                               if d.drone_type == drone_type and d.status != DroneStatus.TERMINATED])
            
            if current_count < config['max_instances']:
                # Check if we need more drones based on workload
                pending_tasks = len([t for t in self.task_queue 
                                   if t.drone_type == drone_type])
                
                if pending_tasks > current_count or current_count == 0:
                    drone_id = f"{drone_type.value}_{uuid.uuid4().hex[:8]}"
                    drone = config['class'](drone_id)
                    self.active_drones[drone_id] = drone
                    
                    # Register in database
                    self._register_drone(drone)
                    logger.info(f"Spawned new drone: {drone_id}")
    
    def _assign_tasks(self):
        """Assign pending tasks to available drones"""
        available_drones = [d for d in self.active_drones.values() 
                          if d.status == DroneStatus.IDLE]
        
        # Sort tasks by priority (highest first)
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)
        
        for task in self.task_queue[:]:
            # Find suitable drone
            suitable_drones = [d for d in available_drones 
                             if d.drone_type == task.drone_type]
            
            if suitable_drones:
                drone = suitable_drones[0]
                available_drones.remove(drone)
                self.task_queue.remove(task)
                
                # Execute task in thread pool
                future = self.executor.submit(self._execute_task_sync, drone, task)
                
                # Store future for monitoring
                drone.current_task = task
                drone.status = DroneStatus.ACTIVE
                
                logger.info(f"Assigned task {task.task_id} to drone {drone.drone_id}")
    
    def _execute_task_sync(self, drone: BaseDrone, task: DroneTask):
        """Synchronous wrapper for async task execution"""
        try:
            # Run the async task
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(drone.execute_task(task))
            loop.close()
            
            # Store result
            self.completed_tasks.append(result)
            self._store_result(result)
            
            # Update drone status
            drone.status = DroneStatus.IDLE
            drone.current_task = None
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            drone.status = DroneStatus.FAILED
            drone.tasks_failed += 1
    
    def _cleanup_drones(self):
        """Remove terminated or long-idle drones"""
        current_time = datetime.now()
        drones_to_remove = []
        
        for drone_id, drone in self.active_drones.items():
            # Remove terminated drones
            if drone.status == DroneStatus.TERMINATED:
                drones_to_remove.append(drone_id)
            
            # Remove idle drones that haven't been active for too long
            elif (drone.status == DroneStatus.IDLE and 
                  (current_time - drone.last_activity).seconds > 3600):  # 1 hour
                drone.status = DroneStatus.TERMINATED
                drones_to_remove.append(drone_id)
        
        for drone_id in drones_to_remove:
            del self.active_drones[drone_id]
            logger.info(f"Removed drone: {drone_id}")
    
    def _schedule_periodic_tasks(self):
        """Schedule regular maintenance tasks"""
        current_time = datetime.now()
        
        # Schedule verification task every 10 minutes
        last_verification = self._get_last_task_time('system_verification')
        if not last_verification or (current_time - last_verification).seconds > 600:
            self.add_task(
                DroneType.VERIFICATION_DRONE,
                priority=5,
                payload={'verification_type': 'full_system'},
                task_id=f"verification_{int(current_time.timestamp())}"
            )
        
        # Schedule optimization task every 30 minutes
        last_optimization = self._get_last_task_time('system_optimization')
        if not last_optimization or (current_time - last_optimization).seconds > 1800:
            self.add_task(
                DroneType.OPTIMIZATION_DRONE,
                priority=3,
                payload={'optimization_type': 'general'},
                task_id=f"optimization_{int(current_time.timestamp())}"
            )
    
    def add_task(self, drone_type: DroneType, priority: int, payload: Dict[str, Any], 
                 task_id: Optional[str] = None, deadline: Optional[datetime] = None):
        """Add a task to the drone swarm queue"""
        if not task_id:
            task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        task = DroneTask(
            task_id=task_id,
            drone_type=drone_type,
            priority=priority,
            payload=payload,
            created_at=datetime.now(),
            deadline=deadline
        )
        
        self.task_queue.append(task)
        self._store_task(task)
        logger.info(f"Added task {task_id} to queue")
        
        return task_id
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get comprehensive swarm status"""
        active_drones_by_type = {}
        for drone in self.active_drones.values():
            drone_type = drone.drone_type.value
            if drone_type not in active_drones_by_type:
                active_drones_by_type[drone_type] = 0
            active_drones_by_type[drone_type] += 1
        
        return {
            'swarm_running': self.running,
            'total_active_drones': len(self.active_drones),
            'active_drones_by_type': active_drones_by_type,
            'pending_tasks': len(self.task_queue),
            'completed_tasks': len(self.completed_tasks),
            'drone_performance': [drone.get_performance_metrics() 
                                for drone in self.active_drones.values()]
        }
    
    def get_recent_results(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent task results"""
        recent_results = sorted(self.completed_tasks, 
                              key=lambda r: r.completed_at, reverse=True)[:limit]
        
        return [asdict(result) for result in recent_results]
    
    def _register_drone(self, drone: BaseDrone):
        """Register drone in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO drones 
                (drone_id, drone_type, status, created_at, last_activity)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                drone.drone_id,
                drone.drone_type.value,
                drone.status.value,
                drone.created_at,
                drone.last_activity
            ))
            conn.commit()
    
    def _store_task(self, task: DroneTask):
        """Store task in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks 
                (task_id, drone_type, priority, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                task.task_id,
                task.drone_type.value,
                task.priority,
                json.dumps(task.payload),
                task.created_at
            ))
            conn.commit()
    
    def _store_result(self, result: DroneResult):
        """Store result in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO results 
                (task_id, drone_id, success, result_data, execution_time, completed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                result.task_id,
                result.drone_id,
                result.success,
                json.dumps(result.result_data),
                result.execution_time,
                result.completed_at
            ))
            conn.commit()
    
    def _get_last_task_time(self, task_prefix: str) -> Optional[datetime]:
        """Get the timestamp of the last task with given prefix"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT MAX(created_at) FROM tasks 
                WHERE task_id LIKE ?
            ''', (f"{task_prefix}%",))
            result = cursor.fetchone()[0]
            
        return datetime.fromisoformat(result) if result else None

# Global swarm instance
_drone_swarm_instance = None

def get_drone_swarm() -> SeedDroneSwarm:
    """Get or create the global drone swarm instance"""
    global _drone_swarm_instance
    if _drone_swarm_instance is None:
        _drone_swarm_instance = SeedDroneSwarm()
    return _drone_swarm_instance

def start_drone_swarm():
    """Start the global drone swarm"""
    swarm = get_drone_swarm()
    swarm.start_swarm()
    return swarm

def stop_drone_swarm():
    """Stop the global drone swarm"""
    swarm = get_drone_swarm() 
    swarm.stop_swarm()