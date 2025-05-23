#!/bin/bash
# NOUS Personal Assistant - Health Check Script
# This script checks if the application is running and restarts it if needed

# Log file setup
TIMESTAMP=$(date +%Y%m%d)
LOG_FILE="logs/deployment_${TIMESTAMP}.log"
mkdir -p logs

log_message() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
  echo "$1"
}

log_message "INFO: Running health check"

# Check if the application is running on the configured port
PORT=${PORT:-8080}
if ! curl -s http://localhost:$PORT/health > /dev/null; then
  log_message "WARNING: Health check failed, attempting restart"
  
  # Kill any existing processes on the port
  fuser -k $PORT/tcp 2>/dev/null || true
  
  # Wait for processes to terminate
  sleep 2
  
  # Start the application
  log_message "INFO: Restarting application"
  ./deploy.sh &
  
  # Wait for application to start
  sleep 5
  
  # Verify it's running
  if curl -s http://localhost:$PORT/health > /dev/null; then
    log_message "INFO: Application successfully restarted"
  else
    log_message "ERROR: Failed to restart application"
  fi
else
  log_message "INFO: Health check passed"
fi

# Check disk space
DISK_SPACE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_SPACE" -gt 90 ]; then
  log_message "WARNING: Disk space critically low: ${DISK_SPACE}%"
  
  # Clean up old log files
  find logs -name "deployment_*.log" -type f -mtime +7 -delete
  find flask_session -type f -mtime +7 -delete
fi