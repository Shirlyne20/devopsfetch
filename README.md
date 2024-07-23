# DevOpsFetch Tool

## Overview

DevOpsFetch is a robust utility tailored for DevOps professionals, offering extensive system information collection and display capabilities. It delivers in-depth details on various aspects, including active network ports, user login activities, Nginx server configurations, Docker images, and the statuses of Docker containers. Additionally, DevOpsFetch features a continuous monitoring mode that logs system activities in real-time, ensuring that you always have the latest information about your system's state.

## Folder Structure
```
devopsfetch/
├── devopsfetch.py
├── install.sh
├── devopsfetch.service
├──run_devopsfetch.sh
├── README.md
└── logs/
    └── devopsfetch.log
```

## Features

### Information Retrieval
1. **Ports**:
   - Display all active ports and services (`-p` or `--port`).
   - Provide detailed information about a specific port (`-p <port_number>`). ie (`-p 80`)

2. **Docker**:
   - List all Docker images and containers (`-d` or `--docker`).
   - Provide detailed information about a specific container (`-d <container_name>`).

3. **Nginx**:
   - Display all Nginx domains and their ports (`-n` or `--nginx`).
   - Provide detailed configuration information for a specific domain (`-n <domain>`).

4. **Users**:
   - List all users and their last login times (`-u` or `--users`).
   - Provide detailed information about a specific user (`-u <username>`).ie(`-u root`) 

5. **Time Range**:
   - Display activities within a specified time range (`-t` or `--time`).

### Output Formatting
- This ensures all outputs are well formatted for readability in well-formatted tables with descriptive column names.

## Installation

### Prerequisites

- Python 3.x
- Docker
- Nginx (used to check Nginx configurations)
- Systemd (for setting up the monitoring service)

### Installation Steps

**Step 1. Clone the Repository**:
   ```bash
   git clone https://github.com/Shirlyne20/devopsfetch.git
   cd devopsfetch
   ```
**Step 2. Create devopsfetch.py File**

In the `cd devopsfetch` create a file named `devopsfetch.py` that servers as the main script for this tool.It defines the following functions:

**1.list_ports():**

**Purpose**: Display all active ports, users, and services in a single table.

**Description**: Uses the psutil library to retrieve active network connections and display relevant information such as port number, user, and service.

**2.port_info(port):**

**Purpose**: Display detailed information about a specific port.
**Description**: Uses the psutil library to retrieve detailed information about a specific port, including file descriptor, family, type, local address, remote address, status, and process ID.

**3.list_docker():**

**Purpose**: List all Docker images and containers.

**Description**: Uses the docker library to retrieve and display a list of all Docker images and containers on the system.

**4.list_nginx():**

**Purpose**: Display all Nginx domains and their ports.

**Description**: Uses a subprocess call to run nginx -T to retrieve the Nginx configuration and parse the server names and ports.

**5.nginx_info(domain)**:

**Purpose**: Display detailed configuration information for a specific Nginx domain.
**Description**: This function is a placeholder to be implemented based on specific Nginx configuration formats.

**6.list_users()**:

**Purpose**: List all users and their last login times.

**Description**: Uses the pwd module to retrieve user information and the last command to retrieve last login times for each user.

**7.user_info(username):**

**Purpose**: Display detailed information about a specific user.

**Description**: Uses the pwd module to retrieve detailed information about a specific user and the last command to get the last login time.

**8.get_activities(start_time, end_time):**

**Purpose**: Display activities within a specified time range.
**Description**: Uses the journalctl command to retrieve and display system activities within the specified time range.

**main():**

**Purpose**: Parse command-line arguments and call the appropriate functions.

**Description**: Uses the argparse library to parse command-line arguments and call the respective functions based on the provided flags.

Here are contents of the `devopsfetch.py` file:

```bash
#!/usr/bin/env python3
import argparse
import psutil
import docker
from prettytable import PrettyTable
import subprocess
import os
import logging
import time
import pwd
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(filename='devopsfetch.log', level=logging.INFO)

# Initialize Docker client
docker_client = docker.from_env()

def list_ports():
    """Display all active ports, users, and services in a single table."""
    connections = psutil.net_connections(kind='inet')
    table = PrettyTable(['Port', 'User', 'Service'])

    for conn in connections:
        if conn.status == psutil.CONN_LISTEN:
            port = conn.laddr.port
            pid = conn.pid
            if pid:
                try:
                    proc = psutil.Process(pid)
                    user = proc.username()
                    service = proc.name()
                    table.add_row([port, user, service])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

    print(table)

def port_info(port):
    """Display detailed information about a specific port."""
    connections = [conn for conn in psutil.net_connections(kind='inet') if conn.laddr.port == port]
    table = PrettyTable(['FD', 'Family', 'Type', 'Laddr', 'Raddr', 'Status', 'PID'])
    for conn in connections:
        table.add_row([conn.fd, conn.family, conn.type, conn.laddr, conn.raddr, conn.status, conn.pid])
    print(table)

def list_docker():
    """List all Docker images and containers."""
    images = docker_client.images.list()
    containers = docker_client.containers.list(all=True)

    if images:
        image_table = PrettyTable(['Image ID'])
        for image in images:
            image_table.add_row([image.id])
        print("Docker Images:")
        print(image_table)
    else:
        print("No Docker images found.")

    if containers:
        container_table = PrettyTable(['Container ID', 'Status'])
        for container in containers:
            container_table.add_row([container.id, container.status])
        print("Docker Containers:")
        print(container_table)
    else:
        print("No Docker containers found.")

def list_nginx():
    """Display all Nginx domains, proxies, and their configuration files."""
    output = subprocess.run(['nginx', '-T'], capture_output=True, text=True)
    config_data = output.stdout
    nginx_info_table = parse_nginx_config(config_data)
    
    if nginx_info_table:
        print("Nginx Configuration:")
        print(nginx_info_table)
    else:
        print("No Nginx configuration found.")

def parse_nginx_config(config_data):
    """Parse Nginx configuration data and return a PrettyTable with server name, proxy, and configuration file."""
    table = PrettyTable(['Server Name', 'Proxy', 'Configuration File'])
    config_lines = config_data.splitlines()
    
    server_name = None
    proxy = None
    configuration_file = None
    
    for line in config_lines:
        if 'server_name' in line:
            server_name = line.split()[1].strip(';')
        elif 'proxy_pass' in line:
            proxy = line.split()[1].strip(';')
        elif 'include' in line:
            configuration_file = line.split()[1].strip(';')
            table.add_row([server_name, proxy, configuration_file])
            server_name = None
            proxy = None
            configuration_file = None
    
    return table

def nginx_info(domain):
    """Display detailed configuration information for a specific domain."""
    # This function should be implemented based on your specific nginx configuration format
    print(f"Detailed info for domain: {domain}")

def list_users():
    """List all users and their last login times."""
    users = []
    for uid in range(1000):
        try:
            user_info = pwd.getpwuid(uid)
            users.append(user_info.pw_name)
        except KeyError:
            # UID not found
            continue
    
    table = PrettyTable(['User', 'Last Login'])
    for user in users:
        try:
            last_login = subprocess.run(['last', '-n', '1', user], capture_output=True, text=True).stdout.strip()
            if not last_login:
                last_login = "No recent login"
            table.add_row([user, last_login])
        except Exception as e:
            table.add_row([user, f"Error: {str(e)}"])
    
    print(table)


def get_users_info():
    users = []
    current_time = datetime.now()
    
    table = PrettyTable()
    table.field_names = ["Username", "Terminal", "Login Time", "Session Duration"]
    
    for user in psutil.users():
        username = user.name
        terminal = user.terminal
        started = datetime.fromtimestamp(user.started)
        
        duration = current_time - started
        
        last_login = started.strftime('%Y-%m-%d %H:%M:%S')
        duration_str = str(duration).split('.')[0]  # Remove microseconds
        
        table.add_row([username, terminal,last_login, duration_str])
    
    return table.get_string()

def get_user_info(username):
    users = psutil.users()
    user_sessions = [user for user in users if user.name == username]
    
    if not user_sessions:
        return f"User {username} is not currently logged in."
    
    current_time = datetime.now()
    user_info = []
    
    for session in user_sessions:
        started = datetime.fromtimestamp(session.started)
        duration = current_time - started
        
        table = PrettyTable()
        table.field_names = ["Property", "Value"]
        table.add_row(["Username", session.name])
        table.add_row(["Terminal", session.terminal])
        table.add_row(["Login Time", started.strftime('%Y-%m-%d %H:%M:%S')])
        table.add_row(["Session Duration", str(duration).split('.')[0]])  # Remove microseconds
        
        user_info.append(table.get_string())
    
    return "\n\n".join(user_info)
    
def get_activities(start_time, end_time):
    """Display activities within a specified time range."""
    try:
        # Convert input timestamps to datetime objects
        start_dt = datetime.strptime(start_time, "%Y-%m-%d")
        # Add one day to end_time to include the entire end date in the range
        end_dt = datetime.strptime(end_time, "%Y-%m-%d") + timedelta(days=1)

        # Format the datetime objects to the required format
        start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")

        cmd = f"journalctl --since '{start_str}' --until '{end_str}'"
        logging.info(f"Running command: {cmd}")
        output = subprocess.check_output(cmd, shell=True).decode().strip()
        logging.info(f"Command output: {output}")
        if output:
            return output
        else:
            return "-- No entries --"
    except ValueError as ve:
        logging.error(f"Timestamp parsing error: {ve}")
        return f"Error: Failed to parse timestamps: {start_time}, {end_time}"
    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}")
        return f"Error: Failed to retrieve journal logs for the given time range."

def main():
    parser = argparse.ArgumentParser(description="DevOps Fetch Tool")
    parser.add_argument('-p', '--port', nargs='?', const='all', help='Display all active ports or detailed info about a specific port')
    parser.add_argument('-d', '--docker', action='store_true', help='List all Docker images and containers')
    parser.add_argument('-n', '--nginx', type=str, nargs='?', const='', help='Display all Nginx domains or detailed config for a specific domain')
    parser.add_argument('-u', '--users', type=str, nargs='?', const='list', help='Display user info or info for a specific user')
    parser.add_argument("-t", "--time", nargs=2, metavar=('START', 'END'), help="Display activities within a time range (YYYY-MM-DD format)")
    args = parser.parse_args()

    if args.port is not None:
        if args.port == 'all':
            list_ports()
        else:
            port_info(int(args.port))
    elif args.docker:
        list_docker()
    elif args.nginx is not None:
        if args.nginx:
            nginx_info(args.nginx)
        else:
            list_nginx()
    elif args.users is not None:
        if args.users == '' or args.users == 'list':
            print(get_users_info())
        else:
            print(get_user_info(args.users))
    elif args.time:
        start_time, end_time = args.time
        activities = get_activities(start_time, end_time)
        print(activities)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

```

**Step 3:Make the script executable:**
```bash
chmod +x devopsfetch.py
```
**Step 4: Create the `install.sh` file**

The `install.sh` script is used to automate the installation and setup process for the DevOpsFetch tool. This script ensures that all necessary dependencies are installed, the appropriate configuration files are copied to the correct locations, and the systemd service is properly set up and started. This makes the installation process seamless and consistent.

It defines the following functions:
Command Existence Check:

**command_exists()**:

 A helper function to check if a command exists on the system.

**Starting Message:**

Prints a message indicating the start of the installation process.

**Install Required Python Packages:**

Checks if pip is installed. If it is, installs the required Python packages listed in requirements.txt. If pip is not installed, it prints an error message and exits.

**Create Necessary Directories:**

Creates the directory /var/log/devopsfetch to store log files.

**Copy Systemd Service File:**

Copies the devopsfetch.service file from the config directory to /etc/systemd/system/. If the file is not found, it prints an error message and exits.

**Reload Systemd Daemon:**

Reloads the systemd daemon to recognize the new service file.

**Start and Enable the DevOpsFetch Service:**

Starts the devopsfetch service and enables it to start on boot.

**Copy Logrotate Configuration File:**

Copies the devopsfetch logrotate configuration file from config/logrotate.d/ to /etc/logrotate.d/. If the file is not found, it prints an error message and exits.

**Completion Message:**

Prints a message indicating the successful completion of the installation process.


**To make `install.sh` executable:**
```bash
chmod +x install.sh
```
**Run the script:**
```bash
sudo ./install.sh
```

**Step 5: Create a systemd service file `/etc/systemd/system/devopsfetch.service`**

Creating a systemd service file at /etc/systemd/system/devopsfetch.service allows the DevOpsFetch tool to run as a managed service on your system. This means it can be started, stopped, and monitored by the systemd init system.

**Create the Service File:**

Copy the service file to the systemd directory
```bash
sudo cp /home/shirlcookie/devopsfetch/config/devopsfetch.service /etc/systemd/system/devopsfetch.service
```
**Reload systemd to Recognize the New Service:**
```bash
sudo systemctl daemon-reload
```
**Start the Service:**
```bash
sudo systemctl start devopsfetch
```
**Enable the Service to Start on Boot:**
```bash
sudo systemctl enable devopsfetch
```
**Check the Status of the Service:**
```bash
sudo systemctl status devopsfetch
```

**Step 6:Create `run_devopsfetch.sh` file:**

The `run_devopsfetch.sh` script is used to run the DevOpsFetch tool in a specific way, typically to set up the environment, run the tool with certain parameters, and handle logging or other preparations before executing the main script. This script can be useful for encapsulating commands and options that are frequently used together or for setting up additional context or environment variables.

Its content define;

**Ensure the Log Directory Exists:**

`sudo mkdir -p /var/log/devopsfetch`: Creates the log directory if it doesn't already exist.

`sudo chown root:root /var/log/devopsfetch`: Sets the ownership of the log directory to the root user and group.

`sudo chmod 755 /var/log/devopsfetch`: Sets the permissions of the log directory to be readable and executable by everyone, but writable only by the owner.

**Run DevOpsFetch and Output to the Log File:**

/usr/bin/python3 /usr/local/bin/devopsfetch `"$@" 2>&1 | sudo tee -a /var/log/devopsfetch/devopsfetch.log`: Runs the devopsfetch script with all the arguments passed to `run_devopsfetch.sh`. The output (both stdout and stderr) is appended to the `log file /var/log/devopsfetch/devopsfetch.log`.

**Set Up Log Rotation:**

`sudo tee /etc/logrotate.d/devopsfetch > /dev/null << 'EOF' ... EOF`: Creates a logrotate configuration for the devopsfetch logs.
The logrotate configuration ensures that logs are rotated daily, kept for 7 days, compressed, and only rotated if they are not empty. It also specifies permissions and ownership for the rotated logs and reloads the service after rotation.

Completion Message:

`echo "devopsfetch has run and logged to /var/log/devopsfetch/devopsfetch.log"`: Prints a message indicating that DevOpsFetch has run and logged its output.

**To use the run_devopsfetch.sh script;**

Make the Script Executable:
```bash
chmod +x run_devopsfetch.sh
```

## Usage
**Help**

-Display usage instructions:
```bash
devopsfetch -h
```
-Expected Output:
```bash
usage: devopsfetch [-h] [-p [PORT]] [-d] [-n [NGINX]] [-u [USERS]] [-t START END]

DevOps Fetch Tool

options:
  -h, --help            show this help message and exit
  -p [PORT], --port [PORT]
                        Display all active ports or detailed info about a specific port
  -d, --docker          List all Docker images and containers
  -n [NGINX], --nginx [NGINX]
                        Display all Nginx domains or detailed config for a specific domain
  -u [USERS], --users [USERS]
                        Display user info or info for a specific user
  -t START END, --time START END
                        Display activities within a time range (YYYY-MM-DD format)
```
**Ports**

-Display all active ports and services:
```bash
devopsfetch -p
```
-Expected Output
```bash
+-------+-----------------+------------------+
|  Port |       User      |     Service      |
+-------+-----------------+------------------+
|  8080 |       root      |   docker-proxy   |
|  4369 |       epmd      |       epmd       |
|  6379 |      redis      |   redis-server   |
|   80  |     www-data    |      nginx       |
|   80  |     www-data    |      nginx       |
|  5672 |     rabbitmq    |     beam.smp     |
| 15672 |     rabbitmq    |     beam.smp     |
|  8080 |       root      |   docker-proxy   |
|   53  | systemd-resolve | systemd-resolved |
| 25672 |     rabbitmq    |     beam.smp     |
|  6379 |      redis      |   redis-server   |
| 33849 |   shirlcookie   |       node       |
+-------+-----------------+------------------+
```
-Display detailed information about a specific port:
```bash
devopsfetch -p 80
```
**Docker**

-List all Docker images and containers:
```bash
devopsfetch -d
```
-Expected output:
```bash
Docker Images:
+-------------------------------------------------------------------------+
|                                 Image ID                                |
+-------------------------------------------------------------------------+
| sha256:fffffc90d343cbcb01a5032edac86db5998c536cd0a366514121a45c6723765c |
| sha256:d2c94e258dcb3c5ac2798d32e1249e42ef01cba4841c2234249495f87264ac5a |
+-------------------------------------------------------------------------+
Docker Containers:
+------------------------------------------------------------------+---------+
|                           Container ID                           |  Status |
+------------------------------------------------------------------+---------+
| 834fe740eb7206d0bff040a11efb3de7a2e01af6753744deee6be7c7b8a8b6cd | running |
| 8246db8436a9a979e8a6232dda4b792f2c5ab5e1233ed00a9e9464eb0f8abba5 |  exited |
+------------------------------------------------------------------+---------+
```
-Provide detailed information about a specific container:
```bash
devopsfetch -d <container_name>
```
**Nginx**

-Display all Nginx domains and their ports:
```bash
devopsfetch -n
```
-Expected Output:
```bash
+-------------------------+-------+-----------------------------------+
|       Server Name       | Proxy |         Configuration File        |
+-------------------------+-------+-----------------------------------+
|           None          |  None | /etc/nginx/modules-enabled/*.conf |
| server_name_in_redirect |  None |       /etc/nginx/mime.types       |
|           None          |  None |      /etc/nginx/conf.d/*.conf     |
|           None          |  None |     /etc/nginx/sites-enabled/*    |
|           None          |  None |              include              |
|            _            |  None |              include              |
+-------------------------+-------+-----------------------------------+
```
-Provide detailed configuration information for a specific domain:
```bash
devopsfetch -n <domain>
```
**Users**

-List all users and their last login times:
```bash
devopsfetch -u
```

-Expected Output:
```bash
+-------------+----------+---------------------+------------------+
|   Username  | Terminal |      Login Time     | Session Duration |
+-------------+----------+---------------------+------------------+
| shirlcookie |  pts/1   | 2024-07-23 11:18:25 |     7:02:56      |
| shirlcookie |  pts/9   | 2024-07-23 18:21:20 |     0:00:01      |
+-------------+----------+---------------------+------------------+
```
-Provide detailed information about a specific user:
```bash
devopsfetch -u root
```
**Time Range**

-Display activities within a specified time range:
```bash
devopsfetch -t "YYYY-MM-DD " "YYYY-MM-DD"
```
-Expected output:
```bash
Jul 23 18:26:29 DESKTOP-8NM259D sudo[189957]: shirlcookie : TTY=pts/8 ; PWD=/home/shirlcookie/devopsfetch ; USER=root ; COMMAND=/usr/local/bin/devopsfetch -t 2024-07-22 2024-07-23
Jul 23 18:26:29 DESKTOP-8NM259D sudo[189957]: pam_unix(sudo:session): session opened for user root(uid=0) by (uid=1000)
```
## Collaboration Guide

I welcome contributions from the community to improve **Devopsfetch Tool**! Here's how you can get involved:
- Reporting Issues
- Suggesting Features


- Contributing Code
>1. Fork the repository
>
>2. Create a new branch, 
>
>3. Make your changes
>
>4. Test thoroughly
>
>
## Maintenance

## Troubleshooting

## Licence
