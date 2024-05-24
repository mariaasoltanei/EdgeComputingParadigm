from flask import Flask, request, jsonify
from utils import string_to_matrix, matrix_multiplication
app = Flask(__name__)

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
    app.run(host='0.0.0.0', port=5000)