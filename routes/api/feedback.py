"""
Beta Feedback API
Collects and stores user feedback for beta features
"""
import logging
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

logger = logging.getLogger(__name__)

# Create blueprint
feedback_api = Blueprint('feedback_api', __name__, url_prefix='/api')

@feedback_api.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit beta feedback"""
    try:
        # Get feedback data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract feedback fields
        feature_name = data.get('feature_name', 'general')
        rating = data.get('rating')
        feedback_text = data.get('feedback_text', '')
        page_url = data.get('page_url', request.referrer)
        
        # Validate rating if provided
        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            except (TypeError, ValueError):
                return jsonify({'error': 'Invalid rating format'}), 400
        
        # Get user info from session
        user_email = None
        user_id = None
        if 'user' in session:
            user_email = session['user'].get('email')
            user_id = session['user'].get('id')
        
        # Store feedback in database
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            logger.error("DATABASE_URL not configured")
            return jsonify({'error': 'Database not configured'}), 500
        
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Ensure tables exist
            _ensure_feedback_table(engine)
            
            # Find or create beta user
            beta_user_id = None
            if user_email:
                # Check if user exists in beta_users
                result = db_session.execute(
                    text("SELECT id FROM beta_users WHERE email = :email"),
                    {"email": user_email}
                )
                row = result.fetchone()
                if row:
                    beta_user_id = row[0]
                else:
                    # Create beta user if they don't exist
                    beta_user_id = str(uuid.uuid4())
                    invite_code = str(uuid.uuid4())[:8].upper()
                    db_session.execute(text("""
                        INSERT INTO beta_users (id, email, invite_code, joined_at, is_active, role)
                        VALUES (:id, :email, :invite_code, :joined_at, :is_active, :role)
                    """), {
                        "id": beta_user_id,
                        "email": user_email,
                        "invite_code": invite_code,
                        "joined_at": datetime.utcnow(),
                        "is_active": True,
                        "role": "TESTER"
                    })
            
            # Insert feedback
            feedback_id = str(uuid.uuid4())
            db_session.execute(text("""
                INSERT INTO beta_feedback 
                (id, user_id, feature_name, rating, feedback_text, feedback_data, 
                 page_url, user_agent, submitted_at, status)
                VALUES (:id, :user_id, :feature_name, :rating, :feedback_text, :feedback_data,
                        :page_url, :user_agent, :submitted_at, :status)
            """), {
                "id": feedback_id,
                "user_id": beta_user_id,
                "feature_name": feature_name,
                "rating": rating,
                "feedback_text": feedback_text,
                "feedback_data": '{}',  # JSON string for additional data
                "page_url": page_url,
                "user_agent": request.headers.get('User-Agent', ''),
                "submitted_at": datetime.utcnow(),
                "status": "NEW"
            })
            
            db_session.commit()
            logger.info(f"Feedback submitted: {feedback_id} from {user_email or 'anonymous'}")
            
            return jsonify({
                'success': True,
                'message': 'Feedback submitted successfully',
                'feedback_id': feedback_id
            }), 200
            
        except Exception as e:
            db_session.rollback()
            logger.error(f"Database error submitting feedback: {str(e)}")
            return jsonify({'error': 'Failed to save feedback'}), 500
            
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Feedback submission error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@feedback_api.route('/feedback/stats', methods=['GET'])
def feedback_stats():
    """Get feedback statistics (public)"""
    try:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            return jsonify({'error': 'Database not configured'}), 500
        
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        try:
            # Get basic stats
            stats = {
                'total_feedback': 0,
                'average_rating': 0,
                'feature_breakdown': {}
            }
            
            # Total feedback count
            result = db_session.execute(text("SELECT COUNT(*) FROM beta_feedback"))
            stats['total_feedback'] = result.scalar() or 0
            
            # Average rating
            result = db_session.execute(text("SELECT AVG(rating) FROM beta_feedback WHERE rating IS NOT NULL"))
            avg_rating = result.scalar()
            stats['average_rating'] = round(float(avg_rating), 2) if avg_rating else 0
            
            # Feature breakdown
            result = db_session.execute(text("""
                SELECT feature_name, COUNT(*) as count, AVG(rating) as avg_rating
                FROM beta_feedback 
                WHERE feature_name IS NOT NULL
                GROUP BY feature_name
                ORDER BY count DESC
            """))
            
            for row in result:
                stats['feature_breakdown'][row[0]] = {
                    'count': row[1],
                    'average_rating': round(float(row[2]), 2) if row[2] else 0
                }
            
            return jsonify(stats), 200
            
        except Exception as e:
            logger.error(f"Error getting feedback stats: {str(e)}")
            return jsonify({'error': 'Failed to get stats'}), 500
            
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Feedback stats error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def _ensure_feedback_table(engine):
    """Ensure feedback table exists"""
    try:
        with engine.connect() as conn:
            # Create beta_users table if not exists
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS beta_users (
                    id VARCHAR(36) PRIMARY KEY,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    invite_code VARCHAR(32) UNIQUE NOT NULL,
                    flag_set JSON,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    role VARCHAR(20) DEFAULT 'TESTER',
                    notes TEXT
                )
            """))
            
            # Create beta_feedback table if not exists
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS beta_feedback (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) REFERENCES beta_users(id),
                    feature_name VARCHAR(100),
                    rating INTEGER,
                    feedback_text TEXT,
                    feedback_data JSON,
                    page_url VARCHAR(500),
                    user_agent VARCHAR(500),
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'NEW',
                    admin_notes TEXT
                )
            """))
            
            conn.commit()
            
    except Exception as e:
        logger.error(f"Table creation error: {str(e)}")
        raise