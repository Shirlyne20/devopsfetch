#!/bin/bash

# Installation script for devopsfetch

# Update package list and install dependencies
sudo apt update
sudo apt install -y python3 python3-pip apt-transport-https ca-certificates curl software-properties-common nginx

# Install psutil and tabulate using pip
pip3 install psutil tabulate

# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install -y docker-ce

# Copy devopsfetch.py to /usr/local/bin
sudo cp devopsfetch.py /usr/local/bin/devopsfetch
sudo chmod +x /usr/local/bin/devopsfetch

# Create a systemd service
sudo bash -c 'cat <<EOT > /etc/systemd/system/devopsfetch.service
[Unit]
Description=DevOpsFetch Service
After=network.target

[Service]
ExecStart=/usr/local/bin/devopsfetch
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOT'

# Reload systemd and start the service
sudo systemctl daemon-reload
sudo systemctl enable devopsfetch
sudo systemctl start devopsfetch

echo "DevOpsFetch installation and service setup complete."
