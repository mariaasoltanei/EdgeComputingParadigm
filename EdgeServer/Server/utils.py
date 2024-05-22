import numpy as np
import time
import requests
import json
import os

def string_to_matrix(matrix_string):
    return [[int(num) for num in row.split(',')] for row in matrix_string.split(';')]

def determine_complexity(matrix):
    size = len(matrix) * len(matrix[0])  # nr of elements in the matrix
    non_zero_elements = sum(el != 0 for row in matrix for el in row) 
    sparsity = 1 - non_zero_elements / size  # zero elements ratio

    if size > 10000 and sparsity < 0.5:
        return 'High'
    elif size > 5000 and sparsity < 0.7:
        return 'Medium'
    else:
        return 'Low'

def matrix_multiplication(matrix_a, matrix_b):
    start_time = time.time()
    n1, m1 = len(matrix_a), len(matrix_a[0])
    n2, m2 = len(matrix_b), len(matrix_b[0])

    if m1 != n2:
        raise ValueError("nr of columns in the first matrix = nr of rows in the second matrix.")

    result = [[0 for _ in range(m2)] for _ in range(n1)]
    for i in range(n1):
        for j in range(m2):
            for k in range(m1):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]

    end_time = time.time()
    execution_time = end_time - start_time
    return result, execution_time

