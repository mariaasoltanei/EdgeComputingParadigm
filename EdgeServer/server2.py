from flask import Flask, request, jsonify
from utils import string_to_matrix, matrix_multiplication
import psutil

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running"}), 200

@app.route('/load', methods=['GET'])
def load():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    return jsonify({"cpu": cpu_usage, "memory": memory_usage}), 200

@app.route('/matrices', methods=['POST'])
def test():
    data = request.get_json()

    matrix_size = int(data['matrixSize'])
    matrix_a = string_to_matrix(data['matrixA'])
    matrix_b = string_to_matrix(data['matrixB'])

    result_matrix, execution_time = matrix_multiplication(matrix_a, matrix_b)
    print(execution_time)

    return jsonify({'execution_time': execution_time}), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)