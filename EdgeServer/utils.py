import numpy as np
import time

def string_to_matrix(matrix_string):
    return [list(map(int, row.split(','))) for row in matrix_string.split(';')]

def determine_complexity(matrix):
    size = len(matrix) * len(matrix[0])  # Total number of elements in the matrix
    non_zero_elements = sum(el != 0 for row in matrix for el in row)  # Number of non-zero elements
    sparsity = 1 - non_zero_elements / size  # Ratio of zero elements

    # Determine complexity based on size and sparsity
    if size > 10000 and sparsity < 0.5:
        return 'High'
    elif size > 5000 and sparsity < 0.7:
        return 'Medium'
    else:
        return 'Low'
    

def strassen_alg(matrix_a, matrix_b):
    start_time = time.time()

    n = len(matrix_a)

    if n == 1:
        result = matrix_a * matrix_b
    else:
        # Divide matrices into quadrants
        a11, a12, a21, a22 = split(matrix_a)
        b11, b12, b21, b22 = split(matrix_b)

        # Calculate p1 to p7
        p1 = strassen_alg(a11 + a22, b11 + b22)
        p2 = strassen_alg(a21 + a22, b11)
        p3 = strassen_alg(a11, b12 - b22)
        p4 = strassen_alg(a22, b21 - b11)
        p5 = strassen_alg(a11 + a12, b22)
        p6 = strassen_alg(a21 - a11, b11 + b12)
        p7 = strassen_alg(a12 - a22, b21 + b22)

        # Combine p1 to p7 to get the final matrices
        c11 = p1 + p4 - p5 + p7
        c12 = p3 + p5
        c21 = p2 + p4
        c22 = p1 - p2 + p3 + p6

        result = np.vstack((np.hstack((c11, c12)), np.hstack((c21, c22))))

    end_time = time.time()

    return result, end_time - start_time

def split(matrix):
    n = len(matrix)
    mid = n // 2
    return matrix[:mid, :mid], matrix[:mid, mid:], matrix[mid:, :mid], matrix[mid:, mid:]

def offload_task(complexity_a, complexity_b):
    # Define the complexity threshold for offloading tasks
    offload_threshold = 'High'

    # If either matrix has a complexity above the threshold, offload the task
    if complexity_a == offload_threshold or complexity_b == offload_threshold:
        return True

    return False