Installation Guide
==================

This guide provides comprehensive instructions for setting up NOUS Personal Assistant in various environments, with a focus on Replit Cloud deployment.

Quick Start (Replit)
--------------------

NOUS is optimized for one-click deployment on Replit:

1. **Fork or Import**: Import the repository into your Replit workspace
2. **Environment Setup**: Replit automatically installs dependencies via ``replit.nix``
3. **Configure Secrets**: Add required API keys through Replit's Secrets tab
4. **Run Application**: Click the Run button or execute ``python main.py``
5. **Access Application**: Open the generated Replit URL

Required Secrets
~~~~~~~~~~~~~~~~

Configure these secrets in Replit's Secrets tab:

.. code-block:: bash

    # Google OAuth (Required)
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    
    # Session Security (Auto-generated if not provided)
    SESSION_SECRET=your_random_secret_key
    
    # AI Services (Optional - fallbacks available)
    OPENROUTER_API_KEY=your_openrouter_key
    HUGGINGFACE_API_KEY=your_huggingface_key
    
    # Database (Automatically provided by Replit)
    DATABASE_URL=postgresql://... # Auto-configured

Local Development Setup
-----------------------

Prerequisites
~~~~~~~~~~~~~

* Python 3.11 or higher
* PostgreSQL 13+ (or SQLite for development)
* Git
* Node.js 18+ (for documentation building)

Installation Steps
~~~~~~~~~~~~~~~~~~

1. **Clone Repository**

   .. code-block:: bash

       git clone https://github.com/your-username/nous-personal-assistant.git
       cd nous-personal-assistant

2. **Create Virtual Environment**

   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Dependencies**

   .. code-block:: bash

       pip install -r requirements.txt
       pip install -r requirements_dev.txt

4. **Environment Configuration**

   .. code-block:: bash

       cp .env.example .env
       # Edit .env with your configuration

5. **Database Setup**

   .. code-block:: bash

       # For PostgreSQL
       createdb nous_development
       export DATABASE_URL=postgresql://user:pass@localhost/nous_development
       
       # For SQLite (development only)
       export DATABASE_URL=sqlite:///instance/nous.db

6. **Initialize Database**

   .. code-block:: bash

       python -c "from app import app, db; app.app_context().push(); db.create_all()"

7. **Run Application**

   .. code-block:: bash

       python main.py

Environment Configuration
-------------------------

Development Environment
~~~~~~~~~~~~~~~~~~~~~~~

Create a ``.env`` file in the project root:

.. code-block:: bash

    # Flask Configuration
    FLASK_ENV=development
    FLASK_DEBUG=True
    PORT=5000
    
    # Database
    DATABASE_URL=sqlite:///instance/nous.db
    
    # Session Security
    SESSION_SECRET=dev-secret-key-change-in-production
    
    # Google OAuth
    GOOGLE_CLIENT_ID=your_development_client_id
    GOOGLE_CLIENT_SECRET=your_development_client_secret
    
    # AI Services (Optional)
    OPENROUTER_API_KEY=your_key_here
    HUGGINGFACE_API_KEY=your_key_here
    
    # Application Settings
    PUBLIC_MODE=true
    BASE_URL=http://localhost:5000
    API_BASE_PATH=/api/v1

Production Environment
~~~~~~~~~~~~~~~~~~~~~~

Production configuration (typically via environment variables):

.. code-block:: bash

    # Flask Configuration
    FLASK_ENV=production
    FLASK_DEBUG=False
    PORT=5000
    
    # Database (Required)
    DATABASE_URL=postgresql://user:password@host:port/database
    
    # Session Security (Required)
    SESSION_SECRET=secure-random-secret-key
    
    # Google OAuth (Required)
    GOOGLE_CLIENT_ID=production_client_id
    GOOGLE_CLIENT_SECRET=production_client_secret
    
    # AI Services
    OPENROUTER_API_KEY=production_key
    HUGGINGFACE_API_KEY=production_key
    
    # Application Settings
    PUBLIC_MODE=true
    BASE_URL=https://your-app.replit.app
    API_BASE_PATH=/api/v1

Google OAuth Setup
------------------

Creating OAuth Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Google Cloud Console**
   
   - Visit `Google Cloud Console <https://console.cloud.google.com/>`_
   - Create a new project or select existing one
   - Navigate to "APIs & Services" → "Credentials"

2. **Enable Google+ API**
   
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click "Enable"

3. **Create OAuth Client**
   
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     
     - Development: ``http://localhost:5000/oauth/callback``
     - Production: ``https://your-app.replit.app/oauth/callback``

4. **Configure Client**
   
   - Copy Client ID and Client Secret
   - Add to your environment configuration

OAuth Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, download the OAuth configuration JSON:

.. code-block:: bash

    # Save as client_secret.json in project root
    {
      "web": {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost:5000/oauth/callback"]
      }
    }

Database Configuration
----------------------

PostgreSQL Setup
~~~~~~~~~~~~~~~~~

**Using Docker:**

.. code-block:: bash

    docker run --name nous-postgres \
      -e POSTGRES_PASSWORD=password \
      -e POSTGRES_DB=nous_development \
      -p 5432:5432 \
      -d postgres:13

**Manual Installation:**

.. code-block:: bash

    # Ubuntu/Debian
    sudo apt-get install postgresql postgresql-contrib
    
    # macOS
    brew install postgresql
    
    # Create database
    createuser --interactive nous_user
    createdb -O nous_user nous_development

**Connection String:**

.. code-block:: bash

    DATABASE_URL=postgresql://nous_user:password@localhost:5432/nous_development

SQLite Setup (Development)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

SQLite requires no additional setup:

.. code-block:: bash

    DATABASE_URL=sqlite:///instance/nous.db

The application will automatically create the database file and tables.

AI Service Configuration
------------------------

OpenRouter Setup
~~~~~~~~~~~~~~~~~

1. **Create Account**: Visit `OpenRouter <https://openrouter.ai/>`_
2. **Generate API Key**: Go to Settings → API Keys
3. **Add to Environment**: ``OPENROUTER_API_KEY=your_key_here``

Supported models:
* ``google/gemini-pro`` (Primary)
* ``anthropic/claude-3-haiku``
* ``meta-llama/llama-3-8b-instruct``

HuggingFace Setup
~~~~~~~~~~~~~~~~~

1. **Create Account**: Visit `HuggingFace <https://huggingface.co/>`_
2. **Generate Token**: Settings → Access Tokens
3. **Add to Environment**: ``HUGGINGFACE_API_KEY=your_token_here``

Free tier includes:
* Text-to-Speech
* Speech-to-Text  
* Image Classification
* Sentiment Analysis

Development Tools
-----------------

Code Quality Tools
~~~~~~~~~~~~~~~~~~

Install development dependencies:

.. code-block:: bash

    pip install -r requirements_dev.txt

Available tools:

.. code-block:: bash

    # Code formatting
    black .
    
    # Linting
    flake8 .
    
    # Security scanning
    bandit -r .
    
    # Type checking
    mypy .

Documentation Building
~~~~~~~~~~~~~~~~~~~~~~

Build documentation locally:

.. code-block:: bash

    # Install Sphinx dependencies
    pip install sphinx sphinx-rtd-theme
    
    # Build HTML documentation
    cd docs
    make html
    
    # Serve documentation
    cd _build/html
    python -m http.server 8000

Testing Setup
~~~~~~~~~~~~~

Run the test suite:

.. code-block:: bash

    # Run all tests
    pytest
    
    # Run with coverage
    pytest --cov=.
    
    # Run specific test file
    pytest tests/test_app.py

Docker Deployment
-----------------

Dockerfile
~~~~~~~~~~

.. code-block:: dockerfile

    FROM python:3.11-slim

    WORKDIR /app
    
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    COPY . .
    
    EXPOSE 5000
    
    CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]

Docker Compose
~~~~~~~~~~~~~~

.. code-block:: yaml

    version: '3.8'
    
    services:
      web:
        build: .
        ports:
          - "5000:5000"
        environment:
          - DATABASE_URL=postgresql://postgres:password@db:5432/nous
          - SESSION_SECRET=your-secret-here
        depends_on:
          - db
    
      db:
        image: postgres:13
        environment:
          - POSTGRES_PASSWORD=password
          - POSTGRES_DB=nous
        volumes:
          - postgres_data:/var/lib/postgresql/data
    
    volumes:
      postgres_data:

Build and run:

.. code-block:: bash

    docker-compose up --build

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import Errors**

.. code-block:: bash

    # Ensure virtual environment is activated
    source venv/bin/activate
    
    # Reinstall dependencies
    pip install --force-reinstall -r requirements.txt

**Database Connection Errors**

.. code-block:: bash

    # Check DATABASE_URL format
    echo $DATABASE_URL
    
    # Test database connection
    python -c "from app import db; print(db.engine.execute('SELECT 1').scalar())"

**OAuth Redirect Errors**

* Verify redirect URI matches exactly in Google Console
* Check that BASE_URL environment variable is correct
* Ensure OAuth client is configured for correct domain

**Port Conflicts**

.. code-block:: bash

    # Check what's using port 5000
    lsof -i :5000
    
    # Use different port
    export PORT=8000
    python main.py

Getting Help
~~~~~~~~~~~~

* **Documentation**: Full documentation at ``/docs``
* **Health Checks**: Monitor system status at ``/healthz``
* **Logs**: Check application logs for detailed error information
* **GitHub Issues**: Report bugs and request features

Performance Optimization
------------------------

Production Recommendations
~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Use PostgreSQL**: SQLite is for development only
* **Enable Connection Pooling**: Configured automatically
* **Set Proper Worker Count**: 2-4 workers for most deployments
* **Configure Caching**: Consider Redis for session storage
* **Monitor Resource Usage**: Use ``/healthz`` endpoint

Security Checklist
~~~~~~~~~~~~~~~~~~~

* ✅ Use HTTPS in production
* ✅ Set secure session secret
* ✅ Configure proper CORS headers
* ✅ Enable security headers
* ✅ Use environment variables for secrets
* ✅ Regular dependency updates
* ✅ Monitor access logs

This installation guide covers all major deployment scenarios. For Replit deployment, the process is significantly simplified due to the platform's automatic dependency management and environment configuration.