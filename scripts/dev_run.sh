#!/usr/bin/env bash
set -euo pipefail
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
python -m flask run --host 127.0.0.1 --port 5000

