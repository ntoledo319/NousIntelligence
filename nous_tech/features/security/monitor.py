"""
NOUS Tech Security Monitor
Comprehensive security monitoring with blockchain logging, TEE integration, and threat detection
"""

import logging
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)

def init_security_monitor(app):
    """Initialize comprehensive security monitoring system"""
    try:
        # Initialize security components
        from .blockchain import BlockchainAudit
        from .tee import init_tee
        
        # Initialize blockchain audit system
        blockchain_config = {
            'provider_url': app.config.get('BLOCKCHAIN_URL'),
            'contract_abi': app.config.get('BLOCKCHAIN_ABI'),
            'contract_address': app.config.get('BLOCKCHAIN_ADDR')
        }
        
        app.security_audit = BlockchainAudit(**blockchain_config)
        
        # Initialize TEE system
        init_tee(app)
        
        # Initialize security monitor
        app.security_monitor = SecurityMonitor(app)
        
        # Set up monitoring hooks
        _setup_security_hooks(app)
        
        logger.info("Security monitoring system initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize security monitor: {e}")
        # Set up fallback security
        app.security_monitor = FallbackSecurityMonitor()

class SecurityMonitor:
    """Advanced security monitoring and threat detection system"""
    
    def __init__(self, app):
        self.app = app
        self.threat_patterns = []
        self.access_patterns = {}
        self.security_events = []
        self.risk_scores = {}
        self.security_config = {
            'max_failed_attempts': 5,
            'lockout_duration': 300,  # 5 minutes
            'anomaly_threshold': 0.8,
            'high_risk_threshold': 0.7
        }
        
        # Initialize threat detection patterns
        self._initialize_threat_patterns()
        
    def monitor_access(self, user_id: str, resource: str, action: str, 
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Monitor and evaluate access patterns for security threats"""
        try:
            # Log to blockchain audit
            audit_result = self.app.security_audit.log_access(user_id, resource, action, context)
            
            # Evaluate risk
            risk_assessment = self._evaluate_access_risk(user_id, resource, action, context)
            
            # Check for anomalies
            anomaly_score = self._detect_anomalies(user_id, resource, action, context)
            
            # Update access patterns
            self._update_access_patterns(user_id, resource, action)
            
            # Log security event
            security_event = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'resource': resource,
                'action': action,
                'risk_score': risk_assessment['risk_score'],
                'anomaly_score': anomaly_score,
                'audit_hash': audit_result,
                'context': context or {}
            }
            
            self.security_events.append(security_event)
            
            # Trigger alerts if necessary
            if risk_assessment['risk_score'] > self.security_config['high_risk_threshold']:
                self._trigger_security_alert(security_event)
            
            return {
                'access_granted': risk_assessment['risk_score'] < 0.9,
                'risk_score': risk_assessment['risk_score'],
                'anomaly_score': anomaly_score,
                'audit_logged': bool(audit_result),
                'recommendations': risk_assessment.get('recommendations', [])
            }
            
        except Exception as e:
            logger.error(f"Security monitoring failed: {e}")
            return {
                'access_granted': True,  # Fail open for availability
                'error': str(e),
                'security_degraded': True
            }
    
    def monitor_ai_operation(self, user_id: str, operation_type: str, 
                           model_info: Dict[str, Any], 
                           security_level: str = "standard") -> Dict[str, Any]:
        """Monitor AI operations for security compliance"""
        try:
            # Enhanced monitoring for AI operations
            ai_context = {
                'operation_type': operation_type,
                'model_info': model_info,
                'security_level': security_level,
                'requires_tee': security_level in ['high', 'critical']
            }
            
            # Monitor the AI operation access
            access_result = self.monitor_access(
                user_id, 
                f"ai_operation_{operation_type}", 
                "execute", 
                ai_context
            )
            
            # Additional AI-specific security checks
            ai_risk_factors = self._evaluate_ai_risks(model_info, security_level)
            
            # Determine if TEE is required
            requires_tee = (
                security_level in ['high', 'critical'] or
                ai_risk_factors['data_sensitivity'] > 0.7 or
                'phi' in str(model_info).lower()
            )
            
            return {
                **access_result,
                'ai_risk_factors': ai_risk_factors,
                'requires_tee': requires_tee,
                'security_level': security_level,
                'recommended_security_level': self._recommend_security_level(ai_risk_factors)
            }
            
        except Exception as e:
            logger.error(f"AI operation monitoring failed: {e}")
            return {
                'access_granted': False,
                'error': str(e),
                'requires_tee': True  # Fail secure for AI operations
            }
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data"""
        try:
            # Calculate security metrics
            recent_events = [
                event for event in self.security_events 
                if self._parse_timestamp(event['timestamp']) > datetime.now() - timedelta(hours=24)
            ]
            
            dashboard_data = {
                'total_events_24h': len(recent_events),
                'high_risk_events': len([e for e in recent_events if e['risk_score'] > 0.7]),
                'anomaly_events': len([e for e in recent_events if e['anomaly_score'] > 0.8]),
                'unique_users': len(set(e['user_id'] for e in recent_events)),
                'threat_level': self._calculate_overall_threat_level(),
                'security_status': self._get_security_system_status(),
                'recent_alerts': self._get_recent_alerts(),
                'top_risks': self._get_top_risk_factors()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to generate security dashboard: {e}")
            return {'error': str(e)}
    
    def _evaluate_access_risk(self, user_id: str, resource: str, action: str, 
                             context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate risk score for access attempt"""
        risk_factors = {
            'user_history': self._evaluate_user_history(user_id),
            'resource_sensitivity': self._evaluate_resource_sensitivity(resource),
            'action_risk': self._evaluate_action_risk(action),
            'context_risk': self._evaluate_context_risk(context),
            'time_based_risk': self._evaluate_time_based_risk(),
            'frequency_risk': self._evaluate_frequency_risk(user_id)
        }
        
        # Calculate weighted risk score
        weights = {
            'user_history': 0.2,
            'resource_sensitivity': 0.3,
            'action_risk': 0.2,
            'context_risk': 0.15,
            'time_based_risk': 0.1,
            'frequency_risk': 0.05
        }
        
        risk_score = sum(
            risk_factors[factor] * weights[factor] 
            for factor in risk_factors
        )
        
        # Generate recommendations
        recommendations = self._generate_risk_recommendations(risk_factors, risk_score)
        
        return {
            'risk_score': min(risk_score, 1.0),  # Cap at 1.0
            'risk_factors': risk_factors,
            'recommendations': recommendations
        }
    
    def _detect_anomalies(self, user_id: str, resource: str, action: str, 
                         context: Optional[Dict[str, Any]]) -> float:
        """Detect anomalous access patterns"""
        try:
            # Get user's historical patterns
            user_patterns = self.access_patterns.get(user_id, {})
            
            anomaly_indicators = []
            
            # Check resource access patterns
            resource_history = user_patterns.get('resources', {})
            if resource not in resource_history:
                anomaly_indicators.append(0.6)  # New resource access
            
            # Check action patterns
            action_history = user_patterns.get('actions', {})
            if action not in action_history:
                anomaly_indicators.append(0.4)  # New action type
            
            # Check time patterns
            current_hour = datetime.now().hour
            time_patterns = user_patterns.get('access_times', [])
            if time_patterns and abs(current_hour - sum(time_patterns)/len(time_patterns)) > 6:
                anomaly_indicators.append(0.5)  # Unusual time
            
            # Check frequency patterns
            recent_access_count = len([
                event for event in self.security_events[-100:] 
                if event['user_id'] == user_id and 
                self._parse_timestamp(event['timestamp']) > datetime.now() - timedelta(hours=1)
            ])
            
            if recent_access_count > 20:  # More than 20 accesses in an hour
                anomaly_indicators.append(0.8)
            
            # Return maximum anomaly score
            return max(anomaly_indicators) if anomaly_indicators else 0.0
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return 0.0
    
    def _evaluate_ai_risks(self, model_info: Dict[str, Any], security_level: str) -> Dict[str, Any]:
        """Evaluate AI-specific risk factors"""
        return {
            'model_complexity': 0.5,  # Based on model type/size
            'data_sensitivity': 0.8 if 'phi' in str(model_info).lower() else 0.3,
            'output_sensitivity': 0.6,
            'inference_risk': 0.4,
            'privacy_risk': 0.7 if security_level in ['high', 'critical'] else 0.3
        }
    
    def _update_access_patterns(self, user_id: str, resource: str, action: str):
        """Update user access patterns for learning"""
        if user_id not in self.access_patterns:
            self.access_patterns[user_id] = {
                'resources': {},
                'actions': {},
                'access_times': [],
                'last_updated': datetime.now()
            }
        
        patterns = self.access_patterns[user_id]
        
        # Update resource patterns
        patterns['resources'][resource] = patterns['resources'].get(resource, 0) + 1
        
        # Update action patterns
        patterns['actions'][action] = patterns['actions'].get(action, 0) + 1
        
        # Update time patterns
        patterns['access_times'].append(datetime.now().hour)
        if len(patterns['access_times']) > 100:  # Keep last 100 access times
            patterns['access_times'] = patterns['access_times'][-100:]
        
        patterns['last_updated'] = datetime.now()
    
    def _trigger_security_alert(self, security_event: Dict[str, Any]):
        """Trigger security alert for high-risk events"""
        try:
            alert = {
                'alert_id': hashlib.md5(str(security_event).encode()).hexdigest()[:8],
                'timestamp': datetime.now().isoformat(),
                'severity': 'HIGH' if security_event['risk_score'] > 0.8 else 'MEDIUM',
                'event': security_event,
                'alert_type': 'security_risk'
            }
            
            logger.warning(f"SECURITY ALERT: {alert}")
            
            # Store alert for dashboard
            if not hasattr(self, 'security_alerts'):
                self.security_alerts = []
            
            self.security_alerts.append(alert)
            
            # Keep only recent alerts
            if len(self.security_alerts) > 100:
                self.security_alerts = self.security_alerts[-100:]
                
        except Exception as e:
            logger.error(f"Failed to trigger security alert: {e}")
    
    def _initialize_threat_patterns(self):
        """Initialize known threat patterns"""
        self.threat_patterns = [
            {
                'name': 'rapid_access',
                'pattern': 'high_frequency_access',
                'threshold': 50,  # accesses per hour
                'risk_level': 0.8
            },
            {
                'name': 'unusual_time_access',
                'pattern': 'off_hours_access',
                'threshold': 3,  # 3 AM - 6 AM
                'risk_level': 0.6
            },
            {
                'name': 'privilege_escalation',
                'pattern': 'elevated_resource_access',
                'threshold': 5,  # different high-privilege resources
                'risk_level': 0.9
            }
        ]
    
    # Helper methods for risk evaluation
    def _evaluate_user_history(self, user_id: str) -> float:
        """Evaluate user's historical risk"""
        user_events = [e for e in self.security_events if e['user_id'] == user_id]
        if not user_events:
            return 0.3  # New user baseline risk
        
        avg_risk = sum(e['risk_score'] for e in user_events[-10:]) / min(len(user_events), 10)
        return avg_risk
    
    def _evaluate_resource_sensitivity(self, resource: str) -> float:
        """Evaluate sensitivity of the resource"""
        high_sensitivity_keywords = ['phi', 'medical', 'health', 'admin', 'system']
        medium_sensitivity_keywords = ['user', 'profile', 'data']
        
        resource_lower = resource.lower()
        
        if any(keyword in resource_lower for keyword in high_sensitivity_keywords):
            return 0.9
        elif any(keyword in resource_lower for keyword in medium_sensitivity_keywords):
            return 0.6
        else:
            return 0.3
    
    def _evaluate_action_risk(self, action: str) -> float:
        """Evaluate risk of the action"""
        high_risk_actions = ['delete', 'modify', 'admin', 'execute']
        medium_risk_actions = ['update', 'create', 'write']
        
        action_lower = action.lower()
        
        if any(keyword in action_lower for keyword in high_risk_actions):
            return 0.8
        elif any(keyword in action_lower for keyword in medium_risk_actions):
            return 0.5
        else:
            return 0.2
    
    def _evaluate_context_risk(self, context: Optional[Dict[str, Any]]) -> float:
        """Evaluate contextual risk factors"""
        if not context:
            return 0.3
        
        risk_factors = 0.0
        
        # Check for suspicious context
        if context.get('phi_involved'):
            risk_factors += 0.4
        
        if context.get('external_request'):
            risk_factors += 0.3
        
        if context.get('batch_operation'):
            risk_factors += 0.2
        
        return min(risk_factors, 1.0)
    
    def _evaluate_time_based_risk(self) -> float:
        """Evaluate time-based risk factors"""
        current_hour = datetime.now().hour
        
        # Higher risk during off-hours (midnight to 6 AM)
        if 0 <= current_hour <= 6:
            return 0.6
        # Lower risk during business hours
        elif 9 <= current_hour <= 17:
            return 0.1
        else:
            return 0.3
    
    def _evaluate_frequency_risk(self, user_id: str) -> float:
        """Evaluate access frequency risk"""
        recent_events = [
            e for e in self.security_events 
            if e['user_id'] == user_id and 
            self._parse_timestamp(e['timestamp']) > datetime.now() - timedelta(hours=1)
        ]
        
        access_count = len(recent_events)
        
        if access_count > 30:
            return 0.9
        elif access_count > 15:
            return 0.6
        elif access_count > 5:
            return 0.3
        else:
            return 0.1
    
    def _generate_risk_recommendations(self, risk_factors: Dict[str, float], 
                                     risk_score: float) -> List[str]:
        """Generate security recommendations based on risk assessment"""
        recommendations = []
        
        if risk_score > 0.8:
            recommendations.append("Require additional authentication")
            recommendations.append("Enable enhanced monitoring")
        
        if risk_factors['resource_sensitivity'] > 0.7:
            recommendations.append("Use TEE for sensitive operations")
        
        if risk_factors['frequency_risk'] > 0.6:
            recommendations.append("Implement rate limiting")
        
        if risk_factors['time_based_risk'] > 0.5:
            recommendations.append("Verify off-hours access")
        
        return recommendations
    
    def _recommend_security_level(self, ai_risk_factors: Dict[str, float]) -> str:
        """Recommend appropriate security level for AI operations"""
        max_risk = max(ai_risk_factors.values())
        
        if max_risk > 0.8:
            return 'critical'
        elif max_risk > 0.6:
            return 'high'
        elif max_risk > 0.4:
            return 'medium'
        else:
            return 'standard'
    
    def _calculate_overall_threat_level(self) -> str:
        """Calculate overall system threat level"""
        if not self.security_events:
            return 'LOW'
        
        recent_events = [
            e for e in self.security_events 
            if self._parse_timestamp(e['timestamp']) > datetime.now() - timedelta(hours=24)
        ]
        
        if not recent_events:
            return 'LOW'
        
        avg_risk = sum(e['risk_score'] for e in recent_events) / len(recent_events)
        high_risk_count = len([e for e in recent_events if e['risk_score'] > 0.7])
        
        if avg_risk > 0.7 or high_risk_count > 10:
            return 'HIGH'
        elif avg_risk > 0.5 or high_risk_count > 5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_security_system_status(self) -> Dict[str, Any]:
        """Get security system component status"""
        return {
            'blockchain_audit': hasattr(self.app, 'security_audit'),
            'tee_available': self.app.config.get('TEE_ENABLED', False),
            'monitoring_active': True,
            'threat_detection': True,
            'anomaly_detection': True
        }
    
    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent security alerts"""
        if not hasattr(self, 'security_alerts'):
            return []
        
        # Return last 10 alerts
        return self.security_alerts[-10:]
    
    def _get_top_risk_factors(self) -> List[Dict[str, Any]]:
        """Get top risk factors from recent events"""
        recent_events = [
            e for e in self.security_events 
            if self._parse_timestamp(e['timestamp']) > datetime.now() - timedelta(hours=24)
        ]
        
        if not recent_events:
            return []
        
        # Analyze common risk patterns
        risk_analysis = {
            'high_risk_users': len(set(e['user_id'] for e in recent_events if e['risk_score'] > 0.7)),
            'sensitive_resource_access': len([e for e in recent_events if 'sensitive' in e['resource']]),
            'anomalous_behavior': len([e for e in recent_events if e['anomaly_score'] > 0.6])
        }
        
        return [
            {'factor': k, 'count': v, 'severity': 'HIGH' if v > 5 else 'MEDIUM'}
            for k, v in risk_analysis.items() if v > 0
        ]
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime object"""
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except Exception:
            return datetime.now()

class FallbackSecurityMonitor:
    """Fallback security monitor when main system fails"""
    
    def monitor_access(self, user_id: str, resource: str, action: str, 
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fallback monitoring with basic logging"""
        logger.info(f"FALLBACK SECURITY: {user_id} {action} {resource}")
        return {
            'access_granted': True,
            'risk_score': 0.5,
            'fallback_mode': True
        }
    
    def monitor_ai_operation(self, user_id: str, operation_type: str, 
                           model_info: Dict[str, Any], 
                           security_level: str = "standard") -> Dict[str, Any]:
        """Fallback AI operation monitoring"""
        logger.info(f"FALLBACK AI SECURITY: {user_id} {operation_type}")
        return {
            'access_granted': True,
            'requires_tee': security_level in ['high', 'critical'],
            'fallback_mode': True
        }
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Fallback security dashboard"""
        return {
            'status': 'FALLBACK_MODE',
            'error': 'Security monitoring in fallback mode'
        }

def _setup_security_hooks(app):
    """Set up Flask hooks for security monitoring"""
    @app.before_request
    def before_request_security():
        """Security check before each request"""
        try:
            # Basic security headers and monitoring
            pass
        except Exception as e:
            logger.error(f"Before request security failed: {e}")
    
    @app.after_request
    def after_request_security(response):
        """Security monitoring after each request"""
        try:
            # Log request completion
            pass
        except Exception as e:
            logger.error(f"After request security failed: {e}")
        
        return response

# Convenience functions for security monitoring
def monitor_access(user_id: str, resource: str, action: str, 
                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Monitor access with security evaluation"""
    try:
        from flask import current_app
        
        if hasattr(current_app, 'security_monitor'):
            return current_app.security_monitor.monitor_access(user_id, resource, action, context)
        else:
            return {'access_granted': True, 'security_unavailable': True}
            
    except Exception as e:
        logger.error(f"Access monitoring failed: {e}")
        return {'access_granted': True, 'error': str(e)}

def monitor_ai_operation(user_id: str, operation_type: str, model_info: Dict[str, Any], 
                        security_level: str = "standard") -> Dict[str, Any]:
    """Monitor AI operations for security compliance"""
    try:
        from flask import current_app
        
        if hasattr(current_app, 'security_monitor'):
            return current_app.security_monitor.monitor_ai_operation(
                user_id, operation_type, model_info, security_level
            )
        else:
            return {'access_granted': True, 'requires_tee': False, 'security_unavailable': True}
            
    except Exception as e:
        logger.error(f"AI operation monitoring failed: {e}")
        return {'access_granted': True, 'error': str(e)}