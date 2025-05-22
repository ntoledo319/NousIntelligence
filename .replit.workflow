# Replit Workflow Configuration
workflow = "nous"
entrypoint = "wsgi.py"
run = "gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 120 wsgi:app"
language = "python3"
hidden = ["__pycache__", "*.pyc", "venv", ".pytest_cache"]
onBoot = ["bash", "-c", "mkdir -p logs"]