[nix]
channel = "stable-24_05"

[deployment]
run = "bash public_start.sh"
deploymentTarget = "cloudrun"
ignorePorts = false

[[ports]]
localPort = 8080
externalPort = 80

[env]
PORT = "8080"
FLASK_APP = "main.py"
FLASK_ENV = "production"
PYTHONUNBUFFERED = "1"