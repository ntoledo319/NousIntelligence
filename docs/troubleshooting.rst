Troubleshooting Guide
====================

This guide provides solutions to common issues encountered when deploying, configuring, and using NOUS Personal Assistant.

Common Issues and Solutions
---------------------------

Authentication Problems
~~~~~~~~~~~~~~~~~~~~~~~

**Issue: "OAuth redirect URI mismatch"**

This error occurs when the redirect URI configured in Google Console doesn't match the application's callback URL.

*Solution:*

1. Check your Google Cloud Console OAuth configuration
2. Ensure redirect URIs match exactly:
   
   .. code-block:: text
   
       Development: http://localhost:5000/oauth/callback
       Production: https://your-app.replit.app/oauth/callback

3. Verify BASE_URL environment variable:
   
   .. code-block:: bash
   
       # Check current setting
       echo $BASE_URL
       
       # Should match your domain
       BASE_URL=https://your-app.replit.app

**Issue: "Authentication loop - keeps redirecting to login"**

*Solution:*

1. Check session configuration:
   
   .. code-block:: python
   
       # Verify session secret is set
       import os
       print(os.getenv('SESSION_SECRET'))

2. Clear browser cookies and cache

3. Verify ProxyFix middleware configuration:
   
   .. code-block:: python
   
       from werkzeug.middleware.proxy_fix import ProxyFix
       app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

**Issue: "Google OAuth client not found"**

*Solution:*

1. Verify client secrets are properly configured:
   
   .. code-block:: bash
   
       # Check if client_secret.json exists
       ls -la client_secret.json
       
       # Or check environment variables
       echo $GOOGLE_CLIENT_ID
       echo $GOOGLE_CLIENT_SECRET

2. Regenerate OAuth credentials if necessary

Database Issues
~~~~~~~~~~~~~~~

**Issue: "Database connection failed"**

*Symptoms:* Application crashes on startup, "SQLAlchemy connection error"

*Solution:*

1. Check DATABASE_URL format:
   
   .. code-block:: bash
   
       # Correct format
       DATABASE_URL=postgresql://user:password@host:port/database
       
       # For Replit (automatic)
       DATABASE_URL=${REPLIT_DB_URL}

2. Test database connection:
   
   .. code-block:: python
   
       from sqlalchemy import create_engine
       import os
       
       try:
           engine = create_engine(os.getenv('DATABASE_URL'))
           with engine.connect() as conn:
               result = conn.execute('SELECT 1').scalar()
               print(f"Database connection successful: {result}")
       except Exception as e:
           print(f"Database connection failed: {e}")

3. For Replit, ensure PostgreSQL is enabled in the project

**Issue: "Table doesn't exist" errors**

*Solution:*

1. Initialize database tables:
   
   .. code-block:: bash
   
       python -c "from app import app, db; app.app_context().push(); db.create_all()"

2. Check model imports in app.py:
   
   .. code-block:: python
   
       # Ensure all models are imported
       import models  # This should import all model files

**Issue: "Connection pool exhausted"**

*Solution:*

1. Optimize connection pool settings:
   
   .. code-block:: python
   
       app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
           "pool_size": 2,           # Reduce for resource-constrained environments
           "max_overflow": 5,        # Lower overflow limit
           "pool_recycle": 1800,     # Recycle connections more frequently
           "pool_pre_ping": True     # Validate connections
       }

2. Close database connections properly:
   
   .. code-block:: python
   
       try:
           result = db.session.query(User).all()
       finally:
           db.session.close()

AI Service Issues
~~~~~~~~~~~~~~~~~

**Issue: "OpenRouter API key invalid"**

*Solution:*

1. Verify API key is correct:
   
   .. code-block:: bash
   
       # Test API key
       curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
            https://openrouter.ai/api/v1/models

2. Check if key has expired or needs renewal

3. Test with fallback provider (HuggingFace)

**Issue: "AI response timeout"**

*Solution:*

1. Increase timeout settings:
   
   .. code-block:: python
   
       import requests
       
       response = requests.post(
           url,
           json=data,
           timeout=60  # Increase from default 30s
       )

2. Implement retry logic:
   
   .. code-block:: python
   
       import time
       from functools import wraps
       
       def retry_on_failure(retries=3, delay=1):
           def decorator(func):
               @wraps(func)
               def wrapper(*args, **kwargs):
                   for attempt in range(retries):
                       try:
                           return func(*args, **kwargs)
                       except Exception as e:
                           if attempt == retries - 1:
                               raise e
                           time.sleep(delay * (2 ** attempt))
               return wrapper
           return decorator

**Issue: "HuggingFace inference API rate limited"**

*Solution:*

1. Implement request queuing:
   
   .. code-block:: python
   
       import asyncio
       from asyncio import Semaphore
       
       # Limit concurrent requests
       semaphore = Semaphore(2)
       
       async def limited_api_call(data):
           async with semaphore:
               return await make_api_call(data)

2. Add authentication token for higher limits:
   
   .. code-block:: bash
   
       HUGGINGFACE_API_KEY=your_token_here

Deployment Issues
~~~~~~~~~~~~~~~~~

**Issue: "Application won't start on Replit"**

*Symptoms:* Replit shows "Application not responding"

*Solution:*

1. Check run configuration in replit.toml:
   
   .. code-block:: toml
   
       run = ["python3", "main.py"]

2. Verify main.py launches the app:
   
   .. code-block:: python
   
       from app import app
       
       if __name__ == "__main__":
           app.run(host="0.0.0.0", port=5000)

3. Check application logs in Replit console

**Issue: "Port already in use"**

*Solution:*

1. Use environment-specified port:
   
   .. code-block:: python
   
       import os
       port = int(os.environ.get('PORT', 5000))
       app.run(host='0.0.0.0', port=port)

2. Kill existing processes:
   
   .. code-block:: bash
   
       # Find process using port
       lsof -i :5000
       
       # Kill process
       kill -9 <PID>

**Issue: "Static files not loading"**

*Solution:*

1. Verify static file configuration:
   
   .. code-block:: python
   
       app = Flask(__name__, static_folder='static', static_url_path='/static')

2. Check file permissions:
   
   .. code-block:: bash
   
       ls -la static/
       chmod 644 static/*.css static/*.js

3. Clear browser cache

Performance Issues
~~~~~~~~~~~~~~~~~~

**Issue: "Slow database queries"**

*Solution:*

1. Add database indexes:
   
   .. code-block:: python
   
       # In model definitions
       class User(db.Model):
           email = db.Column(db.String(255), index=True)
           created_at = db.Column(db.DateTime, index=True)

2. Optimize queries with eager loading:
   
   .. code-block:: python
   
       # Instead of N+1 queries
       users = User.query.options(
           db.joinedload(User.feedback)
       ).all()

3. Use query profiling:
   
   .. code-block:: python
   
       import time
       
       start_time = time.time()
       result = db.session.query(User).all()
       duration = time.time() - start_time
       
       if duration > 0.1:
           print(f"Slow query detected: {duration:.3f}s")

**Issue: "High memory usage"**

*Solution:*

1. Monitor memory usage:
   
   .. code-block:: python
   
       import psutil
       
       process = psutil.Process()
       memory_mb = process.memory_info().rss / 1024 / 1024
       print(f"Memory usage: {memory_mb:.1f} MB")

2. Implement pagination:
   
   .. code-block:: python
   
       def get_users_paginated(page=1, per_page=20):
           return User.query.paginate(
               page=page,
               per_page=per_page,
               error_out=False
           )

3. Use connection pooling and close sessions:
   
   .. code-block:: python
   
       try:
           # Database operations
           pass
       finally:
           db.session.close()

SSL/TLS Issues
~~~~~~~~~~~~~~

**Issue: "Mixed content warnings"**

*Solution:*

1. Ensure all resources use HTTPS:
   
   .. code-block:: html
   
       <!-- Good -->
       <script src="https://cdn.example.com/script.js"></script>
       
       <!-- Bad in HTTPS context -->
       <script src="http://cdn.example.com/script.js"></script>

2. Use protocol-relative URLs:
   
   .. code-block:: html
   
       <script src="//cdn.example.com/script.js"></script>

**Issue: "SSL certificate errors"**

*Solution:*

1. For Replit: SSL is automatic, check domain configuration

2. For custom domains, verify certificate installation:
   
   .. code-block:: bash
   
       # Check certificate
       openssl s_client -connect your-domain.com:443 -servername your-domain.com

Frontend Issues
~~~~~~~~~~~~~~~

**Issue: "JavaScript errors in console"**

*Solution:*

1. Check for CSRF token issues:
   
   .. code-block:: javascript
   
       // Ensure CSRF token is included
       const csrfToken = document.querySelector('meta[name=csrf-token]')?.getAttribute('content');
       
       fetch('/api/endpoint', {
           method: 'POST',
           headers: {
               'Content-Type': 'application/json',
               'X-CSRFToken': csrfToken
           },
           body: JSON.stringify(data)
       });

2. Fix CORS issues:
   
   .. code-block:: python
   
       @app.after_request
       def after_request(response):
           response.headers.add('Access-Control-Allow-Origin', '*')
           response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
           response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
           return response

**Issue: "Chat interface not responding"**

*Solution:*

1. Check API endpoint connectivity:
   
   .. code-block:: javascript
   
       // Test API endpoint
       fetch('/api/v1/health')
           .then(response => response.json())
           .then(data => console.log('API Status:', data))
           .catch(error => console.error('API Error:', error));

2. Verify WebSocket connections (if used):
   
   .. code-block:: javascript
   
       const ws = new WebSocket('wss://your-domain.com/ws');
       ws.onopen = () => console.log('WebSocket connected');
       ws.onerror = (error) => console.error('WebSocket error:', error);

Debugging Tools and Techniques
------------------------------

Logging Configuration
~~~~~~~~~~~~~~~~~~~~~

Enable comprehensive logging:

.. code-block:: python

    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('debug.log'),
            logging.StreamHandler()
        ]
    )
    
    # Log database queries
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

Health Check Diagnostics
~~~~~~~~~~~~~~~~~~~~~~~~~

Use built-in health endpoints:

.. code-block:: bash

    # Basic health check
    curl https://your-app.replit.app/health
    
    # Comprehensive health check
    curl https://your-app.replit.app/healthz
    
    # Chat system health
    curl https://your-app.replit.app/api/v1/health/chat

Database Diagnostics
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Check database connectivity
    def diagnose_database():
        try:
            # Test basic connection
            result = db.session.execute('SELECT 1').scalar()
            print(f"✅ Database connection: OK ({result})")
            
            # Check table existence
            tables = db.inspect(db.engine).get_table_names()
            print(f"✅ Tables found: {len(tables)}")
            
            # Check user count
            user_count = User.query.count()
            print(f"✅ Users in database: {user_count}")
            
        except Exception as e:
            print(f"❌ Database error: {e}")

API Diagnostics
~~~~~~~~~~~~~~~

.. code-block:: python

    # Test external API connections
    def diagnose_apis():
        apis = {
            'OpenRouter': 'https://openrouter.ai/api/v1/models',
            'HuggingFace': 'https://huggingface.co/api/models'
        }
        
        for name, url in apis.items():
            try:
                response = requests.get(url, timeout=10)
                print(f"✅ {name}: {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: {e}")

Performance Monitoring
----------------------

Real-time Monitoring
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import psutil
    import time
    
    def monitor_performance():
        """Monitor system performance metrics."""
        while True:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Database connections
            db_pool = db.engine.pool
            pool_size = db_pool.size()
            checked_out = db_pool.checkedout()
            
            print(f"CPU: {cpu_percent}% | Memory: {memory_percent}% | DB Pool: {checked_out}/{pool_size}")
            
            time.sleep(5)

Query Performance Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    import time
    
    # Log slow queries
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = time.time()
    
    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - context._query_start_time
        if total > 0.1:  # Log queries slower than 100ms
            logger.warning(f"Slow query: {total:.3f}s - {statement[:100]}...")

Error Recovery Procedures
-------------------------

Application Recovery
~~~~~~~~~~~~~~~~~~~~

If the application becomes unresponsive:

1. **Restart Application**
   
   .. code-block:: bash
   
       # On Replit: Click stop/start
       # On other platforms: restart service
       sudo systemctl restart your-app

2. **Clear Sessions**
   
   .. code-block:: python
   
       # Clear session files
       import os
       import glob
       
       session_files = glob.glob('flask_session/*')
       for file in session_files:
           os.remove(file)

3. **Reset Database Connections**
   
   .. code-block:: python
   
       # Reset connection pool
       db.engine.dispose()

Database Recovery
~~~~~~~~~~~~~~~~~

For database issues:

1. **Connection Pool Reset**
   
   .. code-block:: python
   
       from app import db
       db.engine.dispose()

2. **Table Recreation** (Development only)
   
   .. code-block:: python
   
       from app import app, db
       with app.app_context():
           db.drop_all()
           db.create_all()

3. **Backup Restoration**
   
   .. code-block:: bash
   
       # Restore from backup
       psql $DATABASE_URL < backup.sql

Emergency Contacts and Resources
---------------------------------

Support Channels
~~~~~~~~~~~~~~~~

* **Replit Support**: For platform-specific issues
* **Google Cloud Support**: For OAuth and API issues
* **PostgreSQL Community**: For database-related problems

Documentation Resources
~~~~~~~~~~~~~~~~~~~~~~~

* **Flask Documentation**: https://flask.palletsprojects.com/
* **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
* **Replit Documentation**: https://docs.replit.com/

Logs and Monitoring
~~~~~~~~~~~~~~~~~~~

Key log files to check:

* Application logs: ``logs/app.log``
* Error logs: ``logs/error.log``
* Access logs: ``logs/access.log``
* Database logs: Check PostgreSQL logs

Health check URLs:

* ``/health`` - Basic status
* ``/healthz`` - Comprehensive health
* ``/api/v1/health/chat`` - Chat system status

This troubleshooting guide covers the most common issues encountered with NOUS Personal Assistant. For issues not covered here, check the application logs and health endpoints for additional diagnostic information.