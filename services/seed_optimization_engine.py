"""
SEED Optimization Engine for NOUS Platform
Self-Optimization and Learning Engine adapted for comprehensive mental health and personal assistance

This engine integrates with existing NOUS features to provide adaptive learning across:
- Therapeutic interventions (CBT, DBT, AA)
- AI service optimization
- User engagement patterns
- Predictive analytics enhancement
- Multi-modal interaction optimization
"""

import logging
import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# Import existing NOUS services (with fallbacks)
try:
    from utils.unified_ai_service import UnifiedAIService
except ImportError:
    UnifiedAIService = None

try:
    from utils.ai_brain_cost_optimizer import get_ai_optimization_report
except ImportError:
    get_ai_optimization_report = None

try:
    from services.predictive_analytics import PredictiveAnalyticsEngine
except ImportError:
    PredictiveAnalyticsEngine = None

logger = logging.getLogger(__name__)

class OptimizationDomain(Enum):
    """Different domains for SEED optimization"""
    THERAPEUTIC = "therapeutic"
    AI_SERVICES = "ai_services"
    USER_ENGAGEMENT = "user_engagement"
    CONTENT_DELIVERY = "content_delivery"
    PREDICTIVE_ACCURACY = "predictive_accuracy"
    CRISIS_PREVENTION = "crisis_prevention"

@dataclass
class OptimizationMetric:
    """Represents a metric to be optimized"""
    domain: OptimizationDomain
    metric_name: str
    current_value: float
    target_value: float
    improvement_direction: str  # 'increase' or 'decrease'
    weight: float = 1.0

@dataclass
class OptimizationResult:
    """Result of an optimization cycle"""
    domain: OptimizationDomain
    metric_improved: bool
    old_value: float
    new_value: float
    improvement_percentage: float
    parameters_adjusted: Dict[str, Any]
    confidence: float

class NOUSSeedEngine:
    """
    Main SEED optimization engine for NOUS platform
    Adapts the SEED concept to work across all major NOUS systems
    """
    
    def __init__(self):
        """Initialize the SEED engine with connections to existing services"""
        self.db_path = Path("instance/seed_optimization.db")
        self.init_database()
        
        # Initialize connections to existing services with fallbacks
        self.ai_service = UnifiedAIService() if UnifiedAIService else None
        self.predictive_engine = PredictiveAnalyticsEngine() if PredictiveAnalyticsEngine else None
        self.therapeutic_assistant = None  # Will be initialized when needed
        
        # Optimization history
        self.optimization_history = []
        
        # Current optimization parameters for each domain
        self.domain_parameters = {
            OptimizationDomain.THERAPEUTIC: {
                'intervention_timing_threshold': 0.7,
                'skill_recommendation_confidence': 0.8,
                'crisis_detection_sensitivity': 0.85,
                'personalization_weight': 0.9
            },
            OptimizationDomain.AI_SERVICES: {
                'cost_vs_quality_threshold': 0.75,
                'local_processing_preference': 0.8,
                'cache_retention_days': 30,
                'premium_api_trigger': 0.9
            },
            OptimizationDomain.USER_ENGAGEMENT: {
                'notification_frequency': 0.6,
                'feature_suggestion_timing': 0.7,
                'content_complexity_level': 0.5,
                'interaction_style_adaptation': 0.8
            }
        }
        
        logger.info("NOUS SEED Engine initialized successfully")
    
    def init_database(self):
        """Initialize the SEED optimization database"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Optimization cycles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimization_cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    user_id TEXT,
                    cycle_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metrics_before TEXT NOT NULL,
                    metrics_after TEXT NOT NULL,
                    parameters_adjusted TEXT NOT NULL,
                    improvement_achieved REAL NOT NULL,
                    confidence_score REAL NOT NULL
                )
            """)
            
            # Learning patterns table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    effectiveness_score REAL NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    last_successful TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User-specific optimizations
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_optimizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    optimization_key TEXT NOT NULL,
                    optimization_value TEXT NOT NULL,
                    effectiveness_score REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, domain, optimization_key)
                )
            """)
            
            # Global optimization insights
            conn.execute("""
                CREATE TABLE IF NOT EXISTS global_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_type TEXT NOT NULL,
                    insight_data TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    impact_score REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def optimize_therapeutic_interventions(self, user_id: str, recent_interactions: List[Dict]) -> OptimizationResult:
        """
        Optimize therapeutic interventions based on user response patterns
        Integrates with existing CBT, DBT, and AA systems
        """
        domain = OptimizationDomain.THERAPEUTIC
        
        try:
            # Analyze current therapeutic effectiveness
            current_metrics = self._analyze_therapeutic_effectiveness(user_id, recent_interactions)
            
            # Get current parameters
            current_params = self.domain_parameters[domain].copy()
            
            # Apply SEED-style optimization
            if len(recent_interactions) > 5:  # Need sufficient data
                # Analyze what's working vs not working
                effectiveness_patterns = self._find_therapeutic_patterns(recent_interactions)
                
                # Adjust parameters based on patterns
                new_params = self._optimize_therapeutic_parameters(
                    current_params, effectiveness_patterns, current_metrics
                )
                
                # Calculate improvement
                improvement = self._calculate_therapeutic_improvement(
                    current_metrics, effectiveness_patterns
                )
                
                # Update parameters
                self.domain_parameters[domain] = new_params
                
                # Store optimization cycle
                self._store_optimization_cycle(
                    domain, user_id, current_metrics, improvement, new_params
                )
                
                return OptimizationResult(
                    domain=domain,
                    metric_improved=improvement > 0,
                    old_value=current_metrics.get('overall_effectiveness', 0.5),
                    new_value=current_metrics.get('overall_effectiveness', 0.5) + improvement,
                    improvement_percentage=improvement * 100,
                    parameters_adjusted=new_params,
                    confidence=min(0.95, len(recent_interactions) / 20)
                )
            
        except Exception as e:
            logger.error(f"Therapeutic optimization error: {e}")
        
        return OptimizationResult(
            domain=domain,
            metric_improved=False,
            old_value=0.5,
            new_value=0.5,
            improvement_percentage=0.0,
            parameters_adjusted={},
            confidence=0.0
        )
    
    def optimize_ai_service_selection(self, usage_history: List[Dict]) -> OptimizationResult:
        """
        Optimize AI service provider selection based on cost vs quality outcomes
        Integrates with existing AI service management
        """
        domain = OptimizationDomain.AI_SERVICES
        
        try:
            # Get current AI cost metrics with fallbacks
            if self.ai_service and hasattr(self.ai_service, 'get_cost_report'):
                cost_report = self.ai_service.get_cost_report()
                current_metrics = {
                    'cost_per_request': cost_report.get('cost_per_user', 0.5),
                    'quality_score': self._calculate_ai_quality_score(usage_history),
                    'response_time': self._calculate_avg_response_time(usage_history)
                }
            else:
                # Fallback metrics when service unavailable
                current_metrics = {
                    'cost_per_request': 0.5,
                    'quality_score': 0.7,
                    'response_time': 2.0
                }
            
            # Analyze provider performance patterns
            provider_effectiveness = self._analyze_provider_effectiveness(usage_history)
            
            # Optimize provider selection parameters
            current_params = self.domain_parameters[domain]
            new_params = self._optimize_ai_parameters(
                current_params, provider_effectiveness, current_metrics
            )
            
            # Calculate improvement potential
            improvement = self._calculate_ai_improvement(
                current_metrics, provider_effectiveness
            )
            
            # Update parameters
            self.domain_parameters[domain] = new_params
            
            # Store optimization
            self._store_optimization_cycle(
                domain, None, current_metrics, improvement, new_params
            )
            
            return OptimizationResult(
                domain=domain,
                metric_improved=improvement > 0,
                old_value=current_metrics['cost_per_request'],
                new_value=current_metrics['cost_per_request'] * (1 - improvement),
                improvement_percentage=improvement * 100,
                parameters_adjusted=new_params,
                confidence=min(0.9, len(usage_history) / 50)
            )
            
        except Exception as e:
            logger.error(f"AI service optimization error: {e}")
        
        return OptimizationResult(
            domain=domain,
            metric_improved=False,
            old_value=0.5,
            new_value=0.5,
            improvement_percentage=0.0,
            parameters_adjusted={},
            confidence=0.0
        )
    
    def optimize_user_engagement(self, user_id: str, engagement_data: List[Dict]) -> OptimizationResult:
        """
        Optimize user engagement patterns and notification timing
        Integrates with existing analytics and notification systems
        """
        domain = OptimizationDomain.USER_ENGAGEMENT
        
        try:
            # Analyze current engagement patterns
            current_metrics = self._analyze_engagement_metrics(user_id, engagement_data)
            
            # Find optimal engagement patterns
            engagement_patterns = self._find_engagement_patterns(engagement_data)
            
            # Optimize engagement parameters
            current_params = self.domain_parameters[domain]
            new_params = self._optimize_engagement_parameters(
                current_params, engagement_patterns, current_metrics
            )
            
            # Calculate improvement
            improvement = self._calculate_engagement_improvement(
                current_metrics, engagement_patterns
            )
            
            # Update parameters
            self.domain_parameters[domain] = new_params
            
            # Store optimization
            self._store_optimization_cycle(
                domain, user_id, current_metrics, improvement, new_params
            )
            
            return OptimizationResult(
                domain=domain,
                metric_improved=improvement > 0,
                old_value=current_metrics.get('engagement_score', 0.5),
                new_value=current_metrics.get('engagement_score', 0.5) + improvement,
                improvement_percentage=improvement * 100,
                parameters_adjusted=new_params,
                confidence=min(0.85, len(engagement_data) / 30)
            )
            
        except Exception as e:
            logger.error(f"Engagement optimization error: {e}")
        
        return OptimizationResult(
            domain=domain,
            metric_improved=False,
            old_value=0.5,
            new_value=0.5,
            improvement_percentage=0.0,
            parameters_adjusted={},
            confidence=0.0
        )
    
    def run_comprehensive_optimization(self, user_id: str = None) -> Dict[str, OptimizationResult]:
        """
        Run optimization across all domains for maximum system improvement
        """
        results = {}
        
        try:
            # Get relevant data for all optimizations
            if user_id:
                # User-specific optimization
                therapeutic_data = self._get_user_therapeutic_data(user_id)
                engagement_data = self._get_user_engagement_data(user_id)
                
                # Run user-specific optimizations
                results['therapeutic'] = self.optimize_therapeutic_interventions(
                    user_id, therapeutic_data
                )
                results['engagement'] = self.optimize_user_engagement(
                    user_id, engagement_data
                )
            
            # System-wide optimizations
            ai_usage_data = self._get_ai_usage_data()
            results['ai_services'] = self.optimize_ai_service_selection(ai_usage_data)
            
            # Generate global insights
            self._generate_global_insights(results)
            
        except Exception as e:
            logger.error(f"Comprehensive optimization error: {e}")
        
        return results
    
    def get_optimization_recommendations(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Get current optimization recommendations based on learned patterns
        """
        recommendations = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get user-specific optimizations if user_id provided
                if user_id:
                    cursor = conn.execute("""
                        SELECT domain, optimization_key, optimization_value, effectiveness_score
                        FROM user_optimizations
                        WHERE user_id = ? AND effectiveness_score > 0.6
                        ORDER BY effectiveness_score DESC
                        LIMIT 10
                    """, (user_id,))
                    
                    for row in cursor.fetchall():
                        recommendations.append({
                            'type': 'personal',
                            'domain': row[0],
                            'recommendation': row[1],
                            'value': json.loads(row[2]),
                            'confidence': row[3],
                            'user_specific': True
                        })
                
                # Get global insights
                cursor = conn.execute("""
                    SELECT insight_type, insight_data, confidence, impact_score
                    FROM global_insights
                    WHERE confidence > 0.7
                    ORDER BY impact_score DESC
                    LIMIT 5
                """)
                
                for row in cursor.fetchall():
                    recommendations.append({
                        'type': 'system',
                        'insight_type': row[0],
                        'data': json.loads(row[1]),
                        'confidence': row[2],
                        'impact': row[3],
                        'user_specific': False
                    })
        
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
        
        return recommendations
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """
        Get current status of all optimization domains
        """
        status = {
            'engine_status': 'active',
            'domains': {},
            'total_optimizations': 0,
            'avg_improvement': 0.0,
            'last_optimization': None
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get total optimizations
                cursor = conn.execute("SELECT COUNT(*) FROM optimization_cycles")
                status['total_optimizations'] = cursor.fetchone()[0]
                
                # Get average improvement
                cursor = conn.execute("SELECT AVG(improvement_achieved) FROM optimization_cycles")
                result = cursor.fetchone()[0]
                status['avg_improvement'] = result if result else 0.0
                
                # Get last optimization time
                cursor = conn.execute("""
                    SELECT cycle_timestamp FROM optimization_cycles
                    ORDER BY cycle_timestamp DESC LIMIT 1
                """)
                result = cursor.fetchone()
                if result:
                    status['last_optimization'] = result[0]
                
                # Get domain-specific status
                for domain in OptimizationDomain:
                    cursor = conn.execute("""
                        SELECT COUNT(*), AVG(improvement_achieved), MAX(cycle_timestamp)
                        FROM optimization_cycles WHERE domain = ?
                    """, (domain.value,))
                    
                    result = cursor.fetchone()
                    status['domains'][domain.value] = {
                        'optimizations_count': result[0] if result[0] else 0,
                        'avg_improvement': result[1] if result[1] else 0.0,
                        'last_optimization': result[2] if result[2] else None,
                        'current_parameters': self.domain_parameters.get(domain, {})
                    }
        
        except Exception as e:
            logger.error(f"Error getting optimization status: {e}")
            status['engine_status'] = 'error'
        
        return status
    
    # Helper methods for specific optimization logic
    def _analyze_therapeutic_effectiveness(self, user_id: str, interactions: List[Dict]) -> Dict[str, float]:
        """Analyze current therapeutic intervention effectiveness"""
        if not interactions:
            return {'overall_effectiveness': 0.5}
        
        # Calculate effectiveness based on user feedback and mood improvements
        effectiveness_scores = []
        for interaction in interactions:
            if 'effectiveness_rating' in interaction:
                effectiveness_scores.append(interaction['effectiveness_rating'] / 10.0)
        
        return {
            'overall_effectiveness': np.mean(effectiveness_scores) if effectiveness_scores else 0.5,
            'intervention_count': len(interactions),
            'positive_outcomes': len([s for s in effectiveness_scores if s > 0.6])
        }
    
    def _find_therapeutic_patterns(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Find patterns in therapeutic intervention effectiveness"""
        patterns = {}
        
        # Analyze timing patterns
        time_effectiveness = {}
        for interaction in interactions:
            if 'timestamp' in interaction and 'effectiveness_rating' in interaction:
                hour = datetime.fromisoformat(interaction['timestamp']).hour
                if hour not in time_effectiveness:
                    time_effectiveness[hour] = []
                time_effectiveness[hour].append(interaction['effectiveness_rating'])
        
        # Find best times
        best_times = []
        for hour, ratings in time_effectiveness.items():
            avg_rating = np.mean(ratings)
            if avg_rating > 7:  # Good effectiveness
                best_times.append(hour)
        
        patterns['optimal_times'] = best_times
        patterns['time_effectiveness'] = time_effectiveness
        
        return patterns
    
    def _optimize_therapeutic_parameters(self, current_params: Dict, patterns: Dict, metrics: Dict) -> Dict:
        """Optimize therapeutic parameters based on patterns"""
        new_params = current_params.copy()
        
        # Adjust timing threshold based on patterns
        if patterns.get('optimal_times'):
            # If we found optimal times, be more aggressive with timing
            new_params['intervention_timing_threshold'] = min(0.9, 
                current_params['intervention_timing_threshold'] * 1.1)
        
        # Adjust confidence based on overall effectiveness
        effectiveness = metrics.get('overall_effectiveness', 0.5)
        if effectiveness > 0.7:
            new_params['skill_recommendation_confidence'] = min(0.95,
                current_params['skill_recommendation_confidence'] * 1.05)
        elif effectiveness < 0.4:
            new_params['skill_recommendation_confidence'] = max(0.5,
                current_params['skill_recommendation_confidence'] * 0.95)
        
        return new_params
    
    def _calculate_therapeutic_improvement(self, metrics: Dict, patterns: Dict) -> float:
        """Calculate expected improvement from therapeutic optimization"""
        base_improvement = 0.0
        
        # Improvement based on pattern recognition
        if patterns.get('optimal_times'):
            base_improvement += 0.1  # 10% improvement from timing optimization
        
        # Improvement based on current effectiveness
        effectiveness = metrics.get('overall_effectiveness', 0.5)
        if effectiveness < 0.6:
            base_improvement += 0.15  # More room for improvement
        
        return min(0.3, base_improvement)  # Cap at 30% improvement per cycle
    
    def _analyze_provider_effectiveness(self, usage_history: List[Dict]) -> Dict[str, Any]:
        """Analyze AI provider effectiveness patterns"""
        provider_stats = {}
        
        for usage in usage_history:
            provider = usage.get('provider', 'unknown')
            if provider not in provider_stats:
                provider_stats[provider] = {
                    'requests': 0,
                    'total_cost': 0.0,
                    'total_quality': 0.0,
                    'total_time': 0.0
                }
            
            stats = provider_stats[provider]
            stats['requests'] += 1
            stats['total_cost'] += usage.get('cost', 0.0)
            stats['total_quality'] += usage.get('quality_score', 0.5)
            stats['total_time'] += usage.get('response_time', 1.0)
        
        # Calculate averages
        for provider, stats in provider_stats.items():
            if stats['requests'] > 0:
                stats['avg_cost'] = stats['total_cost'] / stats['requests']
                stats['avg_quality'] = stats['total_quality'] / stats['requests']
                stats['avg_time'] = stats['total_time'] / stats['requests']
                stats['cost_quality_ratio'] = stats['avg_cost'] / max(0.1, stats['avg_quality'])
        
        return provider_stats
    
    def _calculate_ai_quality_score(self, usage_history: List[Dict]) -> float:
        """Calculate overall AI service quality score"""
        if not usage_history:
            return 0.5
        
        quality_scores = [u.get('quality_score', 0.5) for u in usage_history]
        return np.mean(quality_scores)
    
    def _calculate_avg_response_time(self, usage_history: List[Dict]) -> float:
        """Calculate average AI response time"""
        if not usage_history:
            return 1.0
        
        times = [u.get('response_time', 1.0) for u in usage_history]
        return np.mean(times)
    
    def _optimize_ai_parameters(self, current_params: Dict, effectiveness: Dict, metrics: Dict) -> Dict:
        """Optimize AI service parameters"""
        new_params = current_params.copy()
        
        # Find most cost-effective provider
        best_provider = None
        best_ratio = float('inf')
        
        for provider, stats in effectiveness.items():
            if stats.get('cost_quality_ratio', float('inf')) < best_ratio:
                best_ratio = stats['cost_quality_ratio']
                best_provider = provider
        
        # Adjust cost vs quality threshold
        if best_ratio < 0.5:  # Good cost/quality ratio
            new_params['cost_vs_quality_threshold'] = min(0.9, 
                current_params['cost_vs_quality_threshold'] * 1.1)
        
        return new_params
    
    def _calculate_ai_improvement(self, metrics: Dict, effectiveness: Dict) -> float:
        """Calculate expected AI service improvement"""
        # Find potential cost savings
        cost_improvement = 0.0
        quality_improvement = 0.0
        
        if effectiveness:
            best_ratio = min(stats.get('cost_quality_ratio', 1.0) 
                           for stats in effectiveness.values())
            current_ratio = metrics.get('cost_per_request', 0.5) / max(0.1, metrics.get('quality_score', 0.5))
            
            if best_ratio < current_ratio:
                cost_improvement = (current_ratio - best_ratio) / current_ratio
        
        return min(0.4, cost_improvement)  # Cap at 40% improvement
    
    def _analyze_engagement_metrics(self, user_id: str, engagement_data: List[Dict]) -> Dict[str, float]:
        """Analyze user engagement metrics"""
        if not engagement_data:
            return {'engagement_score': 0.5}
        
        # Calculate various engagement metrics
        total_sessions = len(engagement_data)
        avg_session_length = np.mean([e.get('duration', 0) for e in engagement_data])
        feature_usage_variety = len(set(e.get('feature', '') for e in engagement_data))
        
        # Normalize to 0-1 scale
        engagement_score = min(1.0, (
            (total_sessions / 30) * 0.3 +  # Session frequency
            (avg_session_length / 300) * 0.3 +  # Session length (5 min baseline)
            (feature_usage_variety / 10) * 0.4  # Feature variety
        ))
        
        return {
            'engagement_score': engagement_score,
            'total_sessions': total_sessions,
            'avg_session_length': avg_session_length,
            'feature_variety': feature_usage_variety
        }
    
    def _find_engagement_patterns(self, engagement_data: List[Dict]) -> Dict[str, Any]:
        """Find user engagement patterns"""
        patterns = {}
        
        # Time-based patterns
        time_engagement = {}
        for session in engagement_data:
            if 'timestamp' in session:
                hour = datetime.fromisoformat(session['timestamp']).hour
                if hour not in time_engagement:
                    time_engagement[hour] = []
                time_engagement[hour].append(session.get('duration', 0))
        
        # Find peak engagement times
        peak_times = []
        for hour, durations in time_engagement.items():
            avg_duration = np.mean(durations)
            if avg_duration > 180:  # > 3 minutes
                peak_times.append(hour)
        
        patterns['peak_times'] = peak_times
        patterns['time_engagement'] = time_engagement
        
        return patterns
    
    def _optimize_engagement_parameters(self, current_params: Dict, patterns: Dict, metrics: Dict) -> Dict:
        """Optimize engagement parameters"""
        new_params = current_params.copy()
        
        # Adjust notification frequency based on engagement
        engagement_score = metrics.get('engagement_score', 0.5)
        if engagement_score > 0.7:
            # High engagement - can increase frequency slightly
            new_params['notification_frequency'] = min(0.8,
                current_params['notification_frequency'] * 1.05)
        elif engagement_score < 0.3:
            # Low engagement - reduce frequency
            new_params['notification_frequency'] = max(0.2,
                current_params['notification_frequency'] * 0.95)
        
        return new_params
    
    def _calculate_engagement_improvement(self, metrics: Dict, patterns: Dict) -> float:
        """Calculate expected engagement improvement"""
        base_improvement = 0.0
        
        # Improvement from timing optimization
        if patterns.get('peak_times'):
            base_improvement += 0.1
        
        # Improvement potential based on current engagement
        engagement_score = metrics.get('engagement_score', 0.5)
        if engagement_score < 0.5:
            base_improvement += 0.2  # More room for improvement
        
        return min(0.25, base_improvement)
    
    def _store_optimization_cycle(self, domain: OptimizationDomain, user_id: str, 
                                 metrics: Dict, improvement: float, parameters: Dict):
        """Store optimization cycle results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO optimization_cycles 
                    (domain, user_id, metrics_before, metrics_after, parameters_adjusted, 
                     improvement_achieved, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    domain.value,
                    user_id,
                    json.dumps(metrics),
                    json.dumps({}),  # Placeholder for metrics after
                    json.dumps(parameters),
                    improvement,
                    0.8  # Default confidence
                ))
        except Exception as e:
            logger.error(f"Error storing optimization cycle: {e}")
    
    def _generate_global_insights(self, optimization_results: Dict[str, OptimizationResult]):
        """Generate and store global optimization insights"""
        try:
            insights = []
            
            # Analyze overall optimization trends
            total_improvement = sum(result.improvement_percentage 
                                  for result in optimization_results.values())
            
            if total_improvement > 20:  # Significant improvement
                insights.append({
                    'type': 'system_improvement',
                    'data': {
                        'total_improvement': total_improvement,
                        'domains_improved': len([r for r in optimization_results.values() 
                                               if r.metric_improved]),
                        'recommendations': [
                            'Continue current optimization strategy',
                            'Consider expanding optimization to more domains'
                        ]
                    },
                    'confidence': 0.8,
                    'impact': total_improvement / 100
                })
            
            # Store insights
            with sqlite3.connect(self.db_path) as conn:
                for insight in insights:
                    conn.execute("""
                        INSERT INTO global_insights 
                        (insight_type, insight_data, confidence, impact_score)
                        VALUES (?, ?, ?, ?)
                    """, (
                        insight['type'],
                        json.dumps(insight['data']),
                        insight['confidence'],
                        insight['impact']
                    ))
        
        except Exception as e:
            logger.error(f"Error generating global insights: {e}")
    
    # Data retrieval methods (would connect to actual NOUS database in production)
    def _get_user_therapeutic_data(self, user_id: str) -> List[Dict]:
        """Get user's recent therapeutic interaction data"""
        # Placeholder - would query actual CBT/DBT/AA logs
        return []
    
    def _get_user_engagement_data(self, user_id: str) -> List[Dict]:
        """Get user's recent engagement data"""
        # Placeholder - would query actual user activity logs
        return []
    
    def _get_ai_usage_data(self) -> List[Dict]:
        """Get recent AI service usage data"""
        # Placeholder - would query actual AI usage logs
        return []


# Global instance
_seed_engine = None

def get_seed_engine() -> NOUSSeedEngine:
    """Get or create global SEED engine instance"""
    global _seed_engine
    if _seed_engine is None:
        _seed_engine = NOUSSeedEngine()
    return _seed_engine