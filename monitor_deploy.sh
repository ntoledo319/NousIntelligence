#!/bin/bash
# NOUS Personal Assistant - Deployment Monitoring Script
# This script checks if the application is running and restarts it if needed

# Log file setup
TIMESTAMP=$(date +%Y%m%d)
LOG_FILE="logs/deployment_${TIMESTAMP}.log"
mkdir -p logs

log_message() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
  echo "$1"
}

log_message "INFO in monitor: [MONITOR] Running deployment health check"

# Check if the application is running
if ! curl -s http://localhost:8080/health > /dev/null; then
  log_message "WARNING in monitor: [MONITOR] Application health check failed, attempting restart"
  
  # Kill any existing processes
  pkill -f "python.*main.py" 2>/dev/null || true
  pkill -f "gunicorn" 2>/dev/null || true
  fuser -k 8080/tcp 2>/dev/null || true
  
  # Wait for processes to terminate
  sleep 2
  
  # Start the application
  log_message "INFO in monitor: [MONITOR] Restarting application"
  ./public_start.sh &
  
  # Wait for application to start
  sleep 5
  
  # Verify it's running
  if curl -s http://localhost:8080/health > /dev/null; then
    log_message "INFO in monitor: [MONITOR] Application successfully restarted"
  else
    log_message "ERROR in monitor: [MONITOR] Failed to restart application"
  fi
else
  log_message "INFO in monitor: [MONITOR] Application health check passed"
fi

# Check if we have enough disk space
DISK_SPACE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_SPACE" -gt 90 ]; then
  log_message "WARNING in monitor: [MONITOR] Disk space critically low: ${DISK_SPACE}%"
  
  # Clean up old log files if needed
  find logs -name "deployment_*.log" -type f -mtime +7 -delete
  find flask_session -type f -mtime +7 -delete
fi

# Check for memory usage
MEM_USAGE=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
log_message "INFO in monitor: [MONITOR] Memory usage: $MEM_USAGE"

log_message "INFO in monitor: [MONITOR] Deployment monitoring completed"