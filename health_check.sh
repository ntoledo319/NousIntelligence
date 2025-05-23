#!/bin/bash

# Simple health check script for NOUS application
LOG_FILE="logs/health_check_$(date +%Y%m%d).log"

log_message() {
  echo "$(date +'[%Y-%m-%d %H:%M:%S]') $1" | tee -a "$LOG_FILE"
}

log_message "Running health check"

# Check if application is running
PORT=${PORT:-8080}
if curl -s http://localhost:$PORT/health > /dev/null; then
  log_message "Health check passed"
  exit 0
else
  log_message "Health check failed - attempting restart"
  pkill -f "gunicorn" || true
  ./public_start.sh &
  sleep 3
  if curl -s http://localhost:$PORT/health > /dev/null; then
    log_message "Application successfully restarted"
    exit 0
  else
    log_message "Failed to restart application"
    exit 1
  fi
fi