"""
Predictive Analytics Engine
Leverages existing analytics system + unified AI service + user behavior data
to predict user needs and suggest actions before requested
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from collections import defaultdict, Counter

from utils.unified_ai_service import UnifiedAIService
from utils.analytics_service import AnalyticsService
from config.app_config import AppConfig

logger = logging.getLogger(__name__)

class PredictiveAnalyticsEngine:
    """Advanced predictive analytics using existing user behavior data"""
    
    def __init__(self):
        """Initialize predictive analytics engine"""
        self.ai_service = UnifiedAIService()
        self.analytics_service = AnalyticsService()
        self.db_path = Path("instance/analytics_predictions.db")
        self.init_database()
        logger.info("Predictive Analytics Engine initialized")
    
    def init_database(self):
        """Initialize predictions database"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    prediction_type TEXT NOT NULL,
                    prediction_data TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prediction_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prediction_id INTEGER,
                    user_id TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    feedback_value REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (prediction_id) REFERENCES predictions (id)
                )
            """)
    
    def analyze_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user behavior patterns from existing analytics data"""
        try:
            # Get user activity data from analytics service
            user_activities = self.analytics_service.get_user_activities(user_id)
            
            patterns = {
                'time_patterns': self._analyze_time_patterns(user_activities),
                'feature_usage': self._analyze_feature_usage(user_activities),
                'task_patterns': self._analyze_task_patterns(user_id),
                'routine_detection': self._detect_routines(user_activities),
                'preference_patterns': self._analyze_preferences(user_id)
            }
            
            # Store patterns in database
            self._store_patterns(user_id, patterns)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing user patterns: {e}")
            return {}
    
    def _analyze_time_patterns(self, activities: List[Dict]) -> Dict[str, Any]:
        """Analyze when user is most active"""
        if not activities:
            return {}
            
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)
        
        for activity in activities:
            if 'timestamp' in activity:
                dt = datetime.fromisoformat(activity['timestamp'])
                hourly_activity[dt.hour] += 1
                daily_activity[dt.weekday()] += 1
        
        # Find peak hours and days
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 9
        peak_day = max(daily_activity.items(), key=lambda x: x[1])[0] if daily_activity else 0
        
        return {
            'peak_hour': peak_hour,
            'peak_day': peak_day,
            'hourly_distribution': dict(hourly_activity),
            'daily_distribution': dict(daily_activity)
        }
    
    def _analyze_feature_usage(self, activities: List[Dict]) -> Dict[str, Any]:
        """Analyze which features user uses most"""
        feature_usage = Counter()
        feature_sequences = []
        
        for activity in activities:
            if 'feature' in activity:
                feature_usage[activity['feature']] += 1
                feature_sequences.append(activity['feature'])
        
        # Find common feature sequences
        sequences = []
        for i in range(len(feature_sequences) - 1):
            sequences.append((feature_sequences[i], feature_sequences[i + 1]))
        
        common_sequences = Counter(sequences).most_common(5)
        
        return {
            'most_used_features': feature_usage.most_common(10),
            'common_sequences': common_sequences,
            'total_features_used': len(feature_usage)
        }
    
    def _analyze_task_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze task creation and completion patterns"""
        try:
            # This would integrate with your task management system
            # For now, we'll create a placeholder pattern
            return {
                'avg_tasks_per_day': 5,
                'completion_rate': 0.78,
                'preferred_task_types': ['personal', 'work', 'health'],
                'peak_task_creation_time': 9  # 9 AM
            }
        except Exception as e:
            logger.error(f"Error analyzing task patterns: {e}")
            return {}
    
    def _detect_routines(self, activities: List[Dict]) -> List[Dict[str, Any]]:
        """Detect recurring behavior patterns"""
        routines = []
        
        # Group activities by day of week and hour
        daily_patterns = defaultdict(lambda: defaultdict(list))
        
        for activity in activities:
            if 'timestamp' in activity and 'feature' in activity:
                dt = datetime.fromisoformat(activity['timestamp'])
                day_hour = f"{dt.weekday()}_{dt.hour}"
                daily_patterns[day_hour]['features'].append(activity['feature'])
        
        # Find recurring patterns
        for day_hour, data in daily_patterns.items():
            if len(data['features']) >= 3:  # At least 3 occurrences
                most_common = Counter(data['features']).most_common(1)
                if most_common:
                    feature, count = most_common[0]
                    confidence = count / len(data['features'])
                    if confidence >= 0.5:  # 50% confidence threshold
                        day, hour = day_hour.split('_')
                        routines.append({
                            'day_of_week': int(day),
                            'hour': int(hour),
                            'feature': feature,
                            'confidence': confidence
                        })
        
        return routines
    
    def _analyze_preferences(self, user_id: str) -> Dict[str, Any]:
        """Analyze user preferences from existing data"""
        # This would integrate with your settings and user preferences
        return {
            'notification_preferences': 'moderate',
            'interface_theme': 'auto',
            'preferred_ai_provider': 'openrouter',
            'voice_enabled': True
        }
    
    def _store_patterns(self, user_id: str, patterns: Dict[str, Any]):
        """Store analyzed patterns in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for pattern_type, pattern_data in patterns.items():
                    conn.execute("""
                        INSERT OR REPLACE INTO user_patterns 
                        (user_id, pattern_type, pattern_data, confidence)
                        VALUES (?, ?, ?, ?)
                    """, (user_id, pattern_type, json.dumps(pattern_data), 0.8))
        except Exception as e:
            logger.error(f"Error storing patterns: {e}")
    
    def generate_predictions(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate predictions based on analyzed patterns"""
        try:
            patterns = self.analyze_user_patterns(user_id)
            predictions = []
            
            # Time-based predictions
            if 'time_patterns' in patterns:
                time_pred = self._predict_next_activity_time(patterns['time_patterns'])
                if time_pred:
                    predictions.append(time_pred)
            
            # Feature usage predictions
            if 'feature_usage' in patterns:
                feature_pred = self._predict_next_feature(patterns['feature_usage'])
                if feature_pred:
                    predictions.append(feature_pred)
            
            # Task predictions
            if 'task_patterns' in patterns:
                task_pred = self._predict_task_needs(patterns['task_patterns'])
                if task_pred:
                    predictions.append(task_pred)
            
            # Routine predictions
            if 'routine_detection' in patterns:
                routine_preds = self._predict_routine_triggers(patterns['routine_detection'])
                predictions.extend(routine_preds)
            
            # Store predictions
            self._store_predictions(user_id, predictions)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return []
    
    def _predict_next_activity_time(self, time_patterns: Dict) -> Optional[Dict[str, Any]]:
        """Predict when user will be active next"""
        if not time_patterns or 'peak_hour' not in time_patterns:
            return None
            
        now = datetime.now()
        peak_hour = time_patterns['peak_hour']
        
        # Predict next peak activity time
        next_peak = now.replace(hour=peak_hour, minute=0, second=0, microsecond=0)
        if next_peak <= now:
            next_peak += timedelta(days=1)
        
        return {
            'type': 'activity_time',
            'prediction': f"You'll likely be most productive at {peak_hour}:00",
            'suggested_action': f"Consider scheduling important tasks around {peak_hour}:00",
            'confidence': 0.75,
            'expires_at': next_peak.isoformat()
        }
    
    def _predict_next_feature(self, feature_usage: Dict) -> Optional[Dict[str, Any]]:
        """Predict which feature user will use next"""
        if not feature_usage or 'most_used_features' not in feature_usage:
            return None
            
        most_used = feature_usage['most_used_features']
        if not most_used:
            return None
            
        top_feature, usage_count = most_used[0]
        
        return {
            'type': 'feature_usage',
            'prediction': f"You'll likely use {top_feature} soon",
            'suggested_action': f"Quick access to {top_feature} is ready",
            'confidence': min(0.9, usage_count / 100),
            'expires_at': (datetime.now() + timedelta(hours=2)).isoformat()
        }
    
    def _predict_task_needs(self, task_patterns: Dict) -> Optional[Dict[str, Any]]:
        """Predict task management needs"""
        if not task_patterns:
            return None
            
        avg_tasks = task_patterns.get('avg_tasks_per_day', 5)
        completion_rate = task_patterns.get('completion_rate', 0.8)
        
        if completion_rate < 0.7:
            return {
                'type': 'task_management',
                'prediction': "You might need help managing your task load",
                'suggested_action': "Consider breaking down large tasks or adjusting priorities",
                'confidence': 0.8,
                'expires_at': (datetime.now() + timedelta(days=1)).isoformat()
            }
        
        return None
    
    def _predict_routine_triggers(self, routines: List[Dict]) -> List[Dict[str, Any]]:
        """Predict routine-based actions"""
        predictions = []
        now = datetime.now()
        
        for routine in routines:
            # Check if we're approaching a routine time
            routine_day = routine['day_of_week']
            routine_hour = routine['hour']
            
            # If it's the right day and within 1 hour of routine time
            if (now.weekday() == routine_day and 
                abs(now.hour - routine_hour) <= 1):
                
                predictions.append({
                    'type': 'routine_trigger',
                    'prediction': f"Time for your usual {routine['feature']} activity",
                    'suggested_action': f"Ready to use {routine['feature']}?",
                    'confidence': routine['confidence'],
                    'expires_at': (now + timedelta(hours=2)).isoformat()
                })
        
        return predictions
    
    def _store_predictions(self, user_id: str, predictions: List[Dict]):
        """Store predictions in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for pred in predictions:
                    conn.execute("""
                        INSERT INTO predictions 
                        (user_id, prediction_type, prediction_data, confidence, expires_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        user_id, 
                        pred['type'], 
                        json.dumps(pred), 
                        pred['confidence'],
                        pred.get('expires_at')
                    ))
        except Exception as e:
            logger.error(f"Error storing predictions: {e}")
    
    def get_active_predictions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get current active predictions for user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT prediction_data, confidence 
                    FROM predictions 
                    WHERE user_id = ? 
                    AND used = FALSE 
                    AND (expires_at IS NULL OR expires_at > datetime('now'))
                    ORDER BY confidence DESC
                    LIMIT 10
                """, (user_id,))
                
                predictions = []
                for row in cursor.fetchall():
                    pred_data = json.loads(row[0])
                    pred_data['confidence'] = row[1]
                    predictions.append(pred_data)
                
                return predictions
                
        except Exception as e:
            logger.error(f"Error getting active predictions: {e}")
            return []
    
    def record_prediction_feedback(self, user_id: str, prediction_id: int, 
                                  feedback_type: str, feedback_value: float):
        """Record user feedback on predictions for learning"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO prediction_feedback 
                    (prediction_id, user_id, feedback_type, feedback_value)
                    VALUES (?, ?, ?, ?)
                """, (prediction_id, user_id, feedback_type, feedback_value))
                
                # Mark prediction as used
                conn.execute("""
                    UPDATE predictions SET used = TRUE WHERE id = ?
                """, (prediction_id,))
                
        except Exception as e:
            logger.error(f"Error recording prediction feedback: {e}")
    
    def get_prediction_accuracy(self, user_id: str) -> Dict[str, float]:
        """Calculate prediction accuracy metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        p.prediction_type,
                        AVG(pf.feedback_value) as avg_feedback,
                        COUNT(pf.id) as feedback_count
                    FROM predictions p
                    JOIN prediction_feedback pf ON p.id = pf.prediction_id
                    WHERE p.user_id = ?
                    GROUP BY p.prediction_type
                """, (user_id,))
                
                accuracy = {}
                for row in cursor.fetchall():
                    pred_type, avg_feedback, count = row
                    accuracy[pred_type] = {
                        'accuracy': avg_feedback,
                        'sample_size': count
                    }
                
                return accuracy
                
        except Exception as e:
            logger.error(f"Error calculating prediction accuracy: {e}")
            return {}

# Global instance
predictive_engine = PredictiveAnalyticsEngine()