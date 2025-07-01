"""
SEED Integration Layer for NOUS Platform
Connects SEED optimization engine to existing NOUS features and database models

This layer provides seamless integration between SEED learning and:
- Health models (CBT, DBT, AA)
- Analytics models (UserActivity, UserMetrics, UserInsight)
- AI services (UnifiedAIService, EnhancedAISystem)
- Financial models (for cost optimization)
- User engagement tracking
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import and_, desc
from database import db

# Import NOUS models
from models.health_models import (
    CBTMoodLog, CBTThoughtRecord, CBTBehaviorExperiment, CBTCopingSkill, CBTSkillUsage,
    DBTSkillLog, DBTSkillRecommendation, DBTCrisisResource
)
from models.analytics_models import UserActivity, UserMetrics, UserInsight
from models.user import User

# Import SEED engine
from services.seed_optimization_engine import get_seed_engine, OptimizationDomain

logger = logging.getLogger(__name__)

class SeedIntegrationLayer:
    """
    Integration layer connecting SEED optimization to NOUS database and services
    """
    
    def __init__(self):
        """Initialize integration layer with SEED engine"""
        self.seed_engine = get_seed_engine()
        logger.info("SEED Integration Layer initialized")
    
    def optimize_user_therapeutic_experience(self, user_id: str) -> Dict[str, Any]:
        """
        Optimize therapeutic experience for specific user based on their data
        Analyzes CBT, DBT, and AA engagement patterns
        """
        try:
            # Gather user's therapeutic interaction data
            therapeutic_data = self._gather_user_therapeutic_data(user_id)
            
            if not therapeutic_data:
                return {
                    'success': False,
                    'message': 'Insufficient therapeutic data for optimization',
                    'recommendations': []
                }
            
            # Run SEED optimization
            optimization_result = self.seed_engine.optimize_therapeutic_interventions(
                user_id, therapeutic_data
            )
            
            # Generate actionable recommendations
            recommendations = self._generate_therapeutic_recommendations(
                user_id, optimization_result, therapeutic_data
            )
            
            # Update user insights with optimization results
            self._store_therapeutic_insights(user_id, optimization_result, recommendations)
            
            return {
                'success': True,
                'optimization_result': optimization_result,
                'recommendations': recommendations,
                'improvement_potential': f"{optimization_result.improvement_percentage:.1f}%"
            }
            
        except Exception as e:
            logger.error(f"Therapeutic optimization error for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': []
            }
    
    def optimize_ai_cost_efficiency(self) -> Dict[str, Any]:
        """
        Optimize AI service costs across the platform
        Analyzes usage patterns and cost effectiveness
        """
        try:
            # Gather AI usage data from user activities
            ai_usage_data = self._gather_ai_usage_data()
            
            # Run SEED optimization for AI services
            optimization_result = self.seed_engine.optimize_ai_service_selection(ai_usage_data)
            
            # Calculate potential cost savings
            cost_analysis = self._calculate_cost_savings(optimization_result, ai_usage_data)
            
            # Generate system-wide recommendations
            recommendations = self._generate_ai_optimization_recommendations(
                optimization_result, cost_analysis
            )
            
            return {
                'success': True,
                'optimization_result': optimization_result,
                'cost_analysis': cost_analysis,
                'recommendations': recommendations,
                'estimated_monthly_savings': cost_analysis.get('monthly_savings', 0)
            }
            
        except Exception as e:
            logger.error(f"AI cost optimization error: {e}")
            return {
                'success': False,
                'error': str(e),
                'estimated_monthly_savings': 0
            }
    
    def optimize_user_engagement(self, user_id: str) -> Dict[str, Any]:
        """
        Optimize user engagement patterns and feature discovery
        """
        try:
            # Gather user engagement data
            engagement_data = self._gather_user_engagement_data(user_id)
            
            # Run SEED optimization
            optimization_result = self.seed_engine.optimize_user_engagement(
                user_id, engagement_data
            )
            
            # Generate engagement recommendations
            recommendations = self._generate_engagement_recommendations(
                user_id, optimization_result, engagement_data
            )
            
            # Update user metrics and insights
            self._update_engagement_insights(user_id, optimization_result, recommendations)
            
            return {
                'success': True,
                'optimization_result': optimization_result,
                'recommendations': recommendations,
                'current_engagement_score': optimization_result.old_value,
                'projected_engagement_score': optimization_result.new_value
            }
            
        except Exception as e:
            logger.error(f"Engagement optimization error for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': []
            }
    
    def run_comprehensive_user_optimization(self, user_id: str) -> Dict[str, Any]:
        """
        Run comprehensive SEED optimization for a specific user across all domains
        """
        try:
            results = {}
            
            # Run therapeutic optimization
            results['therapeutic'] = self.optimize_user_therapeutic_experience(user_id)
            
            # Run engagement optimization
            results['engagement'] = self.optimize_user_engagement(user_id)
            
            # Get personalized recommendations
            recommendations = self.seed_engine.get_optimization_recommendations(user_id)
            
            # Calculate overall improvement potential
            total_improvement = self._calculate_total_improvement(results)
            
            return {
                'success': True,
                'user_id': user_id,
                'optimization_results': results,
                'personalized_recommendations': recommendations,
                'total_improvement_potential': total_improvement,
                'optimization_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Comprehensive optimization error for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'user_id': user_id
            }
    
    def run_system_wide_optimization(self) -> Dict[str, Any]:
        """
        Run system-wide SEED optimization across all users and services
        """
        try:
            results = {}
            
            # Run AI cost optimization
            results['ai_cost_optimization'] = self.optimize_ai_cost_efficiency()
            
            # Get active users for engagement analysis
            active_users = self._get_active_users()
            
            # Run optimization for top users (sample for system insights)
            user_optimizations = []
            for user_id in active_users[:10]:  # Sample top 10 active users
                user_result = self.optimize_user_engagement(user_id)
                if user_result['success']:
                    user_optimizations.append(user_result)
            
            results['user_engagement_sample'] = user_optimizations
            
            # Get system-wide recommendations
            system_recommendations = self.seed_engine.get_optimization_recommendations()
            
            # Calculate system-wide metrics
            system_metrics = self._calculate_system_metrics(results)
            
            return {
                'success': True,
                'optimization_results': results,
                'system_recommendations': system_recommendations,
                'system_metrics': system_metrics,
                'optimization_timestamp': datetime.utcnow().isoformat(),
                'users_analyzed': len(user_optimizations)
            }
            
        except Exception as e:
            logger.error(f"System-wide optimization error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_optimization_dashboard_data(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get optimization data for dashboard display
        """
        try:
            # Get SEED engine status
            engine_status = self.seed_engine.get_optimization_status()
            
            # Get user-specific data if user_id provided
            user_data = {}
            if user_id:
                user_data = self._get_user_optimization_summary(user_id)
            
            # Get recent insights
            recent_insights = self._get_recent_optimization_insights()
            
            # Get cost savings summary
            cost_summary = self._get_cost_optimization_summary()
            
            return {
                'engine_status': engine_status,
                'user_data': user_data,
                'recent_insights': recent_insights,
                'cost_summary': cost_summary,
                'dashboard_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dashboard data error: {e}")
            return {
                'error': str(e),
                'dashboard_timestamp': datetime.utcnow().isoformat()
            }
    
    # Data gathering methods
    def _gather_user_therapeutic_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Gather user's therapeutic interaction data from CBT, DBT, AA models"""
        therapeutic_data = []
        
        try:
            # Get recent CBT mood logs
            cbt_moods = db.session.query(CBTMoodLog)\
                .filter(CBTMoodLog.user_id == user_id)\
                .filter(CBTMoodLog.created_at >= datetime.utcnow() - timedelta(days=30))\
                .order_by(desc(CBTMoodLog.created_at))\
                .limit(50)\
                .all()
            
            for mood in cbt_moods:
                therapeutic_data.append({
                    'type': 'cbt_mood',
                    'timestamp': mood.created_at.isoformat(),
                    'emotion_intensity': mood.emotion_intensity,
                    'effectiveness_rating': mood.effectiveness_rating,
                    'coping_strategy': mood.coping_strategy_used,
                    'triggers': mood.triggers
                })
            
            # Get CBT skill usage
            cbt_skills = db.session.query(CBTSkillUsage)\
                .filter(CBTSkillUsage.user_id == user_id)\
                .filter(CBTSkillUsage.created_at >= datetime.utcnow() - timedelta(days=30))\
                .order_by(desc(CBTSkillUsage.created_at))\
                .limit(30)\
                .all()
            
            for skill in cbt_skills:
                therapeutic_data.append({
                    'type': 'cbt_skill',
                    'timestamp': skill.created_at.isoformat(),
                    'skill_name': skill.skill_name,
                    'effectiveness_rating': skill.effectiveness_rating,
                    'situation': skill.situation_type
                })
            
            # Get DBT skill logs
            dbt_skills = db.session.query(DBTSkillLog)\
                .filter(DBTSkillLog.user_id == user_id)\
                .filter(DBTSkillLog.timestamp >= datetime.utcnow() - timedelta(days=30))\
                .order_by(desc(DBTSkillLog.timestamp))\
                .limit(30)\
                .all()
            
            for skill in dbt_skills:
                therapeutic_data.append({
                    'type': 'dbt_skill',
                    'timestamp': skill.timestamp.isoformat(),
                    'skill_name': skill.skill_name,
                    'effectiveness_rating': skill.effectiveness,
                    'category': skill.category,
                    'situation': skill.situation
                })
            
        except Exception as e:
            logger.error(f"Error gathering therapeutic data for user {user_id}: {e}")
        
        return therapeutic_data
    
    def _gather_ai_usage_data(self) -> List[Dict[str, Any]]:
        """Gather AI usage data from user activities"""
        ai_usage_data = []
        
        try:
            # Get AI-related activities from the last 30 days
            ai_activities = db.session.query(UserActivity)\
                .filter(UserActivity.activity_type.in_(['chat', 'ai_request', 'voice_interaction']))\
                .filter(UserActivity.timestamp >= datetime.utcnow() - timedelta(days=30))\
                .order_by(desc(UserActivity.timestamp))\
                .limit(500)\
                .all()
            
            for activity in ai_activities:
                activity_data = activity.activity_data or {}
                ai_usage_data.append({
                    'timestamp': activity.timestamp.isoformat(),
                    'activity_type': activity.activity_type,
                    'duration': activity.duration_seconds,
                    'provider': activity_data.get('ai_provider', 'unknown'),
                    'cost': activity_data.get('cost', 0.0),
                    'quality_score': activity_data.get('quality_rating', 0.5),
                    'response_time': activity_data.get('response_time', 1.0),
                    'user_satisfaction': activity_data.get('user_rating', 0.5)
                })
            
        except Exception as e:
            logger.error(f"Error gathering AI usage data: {e}")
        
        return ai_usage_data
    
    def _gather_user_engagement_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Gather user engagement data from activities and metrics"""
        engagement_data = []
        
        try:
            # Get user activities from the last 30 days
            activities = db.session.query(UserActivity)\
                .filter(UserActivity.user_id == user_id)\
                .filter(UserActivity.timestamp >= datetime.utcnow() - timedelta(days=30))\
                .order_by(desc(UserActivity.timestamp))\
                .limit(200)\
                .all()
            
            for activity in activities:
                engagement_data.append({
                    'timestamp': activity.timestamp.isoformat(),
                    'activity_type': activity.activity_type,
                    'category': activity.activity_category,
                    'duration': activity.duration_seconds,
                    'feature': activity.activity_type,
                    'session_id': activity.session_id
                })
            
        except Exception as e:
            logger.error(f"Error gathering engagement data for user {user_id}: {e}")
        
        return engagement_data
    
    def _generate_therapeutic_recommendations(self, user_id: str, optimization_result, 
                                           therapeutic_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate actionable therapeutic recommendations based on optimization"""
        recommendations = []
        
        try:
            # Analyze patterns in therapeutic data
            if optimization_result.metric_improved:
                # Find most effective interventions
                effective_interventions = [
                    d for d in therapeutic_data 
                    if d.get('effectiveness_rating', 0) > 7
                ]
                
                if effective_interventions:
                    most_effective = max(effective_interventions, 
                                       key=lambda x: x.get('effectiveness_rating', 0))
                    
                    recommendations.append({
                        'type': 'skill_recommendation',
                        'priority': 'high',
                        'title': 'Continue Using Effective Techniques',
                        'description': f"Your {most_effective.get('type', 'therapeutic')} approach "
                                     f"with {most_effective.get('skill_name', 'this technique')} "
                                     f"has been highly effective.",
                        'action': f"Use {most_effective.get('skill_name', 'this technique')} "
                                f"when experiencing {most_effective.get('situation', 'stress')}",
                        'confidence': optimization_result.confidence
                    })
                
                # Recommend optimal timing
                time_patterns = self._analyze_timing_patterns(therapeutic_data)
                if time_patterns:
                    recommendations.append({
                        'type': 'timing_optimization',
                        'priority': 'medium',
                        'title': 'Optimize Intervention Timing',
                        'description': f"Your therapeutic interventions are most effective "
                                     f"during certain times.",
                        'action': f"Try using coping skills around {time_patterns['best_time']} "
                                f"for maximum effectiveness",
                        'confidence': 0.7
                    })
                
                # Suggest underutilized techniques
                underutilized = self._find_underutilized_techniques(user_id, therapeutic_data)
                if underutilized:
                    recommendations.append({
                        'type': 'exploration_suggestion',
                        'priority': 'low',
                        'title': 'Explore New Techniques',
                        'description': "Based on your preferences, these techniques might help:",
                        'action': f"Consider trying {', '.join(underutilized[:3])}",
                        'confidence': 0.6
                    })
        
        except Exception as e:
            logger.error(f"Error generating therapeutic recommendations: {e}")
        
        return recommendations
    
    def _generate_ai_optimization_recommendations(self, optimization_result, 
                                                cost_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate AI optimization recommendations"""
        recommendations = []
        
        if optimization_result.improvement_percentage > 5:
            recommendations.append({
                'type': 'cost_optimization',
                'priority': 'high',
                'title': 'AI Cost Optimization Available',
                'description': f"Potential {optimization_result.improvement_percentage:.1f}% "
                             f"cost reduction identified",
                'action': 'Implement optimized AI provider selection',
                'estimated_savings': cost_analysis.get('monthly_savings', 0)
            })
        
        return recommendations
    
    def _generate_engagement_recommendations(self, user_id: str, optimization_result,
                                          engagement_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate user engagement recommendations"""
        recommendations = []
        
        if optimization_result.improvement_percentage > 10:
            recommendations.append({
                'type': 'engagement_boost',
                'priority': 'medium',
                'title': 'Engagement Optimization Available',
                'description': f"Your engagement could improve by "
                             f"{optimization_result.improvement_percentage:.1f}%",
                'action': 'Follow personalized feature suggestions and timing recommendations'
            })
        
        return recommendations
    
    # Helper methods
    def _store_therapeutic_insights(self, user_id: str, optimization_result, 
                                  recommendations: List[Dict]):
        """Store therapeutic optimization insights in database"""
        try:
            insight = UserInsight(
                user_id=user_id,
                insight_type='therapeutic_optimization',
                title='Therapeutic Experience Optimization',
                description=f"SEED analysis suggests {optimization_result.improvement_percentage:.1f}% "
                          f"improvement in therapeutic effectiveness",
                insights_data={
                    'optimization_result': {
                        'improvement_percentage': optimization_result.improvement_percentage,
                        'confidence': optimization_result.confidence,
                        'domain': optimization_result.domain.value
                    },
                    'recommendations': recommendations
                },
                confidence_score=optimization_result.confidence,
                priority_level='high' if optimization_result.improvement_percentage > 20 else 'medium'
            )
            
            db.session.add(insight)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error storing therapeutic insights: {e}")
            db.session.rollback()
    
    def _update_engagement_insights(self, user_id: str, optimization_result, 
                                  recommendations: List[Dict]):
        """Update user engagement insights"""
        try:
            insight = UserInsight(
                user_id=user_id,
                insight_type='engagement_optimization',
                title='User Engagement Optimization',
                description=f"SEED analysis suggests {optimization_result.improvement_percentage:.1f}% "
                          f"improvement in platform engagement",
                insights_data={
                    'current_score': optimization_result.old_value,
                    'projected_score': optimization_result.new_value,
                    'recommendations': recommendations
                },
                confidence_score=optimization_result.confidence,
                priority_level='medium'
            )
            
            db.session.add(insight)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error storing engagement insights: {e}")
            db.session.rollback()
    
    def _calculate_cost_savings(self, optimization_result, ai_usage_data: List[Dict]) -> Dict[str, Any]:
        """Calculate potential cost savings from AI optimization"""
        try:
            current_monthly_cost = sum(usage.get('cost', 0) for usage in ai_usage_data)
            potential_savings = current_monthly_cost * (optimization_result.improvement_percentage / 100)
            
            return {
                'current_monthly_cost': current_monthly_cost,
                'potential_savings_percentage': optimization_result.improvement_percentage,
                'monthly_savings': potential_savings,
                'annual_savings': potential_savings * 12
            }
        except Exception as e:
            logger.error(f"Error calculating cost savings: {e}")
            return {'monthly_savings': 0, 'annual_savings': 0}
    
    def _get_active_users(self, days: int = 7) -> List[str]:
        """Get list of active user IDs"""
        try:
            active_users = db.session.query(UserActivity.user_id)\
                .filter(UserActivity.timestamp >= datetime.utcnow() - timedelta(days=days))\
                .distinct()\
                .limit(50)\
                .all()
            
            return [user[0] for user in active_users]
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    def _calculate_total_improvement(self, results: Dict[str, Any]) -> float:
        """Calculate total improvement potential across all optimization domains"""
        total_improvement = 0.0
        count = 0
        
        for domain_result in results.values():
            if domain_result.get('success') and 'optimization_result' in domain_result:
                opt_result = domain_result['optimization_result']
                if hasattr(opt_result, 'improvement_percentage'):
                    total_improvement += opt_result.improvement_percentage
                    count += 1
        
        return total_improvement / max(1, count)
    
    def _analyze_timing_patterns(self, therapeutic_data: List[Dict]) -> Dict[str, Any]:
        """Analyze timing patterns in therapeutic data"""
        time_effectiveness = {}
        
        for data in therapeutic_data:
            if 'timestamp' in data and 'effectiveness_rating' in data:
                try:
                    hour = datetime.fromisoformat(data['timestamp']).hour
                    if hour not in time_effectiveness:
                        time_effectiveness[hour] = []
                    time_effectiveness[hour].append(data['effectiveness_rating'])
                except ValueError:
                    continue
        
        # Find best time
        best_time = None
        best_score = 0
        
        for hour, ratings in time_effectiveness.items():
            avg_rating = sum(ratings) / len(ratings)
            if avg_rating > best_score:
                best_score = avg_rating
                best_time = f"{hour}:00"
        
        return {'best_time': best_time, 'score': best_score} if best_time else {}
    
    def _find_underutilized_techniques(self, user_id: str, therapeutic_data: List[Dict]) -> List[str]:
        """Find therapeutic techniques that user hasn't tried but might benefit from"""
        try:
            # Get all available CBT coping skills
            available_skills = db.session.query(CBTCopingSkill.skill_name)\
                .filter(CBTCopingSkill.user_id.is_(None))\
                .all()  # System skills
            
            # Get user's used skills
            used_skills = set(data.get('skill_name') for data in therapeutic_data 
                            if data.get('skill_name'))
            
            # Find underutilized skills
            all_skills = set(skill[0] for skill in available_skills)
            underutilized = list(all_skills - used_skills)
            
            return underutilized[:5]  # Return top 5
            
        except Exception as e:
            logger.error(f"Error finding underutilized techniques: {e}")
            return []
    
    def _get_user_optimization_summary(self, user_id: str) -> Dict[str, Any]:
        """Get optimization summary for specific user"""
        try:
            # Get recent insights for user
            recent_insights = db.session.query(UserInsight)\
                .filter(UserInsight.user_id == user_id)\
                .filter(UserInsight.insight_type.in_([
                    'therapeutic_optimization', 'engagement_optimization'
                ]))\
                .order_by(desc(UserInsight.created_at))\
                .limit(5)\
                .all()
            
            return {
                'recent_optimizations': len(recent_insights),
                'latest_insights': [insight.to_dict() for insight in recent_insights],
                'optimization_available': len(recent_insights) < 3  # Suggest optimization if few recent
            }
            
        except Exception as e:
            logger.error(f"Error getting user optimization summary: {e}")
            return {}
    
    def _get_recent_optimization_insights(self) -> List[Dict[str, Any]]:
        """Get recent optimization insights for dashboard"""
        try:
            recent_insights = db.session.query(UserInsight)\
                .filter(UserInsight.insight_type.in_([
                    'therapeutic_optimization', 'engagement_optimization'
                ]))\
                .order_by(desc(UserInsight.created_at))\
                .limit(10)\
                .all()
            
            return [insight.to_dict() for insight in recent_insights]
            
        except Exception as e:
            logger.error(f"Error getting recent insights: {e}")
            return []
    
    def _get_cost_optimization_summary(self) -> Dict[str, Any]:
        """Get cost optimization summary"""
        try:
            # This would integrate with your existing cost tracking
            return {
                'optimization_active': True,
                'estimated_monthly_savings': 0.0,
                'last_optimization': None
            }
            
        except Exception as e:
            logger.error(f"Error getting cost summary: {e}")
            return {}
    
    def _calculate_system_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate system-wide optimization metrics"""
        try:
            metrics = {
                'total_optimizations_run': len([r for r in results.values() if r.get('success')]),
                'average_improvement': 0.0,
                'cost_savings_potential': 0.0,
                'users_with_improvements': 0
            }
            
            # Calculate averages from results
            improvements = []
            cost_savings = 0.0
            
            for result in results.values():
                if result.get('success'):
                    if 'optimization_result' in result:
                        opt_result = result['optimization_result']
                        if hasattr(opt_result, 'improvement_percentage'):
                            improvements.append(opt_result.improvement_percentage)
                    
                    if 'estimated_monthly_savings' in result:
                        cost_savings += result['estimated_monthly_savings']
            
            if improvements:
                metrics['average_improvement'] = sum(improvements) / len(improvements)
                metrics['users_with_improvements'] = len(improvements)
            
            metrics['cost_savings_potential'] = cost_savings
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating system metrics: {e}")
            return {}


# Global instance
_integration_layer = None

def get_seed_integration() -> SeedIntegrationLayer:
    """Get or create global SEED integration layer instance"""
    global _integration_layer
    if _integration_layer is None:
        _integration_layer = SeedIntegrationLayer()
    return _integration_layer