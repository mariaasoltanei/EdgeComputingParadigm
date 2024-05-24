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

def submit_to_server(server_url, data):
    try:
        response = requests.post(f"{server_url}/matrices", json=data)
        if response.status_code == 200:
            return response
        else:
            return None
    except requests.RequestException:
        return None

def send_to_cloud_server(matrix_a, matrix_b):
    data = {
        'matrixA': matrix_a,
        'matrixB': matrix_b
    }

    cloud_server_url = f"http://{os.getenv('serverIP')}:5000/matrices"

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
    # print(data['guid'])
    best_server = find_least_busy_server()
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
                #PROBLEM HERE? nu stiu daca imi parseaza bine + ca oricum trb sa le fac in string
                send_to_cloud_server(data['matrixA'], data['matrixB'])
                return jsonify({"message": "Task submitted to cloud"}), 200
    else:
        send_to_cloud_server(data['matrixA'], data['matrixB'])
        return jsonify({"message": "Task submitted to cloud"}), 200

if __name__ == '__main__':
    monitor_thread = Thread(target=check_server_status)
    monitor_thread.start()
    app.run(port=4000)
    monitor_thread.join()
