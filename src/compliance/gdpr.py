from typing import Dict, Any, List
import json
from datetime import datetime

class GDPRCompliance:
    """GDPR compliance implementation"""
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR requests"""
        return {
            'user_profile': self._get_user_profile(user_id),
            'mental_health_data': self._get_mental_health_data(user_id),
            'tasks_and_productivity': self._get_task_data(user_id),
            'family_data': self._get_family_data(user_id),
            'audit_logs': self._get_audit_logs(user_id),
            'export_timestamp': datetime.utcnow().isoformat()
        }
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete all user data per GDPR right to erasure"""
        try:
            from models import User, MoodEntry, Task, ThoughtRecord
            from app import db
            
            # Delete related data
            MoodEntry.query.filter_by(user_id=user_id).delete()
            Task.query.filter_by(user_id=user_id).delete()
            ThoughtRecord.query.filter_by(user_id=user_id).delete()
            
            # Anonymize user record
            user = User.query.get(user_id)
            if user:
                user.email = f"deleted_{user_id}@privacy.invalid"
                user.name = "Deleted User"
                user.is_active = False
                user.deleted_at = datetime.utcnow()
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    def update_consent(self, user_id: str, consent_type: str, granted: bool):
        """Update user consent preferences"""
        from models import Consent
        from app import db
        
        consent = Consent(
            user_id=user_id,
            consent_type=consent_type,
            granted=granted,
            timestamp=datetime.utcnow()
        )
        db.session.add(consent)
        db.session.commit()

gdpr = GDPRCompliance()
