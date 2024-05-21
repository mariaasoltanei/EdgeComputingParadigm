from flask import Flask, request, jsonify
import requests
import time
from queue import Queue
from threading import Thread, Lock

app = Flask(__name__)
task_queue = Queue()
server_status = {}
server_load = {}
all_servers = [
    'http://localhost:5001',
    'http://localhost:5002',
    'http://localhost:5003'
]
active_servers = []
lock = Lock()

def check_server_status():
    while True:
        with lock:
            for server in all_servers:
                try:
                    response = requests.get(f"{server}/status")
                    if response.status_code == 200:
                        server_status[server] = response.json().get('status')
                        if server_status[server] == "running" and server not in active_servers:
                            active_servers.append(server)
                    else:
                        server_status[server] = "not running"
                        if server in active_servers:
                            active_servers.remove(server)
                except requests.ConnectionError:
                    server_status[server] = "not running"
                    if server in active_servers:
                        active_servers.remove(server)

                try:
                    response = requests.get(f"{server}/load")
                    if response.status_code == 200:
                        server_load[server] = response.json()
                    else:
                        server_load[server] = None
                except requests.ConnectionError:
                    server_load[server] = None

        time.sleep(5)  # Check every 5 seconds

def find_best_server():
    best_server = None
    best_load = None
    with lock:
        for server in active_servers:
            load = server_load.get(server)
            print(f"Server: {server}, Load: {load}")
            if load:
                if best_load is None or (load['cpu'] < best_load['cpu'] and load['memory'] < best_load['memory']):
                    best_server = server
                    best_load = load
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
            print(f"Task completed by {server_url} with execution time: {result['execution_time']} seconds")
        else:
            print(f"Failed to offload task to {server_url}")
    except requests.ConnectionError:
        print(f"Failed to connect to {server_url}")

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
                print(f"Best server to handle the request: {best_server}")
                offload_task_to_server(best_server, matrix_size, matrix_a, matrix_b)
            else:
                print("No servers are available to handle the request.")
            task_queue.task_done()

if __name__ == '__main__':
    # Start server monitoring thread
    monitor_thread = Thread(target=check_server_status)
    monitor_thread.start()

    # Start task consumer thread
    consumer_thread = Thread(target=task_consumer)
    consumer_thread.start()

    # Run the Flask app
    app.run(port=4000)

    monitor_thread.join()
    consumer_thread.join()
