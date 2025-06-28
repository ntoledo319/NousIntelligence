"""
NOUS Learning System Module
Self-learning feedback system for continuous AI improvement
"""

import logging
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class LearningSystem:
    """Self-learning system for AI improvement through user feedback"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the learning system
        
        Args:
            db_path: Path to the learning database file
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'instance' / 'nous_learning.db'
        
        self.db_path = str(db_path)
        self._init_database()
        logger.info(f"Learning system initialized with database: {self.db_path}")
    
    def _init_database(self):
        """Initialize the learning database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                input_text TEXT NOT NULL,
                response_text TEXT NOT NULL,
                rating INTEGER,
                feedback_text TEXT,
                context_data TEXT,
                ai_provider TEXT,
                session_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence_score REAL,
                usage_count INTEGER DEFAULT 0,
                last_used TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                improvement_type TEXT NOT NULL,
                description TEXT NOT NULL,
                implementation_status TEXT DEFAULT 'pending',
                priority_score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                implemented_at TEXT
            )
        ''')
        
        # Create indexes for better performance
        conn.execute('CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type)')
        
        conn.commit()
        conn.close()

def init_learning_system(app):
    """Initialize learning system with Flask app
    
    Args:
        app: Flask application instance
    """
    try:
        db_path = app.config.get('LEARNING_DB_PATH')
        learning_system = LearningSystem(db_path)
        app.extensions['learning_system'] = learning_system
        logger.info("Learning system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize learning system: {e}")
        app.extensions['learning_system'] = None

def get_learning_system():
    """Get the learning system instance from the current Flask app
    
    Returns:
        LearningSystem instance or None
    """
    from flask import current_app
    try:
        return current_app.extensions.get('learning_system')
    except RuntimeError:
        # No app context
        return None

def log_interaction(user_id: str, input_text: str, response_text: str, 
                   rating: Optional[int] = None, feedback_text: Optional[str] = None,
                   context: Optional[Dict[str, Any]] = None, ai_provider: str = 'unknown',
                   session_id: Optional[str] = None):
    """Log a user interaction for learning purposes
    
    Args:
        user_id: User identifier
        input_text: User's input/prompt
        response_text: AI's response
        rating: User rating (1-5 scale, optional)
        feedback_text: Additional user feedback (optional)
        context: Additional context data (optional)
        ai_provider: AI provider used
        session_id: Session identifier (optional)
    """
    learning_system = get_learning_system()
    if not learning_system:
        logger.warning("Learning system not available - interaction not logged")
        return
    
    try:
        conn = sqlite3.connect(learning_system.db_path)
        context_json = json.dumps(context) if context else None
        
        conn.execute('''
            INSERT INTO feedback (
                timestamp, user_id, input_text, response_text, rating,
                feedback_text, context_data, ai_provider, session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.utcnow().isoformat(),
            user_id,
            input_text,
            response_text,
            rating,
            feedback_text,
            context_json,
            ai_provider,
            session_id
        ))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Interaction logged for user {user_id}")
        
        # Check if retraining is needed
        retrain_if_needed()
        
    except Exception as e:
        logger.error(f"Failed to log interaction: {e}")

def get_user_feedback(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get feedback history for a specific user
    
    Args:
        user_id: User identifier
        limit: Maximum number of records to return
        
    Returns:
        List of feedback records
    """
    learning_system = get_learning_system()
    if not learning_system:
        return []
    
    try:
        conn = sqlite3.connect(learning_system.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute('''
            SELECT * FROM feedback 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to get user feedback: {e}")
        return []

def get_feedback_analytics() -> Dict[str, Any]:
    """Get analytics about user feedback
    
    Returns:
        Analytics data dictionary
    """
    learning_system = get_learning_system()
    if not learning_system:
        return {'error': 'Learning system not available'}
    
    try:
        conn = sqlite3.connect(learning_system.db_path)
        
        # Get basic statistics
        cursor = conn.execute('SELECT COUNT(*) FROM feedback')
        total_interactions = cursor.fetchone()[0]
        
        cursor = conn.execute('SELECT COUNT(*) FROM feedback WHERE rating IS NOT NULL')
        rated_interactions = cursor.fetchone()[0]
        
        cursor = conn.execute('SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL')
        avg_rating_result = cursor.fetchone()[0]
        avg_rating = round(avg_rating_result, 2) if avg_rating_result else 0
        
        # Get rating distribution
        cursor = conn.execute('''
            SELECT rating, COUNT(*) as count 
            FROM feedback 
            WHERE rating IS NOT NULL 
            GROUP BY rating 
            ORDER BY rating
        ''')
        rating_distribution = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        # Get recent activity
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        cursor = conn.execute('''
            SELECT COUNT(*) FROM feedback 
            WHERE timestamp > ?
        ''', (week_ago,))
        recent_interactions = cursor.fetchone()[0]
        
        # Get top AI providers
        cursor = conn.execute('''
            SELECT ai_provider, COUNT(*) as count 
            FROM feedback 
            GROUP BY ai_provider 
            ORDER BY count DESC 
            LIMIT 5
        ''')
        top_providers = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_interactions': total_interactions,
            'rated_interactions': rated_interactions,
            'average_rating': avg_rating,
            'rating_distribution': rating_distribution,
            'recent_interactions_7d': recent_interactions,
            'top_ai_providers': top_providers,
            'feedback_rate': round(rated_interactions / total_interactions * 100, 1) if total_interactions > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get feedback analytics: {e}")
        return {'error': str(e)}

def identify_patterns() -> List[Dict[str, Any]]:
    """Identify patterns in user feedback for improvement
    
    Returns:
        List of identified patterns
    """
    learning_system = get_learning_system()
    if not learning_system:
        return []
    
    try:
        conn = sqlite3.connect(learning_system.db_path)
        patterns = []
        
        # Pattern 1: Low-rated responses by AI provider
        cursor = conn.execute('''
            SELECT ai_provider, AVG(rating) as avg_rating, COUNT(*) as count
            FROM feedback 
            WHERE rating IS NOT NULL AND rating <= 2
            GROUP BY ai_provider
            HAVING count >= 3
            ORDER BY avg_rating ASC
        ''')
        
        for row in cursor.fetchall():
            patterns.append({
                'type': 'low_rating_provider',
                'provider': row[0],
                'avg_rating': round(row[1], 2),
                'count': row[2],
                'suggestion': f'Consider reducing usage of {row[0]} or improving prompts'
            })
        
        # Pattern 2: Common negative feedback themes
        cursor = conn.execute('''
            SELECT feedback_text, COUNT(*) as count
            FROM feedback 
            WHERE rating IS NOT NULL AND rating <= 2 AND feedback_text IS NOT NULL
            GROUP BY feedback_text
            HAVING count >= 2
            ORDER BY count DESC
            LIMIT 10
        ''')
        
        for row in cursor.fetchall():
            patterns.append({
                'type': 'negative_feedback_theme',
                'feedback': row[0],
                'count': row[1],
                'suggestion': 'Address this common user concern'
            })
        
        # Pattern 3: High-performing response types
        cursor = conn.execute('''
            SELECT ai_provider, AVG(rating) as avg_rating, COUNT(*) as count
            FROM feedback 
            WHERE rating IS NOT NULL AND rating >= 4
            GROUP BY ai_provider
            HAVING count >= 5
            ORDER BY avg_rating DESC
        ''')
        
        for row in cursor.fetchall():
            patterns.append({
                'type': 'high_performance_provider',
                'provider': row[0],
                'avg_rating': round(row[1], 2),
                'count': row[2],
                'suggestion': f'Consider increasing usage of {row[0]}'
            })
        
        conn.close()
        
        # Store patterns in database
        if patterns:
            _store_patterns(patterns)
        
        return patterns
        
    except Exception as e:
        logger.error(f"Failed to identify patterns: {e}")
        return []

def _store_patterns(patterns: List[Dict[str, Any]]):
    """Store identified patterns in the database"""
    learning_system = get_learning_system()
    if not learning_system:
        return
    
    try:
        conn = sqlite3.connect(learning_system.db_path)
        
        for pattern in patterns:
            conn.execute('''
                INSERT INTO patterns (pattern_type, pattern_data, confidence_score)
                VALUES (?, ?, ?)
            ''', (
                pattern['type'],
                json.dumps(pattern),
                0.8  # Default confidence score
            ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to store patterns: {e}")

def suggest_improvements() -> List[Dict[str, Any]]:
    """Generate improvement suggestions based on patterns
    
    Returns:
        List of improvement suggestions
    """
    patterns = identify_patterns()
    improvements = []
    
    for pattern in patterns:
        if pattern['type'] == 'low_rating_provider':
            improvements.append({
                'type': 'provider_optimization',
                'description': f"Reduce reliance on {pattern['provider']} (avg rating: {pattern['avg_rating']})",
                'priority': 0.8,
                'implementation': 'Adjust AI provider selection logic'
            })
        
        elif pattern['type'] == 'high_performance_provider':
            improvements.append({
                'type': 'provider_optimization',
                'description': f"Increase usage of {pattern['provider']} (avg rating: {pattern['avg_rating']})",
                'priority': 0.6,
                'implementation': 'Update AI provider preferences'
            })
        
        elif pattern['type'] == 'negative_feedback_theme':
            improvements.append({
                'type': 'response_quality',
                'description': f"Address common feedback: {pattern['feedback'][:100]}...",
                'priority': 0.7,
                'implementation': 'Improve prompt engineering or add validation'
            })
    
    # Store improvements
    if improvements:
        _store_improvements(improvements)
    
    return improvements

def _store_improvements(improvements: List[Dict[str, Any]]):
    """Store improvement suggestions in the database"""
    learning_system = get_learning_system()
    if not learning_system:
        return
    
    try:
        conn = sqlite3.connect(learning_system.db_path)
        
        for improvement in improvements:
            conn.execute('''
                INSERT INTO improvements (improvement_type, description, priority_score)
                VALUES (?, ?, ?)
            ''', (
                improvement['type'],
                improvement['description'],
                improvement['priority']
            ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to store improvements: {e}")

def retrain_if_needed(threshold: int = 100):
    """Check if retraining is needed based on new feedback
    
    Args:
        threshold: Number of new feedback entries to trigger retraining
    """
    learning_system = get_learning_system()
    if not learning_system:
        return
    
    try:
        conn = sqlite3.connect(learning_system.db_path)
        
        # Count total feedback entries
        cursor = conn.execute('SELECT COUNT(*) FROM feedback')
        total_feedback = cursor.fetchone()[0]
        
        conn.close()
        
        if total_feedback >= threshold and total_feedback % threshold == 0:
            logger.info(f"Retraining threshold reached: {total_feedback} feedback entries")
            _trigger_retraining()
        
    except Exception as e:
        logger.error(f"Failed to check retraining threshold: {e}")

def _trigger_retraining():
    """Trigger the retraining pipeline"""
    try:
        # Generate new patterns and improvements
        patterns = identify_patterns()
        improvements = suggest_improvements()
        
        logger.info(f"Retraining completed: {len(patterns)} patterns, {len(improvements)} improvements identified")
        
        # In a full implementation, this would:
        # 1. Update AI model weights based on feedback
        # 2. Adjust prompt templates
        # 3. Update provider selection logic
        # 4. Refresh response quality filters
        
    except Exception as e:
        logger.error(f"Retraining failed: {e}")

def export_learning_data() -> Dict[str, Any]:
    """Export learning data for analysis
    
    Returns:
        Dictionary containing learning data
    """
    learning_system = get_learning_system()
    if not learning_system:
        return {'error': 'Learning system not available'}
    
    try:
        conn = sqlite3.connect(learning_system.db_path)
        conn.row_factory = sqlite3.Row
        
        # Export feedback data
        cursor = conn.execute('SELECT * FROM feedback ORDER BY timestamp DESC LIMIT 1000')
        feedback_data = [dict(row) for row in cursor.fetchall()]
        
        # Export patterns
        cursor = conn.execute('SELECT * FROM patterns ORDER BY created_at DESC')
        patterns_data = [dict(row) for row in cursor.fetchall()]
        
        # Export improvements
        cursor = conn.execute('SELECT * FROM improvements ORDER BY created_at DESC')
        improvements_data = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'feedback': feedback_data,
            'patterns': patterns_data,
            'improvements': improvements_data,
            'export_timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to export learning data: {e}")
        return {'error': str(e)}