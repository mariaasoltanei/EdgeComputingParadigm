from flask import Flask, request, jsonify
from Server.utils import string_to_matrix, matrix_multiplication
import psutil
import threading

app = Flask(__name__)
task_lock = threading.Lock()
active_tasks = 0

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running"}), 200

# Load endpoint to check the CPU and memory usage of the server
# - CPU usage is calculated using psutil.cpu_percent(interval=1)
# - memory usage is calculated using psutil.virtual_memory().percent
# - number of active tasks is also returned
@app.route('/load', methods=['GET'])
def load():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    with task_lock:
        tasks = active_tasks
    return jsonify({"cpu": cpu_usage, "memory": memory_usage, "active_tasks": tasks}), 200

@app.route('/matrices', methods=['POST'])
def test():
    global active_tasks
    with task_lock:
        active_tasks += 1
    data = request.get_json()

    # matrix_size = int(data['matrixSize'])
    matrix_a = string_to_matrix(data['matrixA'])
    matrix_b = string_to_matrix(data['matrixB'])

    result_matrix, execution_time = matrix_multiplication(matrix_a, matrix_b)
    print(execution_time)
    with task_lock:
        active_tasks -= 1
    return jsonify({'execution_time': execution_time}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
