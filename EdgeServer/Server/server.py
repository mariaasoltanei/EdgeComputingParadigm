from flask import Flask, request, jsonify
import psutil
import threading
import os

app = Flask(__name__)
task_lock = threading.Lock()
active_tasks = 0

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running"}), 200

@app.route('/load', methods=['GET'])
def load():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    with task_lock:
        tasks = active_tasks
    return jsonify({"cpu": cpu_usage, "memory": memory_usage, "active_tasks": tasks}), 200

@app.route('/gyroscope', methods=['POST'])
def receiveGyroscopeData():
    global active_tasks
    with task_lock:
        active_tasks += 1
    data = request.get_json()
    with task_lock:
        active_tasks -= 1
    return jsonify({'gyroscopeData': data['gyroscopeData']}), 200

@app.route('/accelerometer', methods=['POST'])
def receiveAccelerometerData():
    global active_tasks
    with task_lock:
        active_tasks += 1
    data = request.get_json()
    with task_lock:
        active_tasks -= 1
    return jsonify({'accelerometerData': data['accelerometerData']}), 200

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(host='0.0.0.0', port=port)