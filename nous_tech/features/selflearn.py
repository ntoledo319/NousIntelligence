"""
NOUS Tech Self-Learning Module
Continuous learning system with user feedback integration and retraining capabilities
"""

import sqlite3
import datetime
import logging
from typing import Dict, Any, List, Optional, Tuple
import os
import json

logger = logging.getLogger(__name__)

def init_selflearn(app):
    """Initialize self-learning system with feedback database"""
    try:
        # Get database path from config
        db_path = app.config.get('SELFLEARN_DB', 'instance/selflearn.db')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        conn = sqlite3.connect(db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                user TEXT NOT NULL,
                input TEXT NOT NULL,
                response TEXT NOT NULL,
                rating INTEGER,
                feedback_type TEXT DEFAULT 'rating',
                metadata TEXT,
                processed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                insight_data TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                preference_type TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user, preference_type)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Store database path in app config
        app.config['SELFLEARN_DB'] = db_path
        
        logger.info(f"Self-learning system initialized with database: {db_path}")
        
    except Exception as e:
        logger.error(f"Failed to initialize self-learning system: {e}")
        # Set a fallback path
        app.config['SELFLEARN_DB'] = 'instance/selflearn.db'

def log_interaction(user: str, input_text: str, response: str, rating: Optional[int] = None, 
                   feedback_type: str = 'rating', metadata: Optional[Dict[str, Any]] = None):
    """Log user interaction for learning purposes"""
    try:
        from flask import current_app
        
        db_path = current_app.config.get('SELFLEARN_DB', 'instance/selflearn.db')
        conn = sqlite3.connect(db_path)
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        conn.execute('''
            INSERT INTO feedback (ts, user, input, response, rating, feedback_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.datetime.utcnow().isoformat(),
            user,
            input_text,
            response,
            rating,
            feedback_type,
            metadata_json
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Logged interaction for user {user} with rating {rating}")
        
        # Check if retraining is needed
        if rating is not None:
            retrain_if_needed()
            
    except Exception as e:
        logger.error(f"Failed to log interaction: {e}")

def log_detailed_feedback(user: str, input_text: str, response: str, 
                         feedback_data: Dict[str, Any]):
    """Log detailed feedback with structured data"""
    try:
        feedback_type = feedback_data.get('type', 'detailed')
        rating = feedback_data.get('rating')
        
        log_interaction(
            user=user,
            input_text=input_text,
            response=response,
            rating=rating,
            feedback_type=feedback_type,
            metadata=feedback_data
        )
        
    except Exception as e:
        logger.error(f"Failed to log detailed feedback: {e}")

def get_user_feedback_stats(user: str) -> Dict[str, Any]:
    """Get feedback statistics for a specific user"""
    try:
        from flask import current_app
        
        db_path = current_app.config.get('SELFLEARN_DB', 'instance/selflearn.db')
        conn = sqlite3.connect(db_path)
        
        # Get rating statistics
        cursor = conn.execute('''
            SELECT 
                COUNT(*) as total_interactions,
                AVG(rating) as avg_rating,
                MIN(rating) as min_rating,
                MAX(rating) as max_rating,
                COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_feedback,
                COUNT(CASE WHEN rating <= 2 THEN 1 END) as negative_feedback
            FROM feedback 
            WHERE user = ? AND rating IS NOT NULL
        ''', (user,))
        
        stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_interactions': stats[0] if stats else 0,
            'average_rating': round(stats[1], 2) if stats and stats[1] else 0,
            'min_rating': stats[2] if stats else 0,
            'max_rating': stats[3] if stats else 0,
            'positive_feedback': stats[4] if stats else 0,
            'negative_feedback': stats[5] if stats else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get user feedback stats: {e}")
        return {}

def get_learning_insights() -> List[Dict[str, Any]]:
    """Get current learning insights"""
    try:
        from flask import current_app
        
        db_path = current_app.config.get('SELFLEARN_DB', 'instance/selflearn.db')
        conn = sqlite3.connect(db_path)
        
        cursor = conn.execute('''
            SELECT insight_type, insight_data, confidence, created_at, applied
            FROM learning_insights
            ORDER BY created_at DESC
            LIMIT 10
        ''')
        
        insights = []
        for row in cursor.fetchall():
            insights.append({
                'type': row[0],
                'data': json.loads(row[1]) if row[1] else {},
                'confidence': row[2],
                'created_at': row[3],
                'applied': bool(row[4])
            })
        
        conn.close()
        
        return insights
        
    except Exception as e:
        logger.error(f"Failed to get learning insights: {e}")
        return []

def analyze_user_patterns(user: str) -> Dict[str, Any]:
    """Analyze user interaction patterns for personalization"""
    try:
        from flask import current_app
        
        db_path = current_app.config.get('SELFLEARN_DB', 'instance/selflearn.db')
        conn = sqlite3.connect(db_path)
        
        # Analyze interaction patterns
        cursor = conn.execute('''
            SELECT input, response, rating, ts
            FROM feedback
            WHERE user = ?
            ORDER BY ts DESC
            LIMIT 50
        ''', (user,))
        
        interactions = cursor.fetchall()
        
        if not interactions:
            return {'patterns': {}, 'preferences': {}}
        
        # Analyze patterns
        patterns = {
            'frequent_topics': analyze_frequent_topics([row[0] for row in interactions]),
            'preferred_response_style': analyze_response_style([row[1] for row in interactions]),
            'time_patterns': analyze_time_patterns([row[3] for row in interactions]),
            'satisfaction_trends': analyze_satisfaction_trends([(row[2], row[3]) for row in interactions if row[2]])
        }
        
        # Get stored preferences
        cursor = conn.execute('''
            SELECT preference_type, preference_value, confidence
            FROM user_preferences
            WHERE user = ?
        ''', (user,))
        
        preferences = {}
        for row in cursor.fetchall():
            preferences[row[0]] = {
                'value': row[1],
                'confidence': row[2]
            }
        
        conn.close()
        
        return {
            'patterns': patterns,
            'preferences': preferences
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze user patterns: {e}")
        return {'patterns': {}, 'preferences': {}}

def update_user_preference(user: str, preference_type: str, preference_value: str, confidence: float = 0.8):
    """Update user preference based on learning"""
    try:
        from flask import current_app
        
        db_path = current_app.config.get('SELFLEARN_DB', 'instance/selflearn.db')
        conn = sqlite3.connect(db_path)
        
        conn.execute('''
            INSERT OR REPLACE INTO user_preferences (user, preference_type, preference_value, confidence)
            VALUES (?, ?, ?, ?)
        ''', (user, preference_type, preference_value, confidence))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Updated preference for user {user}: {preference_type} = {preference_value}")
        
    except Exception as e:
        logger.error(f"Failed to update user preference: {e}")

def retrain_if_needed(threshold: int = 100):
    """Check if retraining is needed based on feedback volume"""
    try:
        from flask import current_app
        
        db_path = current_app.config.get('SELFLEARN_DB', 'instance/selflearn.db')
        conn = sqlite3.connect(db_path)
        
        # Count unprocessed feedback
        cursor = conn.execute('''
            SELECT COUNT(*) FROM feedback WHERE processed = FALSE
        ''')
        
        unprocessed_count = cursor.fetchone()[0]
        
        conn.close()
        
        if unprocessed_count >= threshold:
            logger.info(f"Retraining triggered: {unprocessed_count} unprocessed feedback items")
            trigger_retraining_pipeline()
        else:
            logger.debug(f"Retraining not needed: {unprocessed_count}/{threshold} feedback items")
            
    except Exception as e:
        logger.error(f"Failed to check retraining needs: {e}")

def trigger_retraining_pipeline():
    """Trigger the retraining pipeline"""
    try:
        from flask import current_app
        
        # In production, this would trigger actual ML retraining
        # For now, we'll create learning insights from the feedback
        
        insights = generate_learning_insights()
        
        # Store insights
        db_path = current_app.config.get('SELFLEARN_DB', 'instance/selflearn.db')
        conn = sqlite3.connect(db_path)
        
        for insight in insights:
            conn.execute('''
                INSERT INTO learning_insights (insight_type, insight_data, confidence)
                VALUES (?, ?, ?)
            ''', (insight['type'], json.dumps(insight['data']), insight['confidence']))
        
        # Mark feedback as processed
        conn.execute('UPDATE feedback SET processed = TRUE WHERE processed = FALSE')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Retraining pipeline completed: {len(insights)} insights generated")
        
    except Exception as e:
        logger.error(f"Failed to trigger retraining pipeline: {e}")

def generate_learning_insights() -> List[Dict[str, Any]]:
    """Generate learning insights from feedback data"""
    try:
        from flask import current_app
        
        db_path = current_app.config.get('SELFLEARN_DB', 'instance/selflearn.db')
        conn = sqlite3.connect(db_path)
        
        # Get recent feedback
        cursor = conn.execute('''
            SELECT user, input, response, rating, metadata
            FROM feedback
            WHERE processed = FALSE AND rating IS NOT NULL
            ORDER BY ts DESC
        ''')
        
        feedback_data = cursor.fetchall()
        conn.close()
        
        insights = []
        
        if feedback_data:
            # Analyze common patterns in high-rated responses
            high_rated = [row for row in feedback_data if row[3] >= 4]
            low_rated = [row for row in feedback_data if row[3] <= 2]
            
            if high_rated:
                insights.append({
                    'type': 'successful_patterns',
                    'data': {
                        'count': len(high_rated),
                        'common_features': analyze_successful_responses([row[2] for row in high_rated])
                    },
                    'confidence': 0.8
                })
            
            if low_rated:
                insights.append({
                    'type': 'improvement_areas',
                    'data': {
                        'count': len(low_rated),
                        'common_issues': analyze_problematic_responses([row[2] for row in low_rated])
                    },
                    'confidence': 0.7
                })
        
        return insights
        
    except Exception as e:
        logger.error(f"Failed to generate learning insights: {e}")
        return []

# Helper functions for pattern analysis
def analyze_frequent_topics(inputs: List[str]) -> Dict[str, int]:
    """Analyze frequent topics in user inputs"""
    topics = {}
    for input_text in inputs:
        words = input_text.lower().split()
        for word in words:
            if len(word) > 3:  # Skip short words
                topics[word] = topics.get(word, 0) + 1
    
    # Return top 10 topics
    return dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10])

def analyze_response_style(responses: List[str]) -> Dict[str, Any]:
    """Analyze preferred response styles"""
    total_responses = len(responses)
    if total_responses == 0:
        return {}
    
    avg_length = sum(len(response) for response in responses) / total_responses
    
    return {
        'average_length': int(avg_length),
        'preferred_style': 'concise' if avg_length < 200 else 'detailed'
    }

def analyze_time_patterns(timestamps: List[str]) -> Dict[str, Any]:
    """Analyze time-based interaction patterns"""
    try:
        hours = []
        for ts in timestamps:
            if ts:
                dt = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
                hours.append(dt.hour)
        
        if not hours:
            return {}
        
        # Find most common hour
        hour_counts = {}
        for hour in hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        most_active_hour = max(hour_counts, key=hour_counts.get)
        
        return {
            'most_active_hour': most_active_hour,
            'total_interactions': len(hours)
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze time patterns: {e}")
        return {}

def analyze_satisfaction_trends(satisfaction_data: List[Tuple[int, str]]) -> Dict[str, Any]:
    """Analyze satisfaction trends over time"""
    if not satisfaction_data:
        return {}
    
    ratings = [item[0] for item in satisfaction_data if item[0] is not None]
    
    if not ratings:
        return {}
    
    return {
        'average_satisfaction': round(sum(ratings) / len(ratings), 2),
        'trend': 'improving' if len(ratings) > 1 and ratings[0] > ratings[-1] else 'stable'
    }

def analyze_successful_responses(responses: List[str]) -> Dict[str, Any]:
    """Analyze common features in successful responses"""
    if not responses:
        return {}
    
    avg_length = sum(len(response) for response in responses) / len(responses)
    
    return {
        'average_length': int(avg_length),
        'count': len(responses),
        'characteristics': 'helpful and detailed' if avg_length > 100 else 'concise and direct'
    }

def analyze_problematic_responses(responses: List[str]) -> Dict[str, Any]:
    """Analyze common issues in problematic responses"""
    if not responses:
        return {}
    
    avg_length = sum(len(response) for response in responses) / len(responses)
    
    return {
        'average_length': int(avg_length),
        'count': len(responses),
        'potential_issues': 'too brief' if avg_length < 50 else 'may lack clarity'
    }