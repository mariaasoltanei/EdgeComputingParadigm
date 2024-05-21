from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from utils import string_to_matrix, determine_complexity, matrix_multiplication
import os
import requests
import json
load_dotenv()

app = Flask(__name__)

# client = MongoClient(os.getenv('MONGODB_CONNECTION_STRING'))
# db = client['matrix_tasks']

# historical_data = db['historical_data']


@app.route('/test', methods=['POST'])
def test():
    data = request.get_json()

    matrix_size = int(data['matrixSize'])
    matrix_a = string_to_matrix(data['matrixA'])
    matrix_b = string_to_matrix(data['matrixB'])

    result_matrix, execution_time = matrix_multiplication(matrix_a, matrix_b)
    print(execution_time)
    # complexity_a = determine_complexity(matrix_a)
    # complexity_b = determine_complexity(matrix_b)
    complexity_a = 'High'
    complexity_b = 'High'
    print(complexity_a, complexity_b)
    if complexity_a == 'High' or complexity_b == 'High':
        response = sendToCloudServer(data['matrixA'], data['matrixB'])
        return response

    return jsonify({'message': 'Task received'}), 200

def sendToCloudServer(matrix_a, matrix_b):
    data = {
        'matrixA': matrix_a,
        'matrixB': matrix_b
    }

    cloud_server_url = f"http://{os.getenv('serverIP')}:5000/receive_task"
    print(cloud_server_url)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(cloud_server_url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        return jsonify({'message': 'Task offloaded ok'}), 200
    else:
        return jsonify({'message': 'Failed to offload task'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


