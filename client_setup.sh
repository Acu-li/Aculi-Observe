#!/bin/bash
set -e

# ------------------------------------------------------------------
# Deploy script for Acu.li Observe Client
# Source: https://github.com/Acu-li/Aculi-Observe
# This script installs and configures the server monitoring client.
# ------------------------------------------------------------------

# Define directories
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST_DIR="/opt/aculiobserveclient"

# Create destination and copy application files
sudo mkdir -p "$DEST_DIR"
sudo cp -f "$SCRIPT_DIR/client.py" "$SCRIPT_DIR/client_config.json" "$DEST_DIR"

# Create an info file describing the client
sudo bash -c "cat > $DEST_DIR/INFO.txt" <<EOL
Acu.li Observe Client

This directory contains the server monitoring client from the Aculi-Observe project:
https://github.com/Acu-li/Aculi-Observe

The client runs as a background service to collect metrics and report server status.
EOL

# Update package sources and install pip
sudo apt-get update
sudo apt-get install -y python3-pip

# Install Python dependencies
pip3 install -r "$SCRIPT_DIR/requirements.txt"

# Install or update the systemd service
SERVICE_FILE="/etc/systemd/system/aculiobserveclient.service"
if [ ! -f "$SERVICE_FILE" ]; then
  sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Acu.li Observe Client
After=network.target

[Service]
Type=simple
WorkingDirectory=$DEST_DIR
ExecStart=/usr/bin/python3 $DEST_DIR/client.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL
  sudo systemctl daemon-reload
  sudo systemctl enable aculiobserveclient.service
fi

# Restart the service to apply any changes
sudo systemctl restart aculiobserveclient.service

# ------------------------------------------------------------------
# Report summary of actions performed
# ------------------------------------------------------------------
echo "Deployment Summary:"
echo "- Worked directory: $SCRIPT_DIR"
echo "- Files copied to: $DEST_DIR"
echo "- INFO.txt created"
echo "- Python dependencies installed via requirements.txt"
echo "- Systemd service 'aculiobserveclient' installed/enabled"
echo "- Service 'aculiobserveclient' restarted"
