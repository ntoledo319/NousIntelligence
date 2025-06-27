Deployment Guide
================

This guide covers deployment strategies for NOUS Personal Assistant, with primary focus on Replit Cloud deployment and alternative deployment options.

Replit Cloud Deployment
------------------------

NOUS is optimized for seamless deployment on Replit Cloud with minimal configuration.

Prerequisites
~~~~~~~~~~~~~

* Replit account with appropriate subscription
* Google OAuth credentials configured
* PostgreSQL database (automatically provided by Replit)

One-Click Deployment
~~~~~~~~~~~~~~~~~~~~

1. **Import Project**
   
   - Fork or import the repository to your Replit workspace
   - Replit automatically detects the Python environment

2. **Configure Secrets**
   
   Navigate to Secrets tab and add:
   
   .. code-block:: bash
   
       GOOGLE_CLIENT_ID=your_google_client_id
       GOOGLE_CLIENT_SECRET=your_google_client_secret
       OPENROUTER_API_KEY=your_openrouter_key  # Optional
       HUGGINGFACE_API_KEY=your_hf_key         # Optional

3. **Deploy**
   
   - Click the Run button or use ``python main.py``
   - Application automatically starts on port 5000
   - Public URL generated automatically

Configuration Files
~~~~~~~~~~~~~~~~~~~~

**replit.toml** (Deployment Configuration):

.. code-block:: toml

    run = ["python3", "main.py"]
    
    [deployment]
    run = ["python3", "main.py"]
    deploymentTarget = "cloudrun"
    
    [env]
    PORT = "5000"
    FLASK_ENV = "production"
    PUBLIC_MODE = "true"
    
    [auth]
    pageEnabled = false
    buttonEnabled = false

**replit.nix** (Environment Dependencies):

.. code-block:: nix

    { pkgs }: {
      deps = [
        pkgs.python311
        pkgs.python311Packages.pip
        pkgs.graphviz
        # Additional system dependencies
      ];
    }

Health Monitoring
~~~~~~~~~~~~~~~~~

Replit provides built-in monitoring. Additional health checks available at:

* ``/health`` - Basic application health
* ``/healthz`` - Comprehensive system health
* ``/api/v1/health/chat`` - Chat system health

Production Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~

**Environment Variables:**

.. code-block:: bash

    # Automatic Replit variables
    REPL_ID=your-repl-id
    REPL_SLUG=your-repl-slug
    REPLIT_DB_URL=your-database-url
    
    # Application variables
    DATABASE_URL=${REPLIT_DB_URL}
    PORT=5000
    FLASK_ENV=production
    PUBLIC_MODE=true

**Performance Optimization:**

* Database connection pooling configured for Replit
* Static asset serving optimized
* Memory usage monitored via ``/healthz``

Alternative Deployment Options
------------------------------

Heroku Deployment
~~~~~~~~~~~~~~~~~

**Prerequisites:**

* Heroku account and CLI installed
* PostgreSQL add-on

**Setup:**

.. code-block:: bash

    # Create Heroku app
    heroku create your-app-name
    
    # Add PostgreSQL
    heroku addons:create heroku-postgresql:hobby-dev
    
    # Set environment variables
    heroku config:set FLASK_ENV=production
    heroku config:set GOOGLE_CLIENT_ID=your_client_id
    heroku config:set GOOGLE_CLIENT_SECRET=your_client_secret
    
    # Deploy
    git push heroku main

**Procfile:**

.. code-block:: text

    web: gunicorn --bind 0.0.0.0:$PORT main:app

Docker Deployment
~~~~~~~~~~~~~~~~~

**Dockerfile:**

.. code-block:: dockerfile

    FROM python:3.11-slim
    
    # Set working directory
    WORKDIR /app
    
    # Install system dependencies
    RUN apt-get update && apt-get install -y \
        gcc \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy requirements and install Python dependencies
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Copy application code
    COPY . .
    
    # Create non-root user
    RUN adduser --disabled-password --gecos '' appuser
    RUN chown -R appuser:appuser /app
    USER appuser
    
    # Expose port
    EXPOSE 5000
    
    # Health check
    HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
        CMD curl -f http://localhost:5000/health || exit 1
    
    # Start application
    CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "main:app"]

**docker-compose.yml:**

.. code-block:: yaml

    version: '3.8'
    
    services:
      web:
        build: .
        ports:
          - "5000:5000"
        environment:
          - DATABASE_URL=postgresql://postgres:password@db:5432/nous
          - FLASK_ENV=production
          - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
          - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
        depends_on:
          - db
        restart: unless-stopped
    
      db:
        image: postgres:13
        environment:
          - POSTGRES_PASSWORD=password
          - POSTGRES_DB=nous
        volumes:
          - postgres_data:/var/lib/postgresql/data
        restart: unless-stopped
    
    volumes:
      postgres_data:

**Build and Deploy:**

.. code-block:: bash

    # Build image
    docker build -t nous-assistant .
    
    # Run with Docker Compose
    docker-compose up -d
    
    # Check logs
    docker-compose logs -f web

DigitalOcean App Platform
~~~~~~~~~~~~~~~~~~~~~~~~~

**app.yaml:**

.. code-block:: yaml

    name: nous-assistant
    
    services:
    - name: web
      source_dir: /
      github:
        repo: your-username/nous-personal-assistant
        branch: main
      run_command: gunicorn --bind 0.0.0.0:$PORT main:app
      environment_slug: python
      instance_count: 1
      instance_size_slug: basic-xxs
      
      envs:
      - key: FLASK_ENV
        value: production
      - key: GOOGLE_CLIENT_ID
        value: ${GOOGLE_CLIENT_ID}
        type: SECRET
      - key: GOOGLE_CLIENT_SECRET  
        value: ${GOOGLE_CLIENT_SECRET}
        type: SECRET
      
      health_check:
        http_path: /health
    
    databases:
    - name: db
      engine: PG
      version: "13"

AWS Elastic Beanstalk
~~~~~~~~~~~~~~~~~~~~~

**requirements.txt** (must include):

.. code-block:: text

    flask==3.0.0
    gunicorn==21.2.0
    # ... other dependencies

**application.py** (EB entry point):

.. code-block:: python

    from main import app
    
    if __name__ == "__main__":
        app.run()

**.ebextensions/python.config:**

.. code-block:: yaml

    option_settings:
      aws:elasticbeanstalk:container:python:
        WSGIPath: application.py
      aws:elasticbeanstalk:application:environment:
        FLASK_ENV: production

Environment Configuration
-------------------------

Development Environment
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # .env.development
    FLASK_ENV=development
    FLASK_DEBUG=True
    DATABASE_URL=sqlite:///instance/nous.db
    BASE_URL=http://localhost:5000
    PORT=5000

Staging Environment
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # .env.staging
    FLASK_ENV=staging
    FLASK_DEBUG=False
    DATABASE_URL=postgresql://user:pass@staging-db/nous
    BASE_URL=https://staging-nous.example.com
    PORT=5000

Production Environment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # .env.production
    FLASK_ENV=production
    FLASK_DEBUG=False
    DATABASE_URL=${DATABASE_URL}  # Provided by platform
    BASE_URL=https://your-app.replit.app
    PORT=5000
    
    # Security
    SESSION_SECRET=${SESSION_SECRET}  # Strong random key
    
    # OAuth
    GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
    GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
    
    # AI Services
    OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}

SSL/TLS Configuration
---------------------

Replit Cloud (Automatic)
~~~~~~~~~~~~~~~~~~~~~~~~~

* SSL certificates automatically managed
* HTTPS enforced by default
* Custom domains supported with SSL

Manual SSL Setup
~~~~~~~~~~~~~~~~

For self-hosted deployments:

.. code-block:: nginx

    # nginx configuration
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name your-domain.com;
        
        ssl_certificate /path/to/certificate.crt;
        ssl_certificate_key /path/to/private.key;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        
        location / {
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

Database Migration
------------------

PostgreSQL Setup
~~~~~~~~~~~~~~~~~

**For production deployments:**

.. code-block:: bash

    # Create database
    createdb nous_production
    
    # Create user
    createuser --interactive nous_user
    
    # Grant permissions
    psql -c "GRANT ALL PRIVILEGES ON DATABASE nous_production TO nous_user;"

**Connection string:**

.. code-block:: bash

    DATABASE_URL=postgresql://nous_user:password@host:5432/nous_production

Data Migration
~~~~~~~~~~~~~~

.. code-block:: python

    # Migration script
    from app import app, db
    import json
    
    def migrate_data():
        """Migrate data between environments."""
        with app.app_context():
            # Export data
            users = User.query.all()
            user_data = [user.to_dict() for user in users]
            
            with open('user_backup.json', 'w') as f:
                json.dump(user_data, f)
            
            print(f"Exported {len(users)} users")

Monitoring and Logging
----------------------

Application Monitoring
~~~~~~~~~~~~~~~~~~~~~~

**Health Check Endpoints:**

.. code-block:: python

    @app.route('/health')
    def health_check():
        """Basic health check."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @app.route('/healthz')  
    def detailed_health():
        """Comprehensive health check."""
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': check_database_health(),
            'external_services': check_external_services(),
            'system': get_system_metrics()
        }
        
        overall_status = 200
        if any(service['status'] == 'unhealthy' for service in health_data.values()):
            overall_status = 503
            health_data['status'] = 'unhealthy'
            
        return jsonify(health_data), overall_status

Log Management
~~~~~~~~~~~~~~

**Production Logging:**

.. code-block:: python

    import logging
    from logging.handlers import RotatingFileHandler
    
    if not app.debug:
        # File logging
        file_handler = RotatingFileHandler(
            'logs/nous.log', 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('NOUS startup')

Performance Optimization
------------------------

Database Optimization
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Connection pooling
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 5,
        "max_overflow": 15,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }

Caching Strategy
~~~~~~~~~~~~~~~~

.. code-block:: python

    from flask_caching import Cache
    
    # Configure caching
    cache = Cache(app, config={
        'CACHE_TYPE': 'simple',
        'CACHE_DEFAULT_TIMEOUT': 300
    })
    
    @cache.cached(timeout=300)
    def get_feature_flags():
        """Cached feature flag retrieval."""
        return FeatureFlag.query.all()

Static File Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Serve static files efficiently
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory('static', filename, max_age=31536000)

Security Considerations
-----------------------

Production Security Checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ✅ HTTPS enabled with strong SSL configuration
* ✅ Security headers configured (CSP, HSTS, etc.)
* ✅ Database connections encrypted
* ✅ Session cookies secure and HTTP-only
* ✅ CSRF protection enabled
* ✅ Input validation on all endpoints
* ✅ Rate limiting implemented
* ✅ Error messages don't expose sensitive information
* ✅ Regular security updates applied
* ✅ Access logs monitored

Environment Variables Security
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import secrets
    
    # Generate secure session secret
    def generate_secret_key():
        return secrets.token_hex(32)
    
    # Validate required environment variables
    required_vars = [
        'DATABASE_URL',
        'SESSION_SECRET', 
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET'
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Required environment variable {var} not set")

Backup and Recovery
-------------------

Database Backup
~~~~~~~~~~~~~~~

.. code-block:: bash

    #!/bin/bash
    # backup.sh
    
    BACKUP_DIR="/backups"
    DATE=$(date +%Y%m%d_%H%M%S)
    
    # Create backup
    pg_dump $DATABASE_URL > "$BACKUP_DIR/nous_backup_$DATE.sql"
    
    # Compress backup
    gzip "$BACKUP_DIR/nous_backup_$DATE.sql"
    
    # Remove old backups (keep 30 days)
    find $BACKUP_DIR -name "nous_backup_*.sql.gz" -mtime +30 -delete

Application Backup
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import json
    from datetime import datetime
    
    def backup_application_data():
        """Backup critical application data."""
        backup_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'users': [user.to_dict() for user in User.query.all()],
            'feature_flags': [flag.to_dict() for flag in FeatureFlag.query.all()],
            'feedback': [fb.to_dict() for fb in UserFeedback.query.all()]
        }
        
        filename = f"app_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        return filename

Troubleshooting
---------------

Common Deployment Issues
~~~~~~~~~~~~~~~~~~~~~~~~

**Database Connection Errors:**

.. code-block:: bash

    # Check DATABASE_URL format
    echo $DATABASE_URL
    
    # Test connection
    python -c "
    import os
    from sqlalchemy import create_engine
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        print('Database connection successful')
    "

**OAuth Redirect Errors:**

* Verify redirect URI in Google Console matches exactly
* Check BASE_URL environment variable
* Ensure HTTPS is properly configured

**Port Binding Issues:**

.. code-block:: python

    # Ensure proper port configuration
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

**Memory Issues:**

* Monitor memory usage via ``/healthz``
* Optimize database queries
* Implement proper caching

Rollback Strategy
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Git-based rollback
    git log --oneline  # Find previous commit
    git revert <commit-hash>
    git push origin main
    
    # Database rollback (if using migrations)
    flask db downgrade <revision>

This deployment guide provides comprehensive coverage for deploying NOUS Personal Assistant across various platforms, with Replit Cloud being the primary and most streamlined option.