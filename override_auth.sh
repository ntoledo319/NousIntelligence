#!/bin/bash

# NOUS Personal Assistant - Authentication Override Script
# This script directly modifies the necessary configuration files to ensure public access

echo "======= NOUS Authentication Override ======="
echo "Starting at $(date)"

# Create log file
mkdir -p logs
LOGFILE="logs/auth_override_$(date +%Y%m%d).log"
echo "Auth override started at $(date)" > "$LOGFILE"

# Create the override file that disables authentication
echo "Creating authentication override..."
cat > .replit.auth << EOF
[auth]
pageEnabled = false
buttonEnabled = false
EOF
echo "$(date): Auth override file created" >> "$LOGFILE"

# Apply the override to the main configuration
if [ -f ".replit" ]; then
  echo "Backing up existing .replit file..."
  cp .replit .replit.backup
  echo "$(date): Backed up .replit" >> "$LOGFILE"
  
  # Check if auth section already exists
  if grep -q "\[auth\]" .replit; then
    echo "Updating existing auth section..."
    sed -i '/\[auth\]/,/^$/c\[auth\]\npageEnabled = false\nbuttonEnabled = false\n' .replit
  else
    echo "Adding auth section..."
    echo "" >> .replit
    echo "[auth]" >> .replit
    echo "pageEnabled = false" >> .replit
    echo "buttonEnabled = false" >> .replit
  fi
  echo "$(date): Updated .replit with auth settings" >> "$LOGFILE"
else
  echo "Creating minimal .replit file with auth settings..."
  cat > .replit << EOF
run = ["bash", "deploy.sh"]

[auth]
pageEnabled = false
buttonEnabled = false
EOF
  echo "$(date): Created new .replit with auth settings" >> "$LOGFILE"
fi

# Also create a deployment-specific version
if [ -f "replit.toml" ]; then
  echo "Updating replit.toml..."
  cp replit.toml replit.toml.backup
  echo "$(date): Backed up replit.toml" >> "$LOGFILE"
  
  # Check if auth section already exists
  if grep -q "\[auth\]" replit.toml; then
    echo "Updating existing auth section in replit.toml..."
    sed -i '/\[auth\]/,/^$/c\[auth\]\npageEnabled = false\nbuttonEnabled = false\n' replit.toml
  else
    echo "Adding auth section to replit.toml..."
    echo "" >> replit.toml
    echo "[auth]" >> replit.toml
    echo "pageEnabled = false" >> replit.toml
    echo "buttonEnabled = false" >> replit.toml
  fi
  echo "$(date): Updated replit.toml with auth settings" >> "$LOGFILE"
fi

echo "Authentication override complete. Your app should now be publicly accessible."
echo "$(date): Auth override completed" >> "$LOGFILE"

# Run the standard deployment script if it exists
if [ -f "deploy.sh" ]; then
  echo "Running standard deployment script..."
  bash deploy.sh
  echo "$(date): Ran deploy.sh" >> "$LOGFILE"
fi