from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from utils import string_to_matrix, determine_complexity, strassen_alg, offload_task, print_matrix, standard_matrix_multiplication
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
    result_matrix, execution_time = standard_matrix_multiplication(matrix_a, matrix_b)
    print(execution_time)

    #print_matrix(execution_time)

    return jsonify({'message': 'Task received'}), 200
# @app.route('/submit_task', methods=['POST'])
# def submit_task():
#     matrix_size = int(request.form['matrixSize'])
#     matrix_a = string_to_matrix(request.form['matrixA'])
#     matrix_b = string_to_matrix(request.form['matrixB'])

#     complexity_a = determine_complexity(matrix_a)
#     complexity_b = determine_complexity(matrix_b)

#     if offload_task(complexity_a, complexity_b):
#         # Offload the task to the cloud server
#         # ...
#         return jsonify({'message': 'Task offloaded to the cloud server'}), 200
#     else:
#         # Perform the multiplication locally
#         result_matrix, execution_time = strassen_alg(matrix_a, matrix_b)
#         complexity_result = determine_complexity(result_matrix)

#         task_details = {
#             'matrix_size_a': len(matrix_a),
#             'matrix_size_b': len(matrix_b),
#             'complexity_a': complexity_a,
#             'complexity_b': complexity_b,
#             'complexity_result': complexity_result,
#             'execution_time': execution_time,
#             'submission_time': datetime.now()
#         }

#         task_id = historical_data.insert_one(task_details).inserted_id
#         return jsonify({'task_id': str(task_id), 'execution_time': execution_time, 'complexity_result': complexity_result}), 201
def sendToCloudServer(matrix_a, matrix_b):
    data = {
        'matrixA': matrix_a,
        'matrixB': matrix_b
    }

    cloud_server_url = "http://{}:5000".format(os.getenv('serverIP'))
    response = requests.post(cloud_server_url, data=json.dumps(data))

    if response.status_code == 200:
        return jsonify({'message': 'Task offloaded to the cloud server'}), 200
    else:
        return jsonify({'message': 'Failed to offload task to the cloud server'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


