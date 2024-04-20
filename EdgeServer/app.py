from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from utils import string_to_matrix, determine_complexity, strassen_alg, offload_task
import os
load_dotenv()

app = Flask(__name__)

client = MongoClient(os.getenv('MONGODB_CONNECTION_STRING'))
db = client['matrix_tasks']

historical_data = db['historical_data']

@app.route('/submit_task', methods=['POST'])
def submit_task():
    matrix_size = int(request.form['matrixSize'])
    matrix_a = string_to_matrix(request.form['matrixA'])
    matrix_b = string_to_matrix(request.form['matrixB'])

    complexity_a = determine_complexity(matrix_a)
    complexity_b = determine_complexity(matrix_b)

    if offload_task(complexity_a, complexity_b):
        # Offload the task to the cloud server
        # ...
        return jsonify({'message': 'Task offloaded to the cloud server'}), 200
    else:
        # Perform the multiplication locally
        result_matrix, execution_time = strassen_alg(matrix_a, matrix_b)
        complexity_result = determine_complexity(result_matrix)

        task_details = {
            'matrix_size_a': len(matrix_a),
            'matrix_size_b': len(matrix_b),
            'complexity_a': complexity_a,
            'complexity_b': complexity_b,
            'complexity_result': complexity_result,
            'execution_time': execution_time,
            'submission_time': datetime.now()
        }

        task_id = historical_data.insert_one(task_details).inserted_id
        return jsonify({'task_id': str(task_id), 'execution_time': execution_time, 'complexity_result': complexity_result}), 201


if __name__ == '__main__':
    app.run(debug=True)



