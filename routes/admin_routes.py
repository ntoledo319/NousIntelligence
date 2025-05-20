"""
Admin routes for the application
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, abort, send_file
from flask_login import current_user
from app import db
from models import User, SystemSettings
from utils.security_helper import admin_required, csrf_protect, log_security_event, sanitize_input, set_admin_status
from sqlalchemy import desc, func, inspect, MetaData, Table, select, text
from datetime import datetime, timedelta
import csv
import io
import logging
import os
from utils.settings import get_all_settings, set_setting

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
    metadata = MetaData()
    metadata.reflect(bind=db.engine)
    table_names = list(metadata.tables.keys())
    
    for table_name in table_names:
        # Get row count for each table using SQLAlchemy
        try:
            # Use a safer approach with parameterized queries
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
    
    # Get system settings from the database
    system_settings = get_all_settings()
    
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
    """Create database backup"""
    try:
        # Get database URL from config
        db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        # Generate timestamp for filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_{timestamp}.sql"
        
        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, filename)
        
        # Use database-specific dump command
        if 'postgresql' in db_url:
            # Parse database URL to get connection details
            from urllib.parse import urlparse
            url = urlparse(db_url)
            dbname = url.path[1:]  # Remove leading slash
            user = url.username
            password = url.password
            host = url.hostname
            port = url.port or 5432
            
            # Set environment variables for pg_dump (avoids password in command line)
            env = os.environ.copy()
            if password:
                env['PGPASSWORD'] = password
            
            # Execute pg_dump command
            import subprocess
            cmd = [
                'pg_dump', 
                '-h', host,
                '-p', str(port),
                '-U', user,
                '-F', 'c',  # Custom format
                '-b',  # Binary format
                '-v',  # Verbose
                '-f', backup_path,
                dbname
            ]
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr}")
        
        elif 'sqlite' in db_url:
            # For SQLite, we can just copy the database file
            import shutil
            db_path = db_url.replace('sqlite:///', '')
            shutil.copy2(db_path, backup_path)
        
        else:
            flash('Unsupported database type for backup', 'danger')
            return redirect(url_for('admin.dashboard'))
        
        # Log the backup event
        log_security_event("DATABASE_BACKUP", "Admin created database backup", severity="INFO")
        
        # Provide the file for download
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Database backup failed: {str(e)}")
        flash(f'Database backup failed: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/database/restore', methods=['POST'])
@admin_required
@csrf_protect
def restore_database():
    """Restore from database backup"""
    try:
        if 'backup_file' not in request.files:
            flash('No backup file provided', 'danger')
            return redirect(url_for('admin.dashboard'))
        
        backup_file = request.files['backup_file']
        if backup_file.filename == '':
            flash('No backup file selected', 'danger')
            return redirect(url_for('admin.dashboard'))
        
        # Save the uploaded file temporarily
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        temp_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"restore_{timestamp}")
        backup_file.save(temp_path)
        
        # Get database URL from config
        db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        try:
            # Use database-specific restore command
            if 'postgresql' in db_url:
                # Parse database URL to get connection details
                from urllib.parse import urlparse
                url = urlparse(db_url)
                dbname = url.path[1:]  # Remove leading slash
                user = url.username
                password = url.password
                host = url.hostname
                port = url.port or 5432
                
                # Set environment variables for pg_restore (avoids password in command line)
                env = os.environ.copy()
                if password:
                    env['PGPASSWORD'] = password
                
                # Execute pg_restore command
                import subprocess
                cmd = [
                    'pg_restore', 
                    '-h', host,
                    '-p', str(port),
                    '-U', user,
                    '-d', dbname,
                    '-c',  # Clean (drop) objects before recreating
                    '-v',  # Verbose
                    temp_path
                ]
                result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise Exception(f"pg_restore failed: {result.stderr}")
            
            elif 'sqlite' in db_url:
                # For SQLite, replace the database file
                import shutil
                db_path = db_url.replace('sqlite:///', '')
                
                # Create a backup of the current database first
                backup_timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                backup_db_path = f"{db_path}.backup_{backup_timestamp}"
                shutil.copy2(db_path, backup_db_path)
                
                # Replace with the uploaded file
                shutil.copy2(temp_path, db_path)
            
            else:
                flash('Unsupported database type for restore', 'danger')
                return redirect(url_for('admin.dashboard'))
            
            # Log the restore event
            log_security_event("DATABASE_RESTORE", "Admin restored database from backup", severity="WARNING")
            
            flash('Database restored successfully. You may need to restart the application.', 'success')
            return redirect(url_for('admin.dashboard'))
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Database restore failed: {str(e)}")
        flash(f'Database restore failed: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/database/tables/<table_name>')
@admin_required
def view_table(table_name):
    """View table contents"""
    try:
        # Sanitize table name to prevent SQL injection
        table_name = sanitize_input(table_name)
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # Limit max per page
        
        # Validate that the table exists
        inspector = inspect(db.engine)
        if table_name not in inspector.get_table_names():
            flash(f'Table {table_name} does not exist', 'danger')
            return redirect(url_for('admin.dashboard'))
        
        # Get table information
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=db.engine)
        columns = [column.name for column in table.columns]
        
        # Count total rows
        count_query = select(func.count()).select_from(table)
        total_rows = db.session.execute(count_query).scalar()
        
        # Calculate pagination
        total_pages = (total_rows + per_page - 1) // per_page
        offset = (page - 1) * per_page
        
        # Query data with pagination
        query = select(table).limit(per_page).offset(offset)
        result = db.session.execute(query)
        rows = [dict(row) for row in result]
        
        # Log the table access
        log_security_event("TABLE_ACCESS", f"Admin viewed table: {table_name}", severity="INFO")
        
        # Render the table view
        return render_template(
            'admin/table_view.html',
            table_name=table_name,
            columns=columns,
            rows=rows,
            page=page,
            per_page=per_page,
            total_rows=total_rows,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error viewing table {table_name}: {str(e)}")
        flash(f'Error viewing table: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/database/tables/<table_name>/export')
@admin_required
def export_table(table_name):
    """Export table as CSV"""
    try:
        # Sanitize table name to prevent SQL injection
        table_name = sanitize_input(table_name)
        
        # Validate that the table exists
        inspector = inspect(db.engine)
        if table_name not in inspector.get_table_names():
            flash(f'Table {table_name} does not exist', 'danger')
            return redirect(url_for('admin.dashboard'))
        
        # Get table information
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=db.engine)
        columns = [column.name for column in table.columns]
        
        # Query all data
        query = select(table)
        result = db.session.execute(query)
        rows = [dict(row) for row in result]
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(columns)
        
        # Write data rows
        for row in rows:
            writer.writerow([row.get(col, '') for col in columns])
        
        # Log the export event
        log_security_event("TABLE_EXPORT", f"Admin exported table: {table_name}", severity="INFO")
        
        # Prepare response
        output.seek(0)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{table_name}_export_{timestamp}.csv'
        )
        
    except Exception as e:
        logger.error(f"Error exporting table {table_name}: {str(e)}")
        flash(f'Error exporting table: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/settings/save', methods=['POST'])
@admin_required
@csrf_protect
def save_system_settings():
    """Save system settings"""
    from utils.settings import set_setting
    
    # Define all supported settings and their types
    settings_config = {
        # Security settings
        'session_timeout': int,
        'max_login_attempts': int,
        'password_min_length': int,
        'account_lockout_duration': int,
        'require_https': bool,
        'enable_audit_logging': bool,
        
        # Feature settings
        'enable_beta_features': bool,
        'enable_social_login': bool,
        'enable_registration': bool,
        
        # Email settings
        'email_from_name': str,
        'email_from_address': str
    }
    
    # Process the form data
    try:
        for key, value_type in settings_config.items():
            # Get value from form
            if value_type == bool:
                # Checkbox - present means True, absent means False
                value = key in request.form
            else:
                # Other form fields - convert to appropriate type
                form_value = request.form.get(key, '')
                if value_type == int:
                    try:
                        value = int(form_value)
                    except (ValueError, TypeError):
                        # Use default if conversion fails
                        flash(f"Invalid value for {key}. Using default value.", "warning")
                        continue
                else:
                    value = form_value
            
            # Save to database
            set_setting(key, value)
        
        # Log the update
        log_security_event("SETTINGS_UPDATED", "Admin updated system settings", severity="INFO")
        
        flash('System settings saved successfully', 'success')
    except Exception as e:
        logger.error(f"Error saving system settings: {str(e)}")
        flash(f'Error saving settings: {str(e)}', 'danger')
    
    return redirect(url_for('admin.system_settings'))


@admin_bp.route('/settings')
@admin_required
def system_settings():
    """View and edit system settings"""
    from utils.settings import get_all_settings
    
    # Get all settings
    settings = get_all_settings()
    
    return render_template(
        'admin/system_settings.html',
        system_settings=settings
    )


def register_admin_blueprint(app):
    """Register the admin blueprint with the app"""
    app.register_blueprint(admin_bp)