run = ["bash", "-c", "python app.py"]
language = "python3"
entrypoint = "app.py"
hidden = ["__pycache__", "*.pyc", "instance", "flask_session"]
onBoot = []

[languages.python3]
pattern = "**/*.py"
syntax = "python"

[env]
PORT = "8080"
FLASK_APP = "app.py"
FLASK_ENV = "development"  # Use development for testing
PYTHONPATH = "${PYTHONPATH}:${REPL_HOME}"
PYTHONUNBUFFERED = "1"

[nix]
channel = "stable-24_05"

[deployment]
deploymentTarget = "cloudrun"
run = ["sh", "-c", "bash public_start.sh"]
buildCommand = "pip install -r requirements.txt"