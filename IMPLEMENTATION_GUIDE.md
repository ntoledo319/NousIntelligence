# NOUS Implementation Guide

This document provides detailed guidance for implementing the incomplete features identified in the FEATURE_TRACKER.md file. Follow these implementation instructions to complete each feature in a consistent and maintainable way.

## General Implementation Guidelines

1. **Follow Existing Patterns**: Match the existing code style and architectural patterns
2. **Document All Changes**: Add comprehensive docstrings and comments
3. **Add Tests**: Write unit and integration tests for new functionality
4. **Error Handling**: Include proper error handling and logging
5. **Incremental Commits**: Make small, focused commits with clear messages

## Authentication & Security Features

### Google OAuth Integration

1. **Configuration Setup**:
   ```python
   # In config.py - ensure these are loaded from environment or secure storage
   GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
   GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
   GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "https://mynous.replit.app/callback/google")
   ```

2. **Client Secret File**:
   ```json
   {
     "web": {
       "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
       "project_id": "your-project-id",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_secret": "YOUR_CLIENT_SECRET",
       "redirect_uris": ["https://mynous.replit.app/callback/google"]
     }
   }
   ```

3. **Testing Strategy**:
   - Create test accounts with Google
   - Verify login flow with successful/failed scenarios
   - Test account linking if a user already exists

### Two-Factor Authentication

1. **Database Schema Verification**:
   ```python
   # Ensure these fields exist in the User model
   two_factor_enabled = db.Column(db.Boolean, default=False)
   two_factor_secret = db.Column(db.String(32))
   
   # And backup codes table
   class TwoFactorBackupCode(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
       code_hash = db.Column(db.String(128), nullable=False)
       used = db.Column(db.Boolean, default=False)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
   ```

2. **Required Dependencies**:
   ```
   pyotp==2.8.0
   qrcode==7.4.2
   pillow==9.5.0
   ```

### Beta Testing System

1. **Database Model**:
   ```python
   class BetaTester(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
       access_code = db.Column(db.String(32))
       active = db.Column(db.Boolean, default=True)
       notes = db.Column(db.Text)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
   ```

2. **Configuration Settings**:
   ```python
   # In config.py
   BETA_MODE = os.environ.get('ENABLE_BETA_MODE', 'true').lower() == 'true'
   BETA_ACCESS_CODE = os.environ.get('BETA_ACCESS_CODE', 'BETANOUS2025')
   MAX_BETA_TESTERS = int(os.environ.get('MAX_BETA_TESTERS', '30'))
   ```

## Admin Features

### Database Management

1. **Backup Implementation**:
   ```python
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
           backup_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'backups', filename)
           
           # Create backup directory if it doesn't exist
           os.makedirs(os.path.dirname(backup_path), exist_ok=True)
           
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
   ```

2. **Restore Implementation**:
   ```python
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
           temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp', f"restore_{timestamp}")
           os.makedirs(os.path.dirname(temp_path), exist_ok=True)
           backup_file.save(temp_path)
           
           # Get database URL from config
           db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
           
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
               shutil.copy2(temp_path, db_path)
           
           else:
               flash('Unsupported database type for restore', 'danger')
               return redirect(url_for('admin.dashboard'))
           
           # Log the restore event
           log_security_event("DATABASE_RESTORE", "Admin restored database from backup", severity="WARNING")
           
           flash('Database restored successfully. You may need to restart the application.', 'success')
           return redirect(url_for('admin.dashboard'))
           
       except Exception as e:
           logger.error(f"Database restore failed: {str(e)}")
           flash(f'Database restore failed: {str(e)}', 'danger')
           return redirect(url_for('admin.dashboard'))
       finally:
           # Clean up temporary file
           if os.path.exists(temp_path):
               os.remove(temp_path)
   ```

### User Invitation System

1. **Email Sending Implementation**:
   ```python
   def send_invitation_email(email, role, message=None, sender_id=None):
       """Send invitation email to new user"""
       try:
           # Generate unique invitation token
           token = secrets.token_urlsafe(32)
           
           # Store invitation in database
           invitation = UserInvitation(
               email=email,
               role=role,
               token=token,
               message=message,
               sender_id=sender_id,
               expires_at=datetime.utcnow() + timedelta(days=7)
           )
           db.session.add(invitation)
           db.session.commit()
           
           # Create invitation URL
           invitation_url = url_for('auth.register_invited', token=token, _external=True)
           
           # Build email content
           subject = "You've been invited to join NOUS"
           
           html_content = render_template(
               'email/invitation.html',
               invitation_url=invitation_url,
               role=role,
               message=message,
               expires_at=invitation.expires_at
           )
           
           # Send email
           from utils.email_sender import send_email
           send_email(email, subject, html_content)
           
           return {"success": True}
           
       except Exception as e:
           logger.error(f"Failed to send invitation email: {str(e)}")
           return {"success": False, "error": str(e)}
   ```

2. **Invitation System Integration**:
   ```python
   @admin_bp.route('/users/invite', methods=['POST'])
   @admin_required
   @csrf_protect
   def invite_user():
       """Send invitation to a new user"""
       email = request.form.get('email')
       role = request.form.get('role')
       message = request.form.get('message')
       
       if not email:
           flash('Email address is required', 'danger')
           return redirect(url_for('admin.dashboard'))
       
       # Check if user already exists
       existing_user = User.query.filter_by(email=email).first()
       if existing_user:
           flash(f'User with email {email} already exists', 'warning')
           return redirect(url_for('admin.dashboard'))
       
       # Send invitation
       result = send_invitation_email(
           email=email,
           role=role,
           message=message,
           sender_id=current_user.id
       )
       
       if result.get('success'):
           log_security_event("INVITE_SENT", f"Invitation sent to {email} with role {role}", severity="INFO")
           flash(f'Invitation sent to {email}', 'success')
       else:
           flash(f'Error sending invitation: {result.get("error")}', 'danger')
       
       return redirect(url_for('admin.dashboard'))
   ```

## For More Features

Additional implementation details for other features can be developed following the patterns shown above. Each feature implementation should include:

1. **Model Definitions**: Database schema changes
2. **Function Implementations**: Core logic and utility functions
3. **Route Handlers**: API endpoints or page controllers
4. **Template Updates**: Frontend changes if needed
5. **Testing Strategy**: How to verify the feature works

## Deployment Checklist

- [ ] Update dependencies in requirements.txt
- [ ] Create database migrations for any model changes
- [ ] Update configuration files and environment variables
- [ ] Run tests before deploying
- [ ] Document new features in user documentation
- [ ] Update CHANGELOG.md with feature additions 