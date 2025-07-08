from celery import Celery
from flask import Flask
import os
import logging

logger = logging.getLogger(__name__)

def make_celery(app: Flask) -> Celery:
    """Create Celery instance with Flask app context"""
    
    celery = Celery(
        app.import_name,
        backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
        broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    
    # Update configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_serializer='json',
        result_expires=3600,
        task_always_eager=os.getenv('CELERY_ALWAYS_EAGER', 'False').lower() == 'true'
    )
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Initialize with app
celery = None

def init_celery(app: Flask):
    """Initialize Celery with Flask app"""
    global celery
    celery = make_celery(app)
    return celery

# Background Tasks
@celery.task(bind=True)
def process_image_async(self, image_path: str, user_id: str):
    """Process uploaded images in background"""
    try:
        from src.services.image_processing import process_image
        
        self.update_state(state='PROGRESS', meta={'status': 'Processing image...'})
        
        result = process_image(image_path, user_id)
        
        return {
            'status': 'completed',
            'result': result,
            'user_id': user_id
        }
    except Exception as exc:
        logger.error(f"Image processing failed: {exc}")
        self.update_state(state='FAILURE', meta={'error': str(exc)})
        raise

@celery.task(bind=True)
def send_email_async(self, to: str, subject: str, body: str, template: str = None):
    """Send emails in background"""
    try:
        from src.services.email_service import send_email
        
        self.update_state(state='PROGRESS', meta={'status': 'Sending email...'})
        
        result = send_email(to, subject, body, template)
        
        return {
            'status': 'sent',
            'to': to,
            'result': result
        }
    except Exception as exc:
        logger.error(f"Email sending failed: {exc}")
        self.update_state(state='FAILURE', meta={'error': str(exc)})
        raise

@celery.task(bind=True)
def generate_analytics_async(self, user_id: str, report_type: str):
    """Generate analytics reports in background"""
    try:
        from src.services.analytics_service import generate_report
        
        self.update_state(state='PROGRESS', meta={'status': f'Generating {report_type} report...'})
        
        report = generate_report(user_id, report_type)
        
        return {
            'status': 'completed',
            'report': report,
            'user_id': user_id,
            'type': report_type
        }
    except Exception as exc:
        logger.error(f"Analytics generation failed: {exc}")
        self.update_state(state='FAILURE', meta={'error': str(exc)})
        raise

@celery.task
def cleanup_old_sessions():
    """Clean up expired sessions"""
    try:
        from datetime import datetime, timedelta
        from models import Session
        from app import db
        
        cutoff = datetime.utcnow() - timedelta(days=7)
        deleted = Session.query.filter(Session.expires_at < cutoff).delete()
        db.session.commit()
        
        logger.info(f"Cleaned up {deleted} expired sessions")
        return {'deleted': deleted}
    except Exception as exc:
        logger.error(f"Session cleanup failed: {exc}")
        raise

@celery.task
def optimize_database():
    """Run database optimization tasks"""
    try:
        from app import db
        
        # Analyze tables for better query planning
        db.session.execute('ANALYZE;')
        
        # Vacuum if PostgreSQL
        try:
            db.session.execute('VACUUM ANALYZE;')
        except Exception:
            pass  # Not all databases support VACUUM
            
        db.session.commit()
        
        logger.info("Database optimization completed")
        return {'status': 'completed'}
    except Exception as exc:
        logger.error(f"Database optimization failed: {exc}")
        raise

# Periodic tasks
from celery.schedules import crontab

celery.conf.beat_schedule = {
    'cleanup-sessions': {
        'task': 'cleanup_old_sessions',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'optimize-database': {
        'task': 'optimize_database',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Weekly on Sunday at 3 AM
    },
}
