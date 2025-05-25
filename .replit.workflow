[nix]
channel = "stable-23_11"

[deployment]
run = ["python", "run_nous.py"]
deploymentTarget = "cloudrun"

[languages]

[languages.python3]
pattern = "**/*.py"

[languages.python3.languageServer]
start = ["pylsp"]

[[ports]]
localPort = 8080
externalPort = 80