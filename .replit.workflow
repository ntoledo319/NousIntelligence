[deployment]
deploymentTarget = "cloudrun"
run = ["sh", "-c", "python app.py"]

[deployment.cloudrun]
memory = "512Mi"
cpu = "1"
concurrency = 80
maxRequests = 10000

[nix]
channel = "stable-23_11"

[[ports]]
localPort = 8080
externalPort = 8080

[env]
PORT = "8080"
FLASK_ENV = "production"
PYTHONUNBUFFERED = "1"

[workflows.nous]
name = "NOUS App"
run = ["sh", "-c", "python app.py"]