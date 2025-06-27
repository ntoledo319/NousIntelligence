"""
Beta Admin Console Routes
Protected admin interface for toledonick98@gmail.com
"""
import os
import uuid
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Create blueprint
beta_admin_bp = Blueprint('beta_admin', __name__, url_prefix='/admin/beta')

# Admin email configuration
SUPER_ADMIN_EMAIL = 'toledonick98@gmail.com'

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            flash('Please log in to access the admin console.', 'warning')
            return redirect(url_for('login'))
        
        user_email = session['user'].get('email', '').lower()
        if user_email != SUPER_ADMIN_EMAIL.lower():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('landing'))
        
        return f(*args, **kwargs)
    return decorated_function

@beta_admin_bp.route('/')
@admin_required
def dashboard():
    """Beta admin dashboard"""
    try:
        # Get database connection
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            flash('Database not configured', 'error')
            return render_template('admin/beta_dashboard.html', stats={})
        
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Initialize tables if they don't exist
        _ensure_tables_exist(engine)
        
        # Get statistics
        stats = {
            'total_users': 0,
            'active_users': 0,
            'total_feedback': 0,
            'new_feedback': 0,
            'feature_flags': 0,
            'enabled_flags': 0
        }
        
        try:
            # Beta users stats
            result = db_session.execute(text("SELECT COUNT(*) FROM beta_users"))
            stats['total_users'] = result.scalar() or 0
            
            result = db_session.execute(text("SELECT COUNT(*) FROM beta_users WHERE is_active = true"))
            stats['active_users'] = result.scalar() or 0
            
            # Feedback stats
            result = db_session.execute(text("SELECT COUNT(*) FROM beta_feedback"))
            stats['total_feedback'] = result.scalar() or 0
            
            result = db_session.execute(text("SELECT COUNT(*) FROM beta_feedback WHERE status = 'NEW'"))
            stats['new_feedback'] = result.scalar() or 0
            
            # Feature flags stats
            result = db_session.execute(text("SELECT COUNT(*) FROM feature_flags"))
            stats['feature_flags'] = result.scalar() or 0
            
            result = db_session.execute(text("SELECT COUNT(*) FROM feature_flags WHERE is_enabled = true"))
            stats['enabled_flags'] = result.scalar() or 0
            
        except Exception as e:
            logger.error(f"Error fetching stats: {str(e)}")
        
        finally:
            db_session.close()
        
        return render_template('admin/beta_dashboard.html', stats=stats)
        
    except Exception as e:
        logger.error(f"Admin dashboard error: {str(e)}")
        flash(f'Dashboard error: {str(e)}', 'error')
        return render_template('admin/beta_dashboard.html', stats={})

@beta_admin_bp.route('/users')
@admin_required
def manage_users():
    """Manage beta users"""
    try:
        db_url = os.environ.get('DATABASE_URL')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Get all beta users
        result = db_session.execute(text("""
            SELECT id, email, invite_code, joined_at, is_active, role, notes 
            FROM beta_users 
            ORDER BY joined_at DESC
        """))
        
        users = []
        for row in result:
            users.append({
                'id': row[0],
                'email': row[1],
                'invite_code': row[2],
                'joined_at': row[3],
                'is_active': row[4],
                'role': row[5],
                'notes': row[6]
            })
        
        db_session.close()
        return render_template('admin/manage_users.html', users=users)
        
    except Exception as e:
        logger.error(f"Manage users error: {str(e)}")
        flash(f'Error loading users: {str(e)}', 'error')
        return render_template('admin/manage_users.html', users=[])

@beta_admin_bp.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    """Add new beta user"""
    try:
        email = request.form.get('email', '').strip().lower()
        role = request.form.get('role', 'TESTER')
        notes = request.form.get('notes', '')
        
        if not email:
            flash('Email is required', 'error')
            return redirect(url_for('beta_admin.manage_users'))
        
        # Generate invite code
        invite_code = str(uuid.uuid4())[:8].upper()
        
        db_url = os.environ.get('DATABASE_URL')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Check if user already exists
        result = db_session.execute(text("SELECT id FROM beta_users WHERE email = :email"), {"email": email})
        if result.fetchone():
            flash('User already exists', 'warning')
            db_session.close()
            return redirect(url_for('beta_admin.manage_users'))
        
        # Insert new user
        user_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO beta_users (id, email, invite_code, role, notes, joined_at, is_active)
            VALUES (:id, :email, :invite_code, :role, :notes, :joined_at, :is_active)
        """), {
            "id": user_id,
            "email": email,
            "invite_code": invite_code,
            "role": role,
            "notes": notes,
            "joined_at": datetime.utcnow(),
            "is_active": True
        })
        
        db_session.commit()
        db_session.close()
        
        flash(f'Beta user added successfully. Invite code: {invite_code}', 'success')
        return redirect(url_for('beta_admin.manage_users'))
        
    except Exception as e:
        logger.error(f"Add user error: {str(e)}")
        flash(f'Error adding user: {str(e)}', 'error')
        return redirect(url_for('beta_admin.manage_users'))

@beta_admin_bp.route('/users/<user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        db_url = os.environ.get('DATABASE_URL')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Get current status
        result = db_session.execute(text("SELECT is_active FROM beta_users WHERE id = :id"), {"id": user_id})
        row = result.fetchone()
        
        if not row:
            flash('User not found', 'error')
        else:
            new_status = not row[0]
            db_session.execute(text("UPDATE beta_users SET is_active = :status WHERE id = :id"), {
                "status": new_status,
                "id": user_id
            })
            db_session.commit()
            
            status_text = "activated" if new_status else "deactivated"
            flash(f'User {status_text} successfully', 'success')
        
        db_session.close()
        return redirect(url_for('beta_admin.manage_users'))
        
    except Exception as e:
        logger.error(f"Toggle user status error: {str(e)}")
        flash(f'Error updating user status: {str(e)}', 'error')
        return redirect(url_for('beta_admin.manage_users'))

@beta_admin_bp.route('/flags')
@admin_required
def manage_flags():
    """Manage feature flags"""
    try:
        db_url = os.environ.get('DATABASE_URL')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Get all feature flags
        result = db_session.execute(text("""
            SELECT id, name, description, is_enabled, rollout_percentage, created_at, created_by
            FROM feature_flags 
            ORDER BY created_at DESC
        """))
        
        flags = []
        for row in result:
            flags.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'is_enabled': row[3],
                'rollout_percentage': row[4],
                'created_at': row[5],
                'created_by': row[6]
            })
        
        db_session.close()
        return render_template('admin/manage_flags.html', flags=flags)
        
    except Exception as e:
        logger.error(f"Manage flags error: {str(e)}")
        flash(f'Error loading flags: {str(e)}', 'error')
        return render_template('admin/manage_flags.html', flags=[])

@beta_admin_bp.route('/flags/add', methods=['POST'])
@admin_required
def add_flag():
    """Add new feature flag"""
    try:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '')
        is_enabled = request.form.get('is_enabled') == 'on'
        rollout_percentage = int(request.form.get('rollout_percentage', 0))
        
        if not name:
            flash('Flag name is required', 'error')
            return redirect(url_for('beta_admin.manage_flags'))
        
        db_url = os.environ.get('DATABASE_URL')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Check if flag already exists
        result = db_session.execute(text("SELECT id FROM feature_flags WHERE name = :name"), {"name": name})
        if result.fetchone():
            flash('Feature flag already exists', 'warning')
            db_session.close()
            return redirect(url_for('beta_admin.manage_flags'))
        
        # Insert new flag
        flag_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO feature_flags (id, name, description, is_enabled, rollout_percentage, created_at, created_by)
            VALUES (:id, :name, :description, :is_enabled, :rollout_percentage, :created_at, :created_by)
        """), {
            "id": flag_id,
            "name": name,
            "description": description,
            "is_enabled": is_enabled,
            "rollout_percentage": rollout_percentage,
            "created_at": datetime.utcnow(),
            "created_by": SUPER_ADMIN_EMAIL
        })
        
        db_session.commit()
        db_session.close()
        
        flash('Feature flag added successfully', 'success')
        return redirect(url_for('beta_admin.manage_flags'))
        
    except Exception as e:
        logger.error(f"Add flag error: {str(e)}")
        flash(f'Error adding flag: {str(e)}', 'error')
        return redirect(url_for('beta_admin.manage_flags'))

@beta_admin_bp.route('/flags/<flag_id>/toggle', methods=['POST'])
@admin_required
def toggle_flag(flag_id):
    """Toggle feature flag status"""
    try:
        db_url = os.environ.get('DATABASE_URL')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Get current status
        result = db_session.execute(text("SELECT is_enabled FROM feature_flags WHERE id = :id"), {"id": flag_id})
        row = result.fetchone()
        
        if not row:
            flash('Feature flag not found', 'error')
        else:
            new_status = not row[0]
            db_session.execute(text("UPDATE feature_flags SET is_enabled = :status WHERE id = :id"), {
                "status": new_status,
                "id": flag_id
            })
            db_session.commit()
            
            status_text = "enabled" if new_status else "disabled"
            flash(f'Feature flag {status_text} successfully', 'success')
        
        db_session.close()
        return redirect(url_for('beta_admin.manage_flags'))
        
    except Exception as e:
        logger.error(f"Toggle flag error: {str(e)}")
        flash(f'Error updating flag: {str(e)}', 'error')
        return redirect(url_for('beta_admin.manage_flags'))

@beta_admin_bp.route('/feedback')
@admin_required
def view_feedback():
    """View beta feedback"""
    try:
        db_url = os.environ.get('DATABASE_URL')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Get all feedback with user info
        result = db_session.execute(text("""
            SELECT f.id, f.feature_name, f.rating, f.feedback_text, f.status, 
                   f.submitted_at, u.email as user_email, f.page_url
            FROM beta_feedback f
            LEFT JOIN beta_users u ON f.user_id = u.id
            ORDER BY f.submitted_at DESC
        """))
        
        feedback = []
        for row in result:
            feedback.append({
                'id': row[0],
                'feature_name': row[1],
                'rating': row[2],
                'feedback_text': row[3],
                'status': row[4],
                'submitted_at': row[5],
                'user_email': row[6],
                'page_url': row[7]
            })
        
        db_session.close()
        return render_template('admin/view_feedback.html', feedback=feedback)
        
    except Exception as e:
        logger.error(f"View feedback error: {str(e)}")
        flash(f'Error loading feedback: {str(e)}', 'error')
        return render_template('admin/view_feedback.html', feedback=[])

@beta_admin_bp.route('/feedback/export')
@admin_required
def export_feedback():
    """Export feedback as CSV"""
    try:
        db_url = os.environ.get('DATABASE_URL')
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        # Get all feedback
        result = db_session.execute(text("""
            SELECT f.id, f.feature_name, f.rating, f.feedback_text, f.status, 
                   f.submitted_at, u.email as user_email, f.page_url, f.user_agent
            FROM beta_feedback f
            LEFT JOIN beta_users u ON f.user_id = u.id
            ORDER BY f.submitted_at DESC
        """))
        
        # Create CSV content
        csv_content = "ID,Feature,Rating,Feedback,Status,Submitted,User,URL,User Agent\n"
        for row in result:
            csv_content += f'"{row[0]}","{row[1]}","{row[2]}","{row[3]}","{row[4]}","{row[5]}","{row[6]}","{row[7]}","{row[8]}"\n'
        
        db_session.close()
        
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=beta_feedback_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
        
    except Exception as e:
        logger.error(f"Export feedback error: {str(e)}")
        flash(f'Error exporting feedback: {str(e)}', 'error')
        return redirect(url_for('beta_admin.view_feedback'))

def _ensure_tables_exist(engine):
    """Ensure beta tables exist in database"""
    try:
        with engine.connect() as conn:
            # Create beta_users table
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
            
            # Create beta_feedback table
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
            
            # Create feature_flags table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS feature_flags (
                    id VARCHAR(36) PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    is_enabled BOOLEAN DEFAULT FALSE,
                    rollout_percentage INTEGER DEFAULT 0,
                    target_users JSON,
                    conditions JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(120)
                )
            """))
            
            # Create system_metrics table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id VARCHAR(36) PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metric_type VARCHAR(50) NOT NULL,
                    metric_value INTEGER,
                    metadata JSON
                )
            """))
            
            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_beta_users_email ON beta_users(email)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_beta_feedback_user ON beta_feedback(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_feature_flags_name ON feature_flags(name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_system_metrics_type ON system_metrics(metric_type)"))
            
            conn.commit()
            
            # Initialize super admin user
            conn.execute(text("""
                INSERT INTO beta_users (id, email, invite_code, role, joined_at, is_active, notes)
                VALUES (:id, :email, :invite_code, :role, :joined_at, :is_active, :notes)
                ON CONFLICT (email) DO NOTHING
            """), {
                "id": str(uuid.uuid4()),
                "email": SUPER_ADMIN_EMAIL,
                "invite_code": "OWNER001",
                "role": "OWNER",
                "joined_at": datetime.utcnow(),
                "is_active": True,
                "notes": "Super admin account"
            })
            
            conn.commit()
            
    except Exception as e:
        logger.error(f"Table creation error: {str(e)}")
        raise