#!/bin/bash

# NOUS Personal Assistant - Deployment Health Checker
# This script monitors the health of the application and restarts it if needed

LOG_FILE="logs/health_monitor.log"
HEALTH_URL="http://localhost:8080/health"
CHECK_INTERVAL=60  # Check every 60 seconds
MAX_FAILURES=3     # Max consecutive failures before restarting

mkdir -p logs

log_message() {
  echo "$(date): $1" >> "$LOG_FILE"
  echo "$1"
}

log_message "Starting NOUS health monitoring script"

# Counter for consecutive failures
failures=0

while true; do
  # Check if the health endpoint is accessible
  health_check=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")
  
  if [ "$health_check" = "200" ]; then
    # Service is responding
    if [ $failures -gt 0 ]; then
      log_message "Service recovered after $failures failures"
    fi
    failures=0
    
    # Check the actual health status from the JSON response
    health_status=$(curl -s "$HEALTH_URL" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$health_status" = "error" ]; then
      log_message "WARNING: Service returned error status, monitoring closely"
    elif [ "$health_status" = "warning" ]; then
      log_message "NOTICE: Service returned warning status"
    fi
  else
    # Service is not responding
    failures=$((failures + 1))
    log_message "WARNING: Health check failed (HTTP $health_check), failure count: $failures"
    
    if [ $failures -ge $MAX_FAILURES ]; then
      log_message "CRITICAL: $MAX_FAILURES consecutive failures, attempting restart"
      
      # Kill any existing processes
      pkill -f "python.*app.py" || true
      pkill -f "gunicorn.*app:app" || true
      
      # Wait a moment
      sleep 5
      
      # Start the service again
      log_message "Restarting service..."
      nohup bash public_start.sh > logs/restart.log 2>&1 &
      
      # Reset failure counter
      failures=0
      
      # Wait a bit longer before checking again to allow startup
      sleep 30
    fi
  fi
  
  # Wait before checking again
  sleep $CHECK_INTERVAL
done