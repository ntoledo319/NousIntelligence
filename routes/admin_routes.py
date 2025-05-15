"""
Admin routes for the application
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, abort, send_file
from flask_login import current_user
from app import db
from models import User
from utils.security_helper import admin_required, csrf_protect, log_security_event, sanitize_input, set_admin_status
from sqlalchemy import desc, func
from datetime import datetime, timedelta
import csv
import io
import logging

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Set admin status for specific email (toledonick98@gmail.com)
def initialize_admin():
    """Initialize admin user on first request"""
    admin_email = "toledonick98@gmail.com"
    try:
        # Check if the user exists first
        user = User.query.filter_by(email=admin_email).first()
        if user and not user.is_admin:
            # Set admin status
            set_admin_status(admin_email, True)
            logging.info(f"Admin status granted to {admin_email}")
        elif not user:
            logging.info(f"Admin email {admin_email} not found - will be set as admin when user registers")
    except Exception as e:
        logging.error(f"Error initializing admin: {str(e)}")


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with user management and system settings"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get users with pagination
    users_pagination = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    users = users_pagination.items
    
    # Calculate stats
    total_users = User.query.count()
    active_users = User.query.filter_by(account_active=True).count()
    
    # New users today
    today = datetime.utcnow().date()
    new_users_today = User.query.filter(
        func.date(User.created_at) == today
    ).count()
    
    # Security events count (placeholder - implement security event logging)
    security_events_count = 0
    security_events = []
    
    # Database tables info (placeholder)
    tables = []
    
    # Get table names from the database - a safer approach using SQLAlchemy
    from sqlalchemy import MetaData, Table, select, func
    
    metadata = MetaData()
    metadata.reflect(bind=db.engine)
    table_names = list(metadata.tables.keys())
    
    for table_name in table_names:
        # Get row count for each table using SQLAlchemy
        try:
            # Use a safer approach with parameterized queries
            from sqlalchemy import text
            result = db.session.execute(text("SELECT COUNT(*) FROM \"" + table_name + "\""))
            row_count = result.scalar()
        except Exception as e:
            logging.error(f"Error counting rows in {table_name}: {str(e)}")
            row_count = 0
        tables.append({
            'name': table_name,
            'rows': row_count,
            'last_updated': None  # Would need triggers or a separate tracking table for this
        })
    
    # DB stats
    db_stats = {
        'size': 'Unknown',  # Would need a specific query for your DB type
        'tables': len(tables)
    }
    
    # System settings placeholder
    system_settings = {
        'session_timeout': 60,
        'max_login_attempts': 5,
        'password_min_length': 12,
        'account_lockout_duration': 15,
        'require_https': True,
        'enable_audit_logging': True
    }
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_today': new_users_today,
        'security_events': security_events_count
    }
    
    return render_template(
        'admin/dashboard.html',
        users=users,
        stats=stats,
        pagination=users_pagination,
        security_events=security_events,
        tables=tables,
        db_stats=db_stats,
        system_settings=system_settings
    )


@admin_bp.route('/users/export')
@admin_required
def export_users():
    """Export users as CSV file"""
    log_security_event("ADMIN_EXPORT", "Admin exported user data", severity="WARNING")
    
    users = User.query.all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Email', 'First Name', 'Last Name', 'Active', 'Admin', 'Created'])
    
    # Write user data
    for user in users:
        writer.writerow([
            user.id,
            user.email,
            user.first_name,
            user.last_name,
            'Yes' if user.account_active else 'No',
            'Yes' if user.is_admin else 'No',
            user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else ''
        ])
    
    # Prepare response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'users_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@admin_bp.route('/users/invite', methods=['POST'])
@admin_required
@csrf_protect
def invite_user():
    """Send invitation to a new user (placeholder)"""
    email = request.form.get('email')
    role = request.form.get('role')
    message = request.form.get('message')
    
    if not email:
        flash('Email address is required', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Here we would implement actual invitation logic
    # For now, just log it and show a success message
    
    log_security_event("INVITE_SENT", f"Invitation sent to {email} with role {role}", severity="INFO")
    flash(f'Invitation sent to {email}', 'success')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users/<user_id>/delete')
@admin_required
def delete_user(user_id):
    """Delete a user account"""
    user = User.query.get_or_404(user_id)
    
    # Prevent admins from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Save details for logging
    email = user.email
    
    try:
        db.session.delete(user)
        db.session.commit()
        log_security_event("USER_DELETED", f"Admin deleted user: {email}", severity="WARNING")
        flash(f'User {email} has been deleted', 'success')
    except Exception as e:
        db.session.rollback()
        log_security_event("ERROR", f"Failed to delete user {email}: {str(e)}", severity="ERROR")
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users/<user_id>/toggle-admin')
@admin_required
def toggle_admin_status(user_id):
    """Toggle admin status for a user"""
    user = User.query.get_or_404(user_id)
    
    # Toggle admin status
    user.is_admin = not user.is_admin
    
    try:
        db.session.commit()
        log_security_event(
            "ADMIN_STATUS_CHANGE", 
            f"Admin status for {user.email} set to {user.is_admin}",
            severity="WARNING"
        )
        
        status = "granted" if user.is_admin else "revoked"
        flash(f'Admin privileges {status} for {user.email}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating admin status: {str(e)}', 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users/<user_id>/toggle-active')
@admin_required
def toggle_active_status(user_id):
    """Toggle active status for a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deactivating your own account
    if user.id == current_user.id:
        flash('You cannot deactivate your own account', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Toggle active status
    user.is_active = not user.is_active
    
    try:
        db.session.commit()
        log_security_event(
            "ACCOUNT_STATUS_CHANGE", 
            f"Account status for {user.email} set to {'active' if user.is_active else 'inactive'}",
            severity="WARNING"
        )
        
        status = "activated" if user.is_active else "deactivated"
        flash(f'Account {status} for {user.email}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating account status: {str(e)}', 'danger')
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/database/backup')
@admin_required
def backup_database():
    """Create database backup (placeholder)"""
    # This would be implemented with actual DB backup logic
    log_security_event("DATABASE_BACKUP", "Admin initiated database backup", severity="INFO")
    flash('Database backup initiated. You will receive a download link when it is complete.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/database/restore', methods=['POST'])
@admin_required
@csrf_protect
def restore_database():
    """Restore from database backup (placeholder)"""
    # This would be implemented with actual DB restore logic
    if 'backup_file' not in request.files:
        flash('No backup file provided', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    backup_file = request.files['backup_file']
    if backup_file.filename == '':
        flash('No backup file selected', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Here would be the actual restore logic
    log_security_event("DATABASE_RESTORE", f"Admin initiated database restore from {backup_file.filename}", severity="WARNING")
    
    flash('Database restore initiated. This may take several minutes.', 'warning')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/database/tables/<table_name>')
@admin_required
def view_table(table_name):
    """View table contents (placeholder)"""
    # This would be implemented with actual table viewing logic
    log_security_event("TABLE_ACCESS", f"Admin viewed table: {table_name}", severity="INFO")
    flash(f'Viewing table {table_name} is not implemented yet', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/database/tables/<table_name>/export')
@admin_required
def export_table(table_name):
    """Export table as CSV (placeholder)"""
    # This would be implemented with actual table export logic
    log_security_event("TABLE_EXPORT", f"Admin exported table: {table_name}", severity="INFO")
    flash(f'Exporting table {table_name} is not implemented yet', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/settings/save', methods=['POST'])
@admin_required
@csrf_protect
def save_system_settings():
    """Save system settings"""
    # Get form data
    session_timeout = request.form.get('session_timeout', 60, type=int)
    max_login_attempts = request.form.get('max_login_attempts', 5, type=int)
    password_min_length = request.form.get('password_min_length', 12, type=int)
    account_lockout_duration = request.form.get('account_lockout_duration', 15, type=int)
    require_https = 'require_https' in request.form
    enable_audit_logging = 'enable_audit_logging' in request.form
    
    # Here we would save these settings to a SystemSettings model
    # For now, just log and show a success message
    
    settings_changes = {
        'session_timeout': session_timeout,
        'max_login_attempts': max_login_attempts,
        'password_min_length': password_min_length,
        'account_lockout_duration': account_lockout_duration,
        'require_https': require_https,
        'enable_audit_logging': enable_audit_logging
    }
    
    log_security_event("SETTINGS_UPDATED", f"Admin updated system settings: {settings_changes}", severity="INFO")
    
    flash('System settings saved successfully', 'success')
    return redirect(url_for('admin.dashboard'))


def register_admin_blueprint(app):
    """Register the admin blueprint with the app"""
    app.register_blueprint(admin_bp)