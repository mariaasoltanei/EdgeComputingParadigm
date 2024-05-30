from flask import Flask, request, jsonify
import requests
import time
from threading import Thread, Lock
import csv
import json
import os

app = Flask(__name__)
server_status = {}
server_load = {}
# Initial list of all servers that can be used to offload tasks
all_servers = [
    'http://127.0.0.1:5001',
    'http://127.0.0.1:5002',
    'http://127.0.0.1:5003'
]
active_servers = []
lock = Lock()

# Initialize server_log.csv file
log_file = 'server_log.csv'
server_downtime = {server: 0 for server in all_servers}
server_task_count = {server: 0 for server in all_servers}
server_task_times = {server: [] for server in all_servers}
downtime_start = {server: time.time() for server in all_servers}

if not os.path.exists(log_file):
    with open(log_file, 'w', newline='') as csvfile:
        fieldnames = ['server', 'task_count', 'execution_time', 'downtime']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

# Update the server_log.csv file with the latest data
def log_to_csv():
    with open(log_file, 'w', newline='') as csvfile:
        fieldnames = ['server', 'task_count', 'execution_time', 'downtime']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for server in all_servers:
            writer.writerow({
                'server': server,
                'task_count': server_task_count[server],
                'execution_time': sum(server_task_times[server]),
                'downtime': server_downtime[server]
            })

# Check the status of each server
# - calling the /status endpoint of each server
# - updates the active_servers list with the servers that are running so that they can be used to offload tasks
# - removes servers from active_servers if they are not running
# - updates the server_downtime dictionary for server_log.csv
def check_server_status():
    while True:
        with lock:
            for server in all_servers:
                try:
                    response = requests.get(f"{server}/status")
                    if response.status_code == 200:
                        server_status[server] = response.json().get('status')
                        if server_status[server] == "running":
                            if server not in active_servers:
                                active_servers.append(server)
                                server_downtime[server] += time.time() - downtime_start[server]
                    else:
                        server_status[server] = "not running"
                        if server in active_servers:
                            active_servers.remove(server)
                            downtime_start[server] = time.time()
                except requests.ConnectionError:
                    server_status[server] = "not running"
                    if server in active_servers:
                        active_servers.remove(server)
                        downtime_start[server] = time.time()

                try:
                    response = requests.get(f"{server}/load")
                    if response.status_code == 200:
                        server_load[server] = response.json()
                    else:
                        server_load[server] = None
                except requests.ConnectionError:
                    server_load[server] = None

        time.sleep(10) 

# Find the least busy server 
# - calling the /load endpoint of each server
# - returns the server that has the least number of active tasks
def find_least_busy_server(exclude=None):
    min_tasks = float('inf')
    best_server = None
    for server in all_servers:
        if server == exclude:
            continue
        try:
            response = requests.get(f"{server}/load")
            if response.status_code == 200 and 'active_tasks' in response.json():
                tasks = response.json()['active_tasks']
                if tasks < min_tasks:
                    min_tasks = tasks
                    best_server = server
        except requests.RequestException:
            continue
    return best_server

# Submit the task to the server
# - calling the /matrices endpoint of the server - matrices will be multiplied if sent to this endpoint
# - returns the response from the server if the task was submitted successfully
def submit_to_server(server_url, data):
    try:
        response = requests.post(f"{server_url}/matrices", json=data)
        if response.status_code == 200:
            return response
        else:
            return None
    except requests.RequestException:
        return None

# Send the task to the cloud server
def send_to_cloud_server(data):
    cloud_server_url = f"http://{os.getenv('serverIP')}:5000/matrices"
 

    headers = {'Content-Type': 'application/json'}
    response = requests.post(cloud_server_url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        print('Task offloaded to cloud successfully')
        return True
    else:
        print('Failed to offload task to cloud')
        return False

# Endpoint that the client will use to submit tasks
# - checks the status of each server
# - finds the least busy server
# - submits the task to the server
# - if the server is not available, retries with the next least busy server and then offloads the task to the cloud server if all servers are busy
@app.route('/post_task', methods=['POST'])
def submit_task():
    data = request.get_json()
    best_server = find_least_busy_server()
    if best_server and len(active_servers) == 1:  
        task_target = server_task_count[best_server] % 2 
        if task_target == 0:
            response = send_to_cloud_server(data)
        else:
            response = submit_to_server(best_server, data)
        return jsonify({"message": "Task submitted based on server availability"}), 200
    if best_server:
        response = submit_to_server(best_server, data)
        if response:
            result = response.json()
            print(result)
            execution_time = result['execution_time']
            print(f"{best_server} - {execution_time} s")
            with lock:
                server_task_count[best_server] += 1
                log_to_csv()
            return jsonify({"message": "Task submitted to server", "server": best_server}), 200
        else:
            second_best_server = find_least_busy_server(exclude=best_server)
            if second_best_server:
                response = submit_to_server(second_best_server, data)
                if response:
                    result = response.json()
                    execution_time = result['execution_time']
                    print(f"{second_best_server} - {execution_time} s")
                    with lock:
                        server_task_count[second_best_server] += 1
                        log_to_csv()
                    return jsonify({"message": "Task submitted to server on retry", "server": second_best_server}), 200
            else:
                send_to_cloud_server(data)
                return jsonify({"message": "Task submitted to cloud"}), 200
    else:
        send_to_cloud_server(data)
        return jsonify({"message": "Task submitted to cloud"}), 200

if __name__ == '__main__':
    monitor_thread = Thread(target=check_server_status)
    monitor_thread.start()
    app.run(port=4000)
    monitor_thread.join()
