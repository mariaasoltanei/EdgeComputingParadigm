from flask import Flask, request, jsonify
from utils import string_to_matrix, matrix_multiplication
import psutil
import threading

app = Flask(__name__)
task_lock = threading.Lock()
active_tasks = 0

@app.route('/matrices', methods=['POST'])
def test():
    global active_tasks
    with task_lock:
        active_tasks += 1
    data = request.get_json()

    matrix_size = int(data['matrixSize'])
    matrix_a = string_to_matrix(data['matrixA'])
    matrix_b = string_to_matrix(data['matrixB'])

    result_matrix, execution_time = matrix_multiplication(matrix_a, matrix_b)
    print(execution_time)
    with task_lock:
        active_tasks -= 1
    return jsonify({'execution_time': execution_time}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)