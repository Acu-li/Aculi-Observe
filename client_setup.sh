#!/bin/bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

sudo apt-get update
sudo apt-get install -y python3-pip
pip3 install -r "$DIR/requirements.txt"

SERVICE_FILE="/etc/systemd/system/aculiclient.service"
if [ ! -f "$SERVICE_FILE" ]; then
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Acu.li client
After=network.target

[Service]
Type=simple
WorkingDirectory=$DIR
ExecStart=/usr/bin/python3 $DIR/client.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL
sudo systemctl daemon-reload
sudo systemctl enable aculiclient.service
fi
sudo systemctl restart aculiclient.service
