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
    """Display all Nginx domains and their ports."""
    output = subprocess.run(['nginx', '-T'], capture_output=True, text=True)
    config_data = output.stdout
    domains = parse_nginx_config(config_data)
    table = PrettyTable(['Domain'])
    for domain in domains:
        table.add_row([domain])
    print(table)

def parse_nginx_config(config_data):
    domains = []
    for line in config_data.splitlines():
        if 'server_name' in line:
            domain = line.split()[1].strip(';')
            domains.append(domain)
    return domains

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
