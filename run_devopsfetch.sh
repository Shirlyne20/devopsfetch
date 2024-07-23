#!/bin/bash

# Create a specific directory for devopsfetch logs
sudo mkdir -p /var/log/devopsfetch
sudo chown root:root /var/log/devopsfetch
sudo chmod 755 /var/log/devopsfetch

# Run devopsfetch with passed arguments and output to the new log file
python3 /usr/local/bin/devopsfetch "$@" 2>&1 | sudo tee -a /var/log/devopsfetch/devopsfetch.log

# Set up log rotation
cat << EOF | sudo tee /etc/logrotate.d/devopsfetch
/var/log/devopsfetch/devopsfetch.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 640 root root
    su root root
    postrotate
        /bin/kill -HUP \$(cat /var/run/devopsfetch.pid 2>/dev/null) 2>/dev/null || true
    endscript
}
EOF

echo "devopsfetch has run and logged to /var/log/devopsfetch/devopsfetch.log"

