from flask import Flask, request, jsonify
import requests
import time
from queue import Queue
from threading import Thread, Lock
import csv
import os
import json

app = Flask(__name__)
task_queue = Queue()
server_status = {}
server_load = {}
all_servers = [
    'http://127.0.0.1:5004',
    'http://127.0.0.1:5005',
    'http://127.0.0.1:5006'
]
active_servers = []
lock = Lock()

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

        time.sleep(5) 

def find_best_server():
    best_server = None
    min_task_count = float('inf')  # Track the server with the least tasks
    best_load = None
    with lock:
        for server in active_servers:
            try:
                response = requests.get(f"{server}/load")
                if response.status_code == 200:
                    server_load_info = response.json()
                    task_count = server_load_info['active_tasks']
                    # Check if this server has the least tasks and acceptable load
                    if task_count < min_task_count:
                        min_task_count = task_count
                        best_server = server
            except requests.ConnectionError:
                continue
    return best_server

def offload_task_to_server(server_url, matrix_size, matrix_a, matrix_b):
    payload = {
        "matrixSize": matrix_size,
        "matrixA": matrix_a,
        "matrixB": matrix_b
    }
    try:
        response = requests.post(f"{server_url}/matrices", json=payload)
        if response.status_code == 200:
            result = response.json()
            execution_time = result['execution_time']
            print(f"{server_url} - {execution_time} s")

            # Log
            with lock:
                server_task_count[server_url] += 1
                server_task_times[server_url].append(execution_time)
                log_to_csv()

        else:
            print(f"Failed to offload task to {server_url}")
    except requests.ConnectionError:
        print(f"Failed to connect to {server_url}")

def send_to_cloud_server(matrix_a, matrix_b):
    data = {
        'matrixA': matrix_a,
        'matrixB': matrix_b
    }

    cloud_server_url = f"http://{os.getenv('serverIP')}:5000/receive_task"
    print(cloud_server_url)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(cloud_server_url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        print('Task offloaded to cloud successfully')
        return True
    else:
        print('Failed to offload task to cloud')
        return False

@app.route('/post_task', methods=['POST'])
def submit_task():
    data = request.get_json()
    matrix_size = data.get('matrixSize')
    matrix_a = data.get('matrixA')
    matrix_b = data.get('matrixB')
    task_queue.put((matrix_size, matrix_a, matrix_b))
    return jsonify({"message": "Task added to the queue"}), 200

def task_consumer():
    while True:
        if not task_queue.empty():
            matrix_size, matrix_a, matrix_b = task_queue.get()
            best_server = find_best_server()
            if best_server:
                offload_task_to_server(best_server, matrix_size, matrix_a, matrix_b)
            else:
                print("No local servers are available. Offloading task to cloud server.")
                send_to_cloud_server(matrix_a, matrix_b)
            task_queue.task_done()

if __name__ == '__main__':
    #monitoring thread
    monitor_thread = Thread(target=check_server_status)
    monitor_thread.start()

    #consumer thread
    consumer_thread = Thread(target=task_consumer)
    consumer_thread.start()

    app.run(port=4000)

    monitor_thread.join()
    consumer_thread.join()
