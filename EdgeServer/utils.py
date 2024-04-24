import numpy as np
import time

def string_to_matrix(matrix_string):
    return [[int(num) for num in row.split(',')] for row in matrix_string.split(';')]

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

def standard_matrix_multiplication(matrix_a, matrix_b):
    # Record the start time
    start_time = time.time()

    # Get the dimensions of the matrices
    n1, m1 = len(matrix_a), len(matrix_a[0])
    n2, m2 = len(matrix_b), len(matrix_b[0])

    # Check if the matrices are compatible for multiplication
    if m1 != n2:
        raise ValueError("The number of columns in the first matrix must be equal to the number of rows in the second matrix.")

    # Create a new matrix to store the result
    result = [[0 for _ in range(m2)] for _ in range(n1)]

    # Perform the multiplication
    for i in range(n1):
        for j in range(m2):
            for k in range(m1):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]

    # Record the end time
    end_time = time.time()

    # Calculate and print the execution time
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

    return result, execution_time

def add_matrices(matrix_a, matrix_b):
    print(type(matrix_a), type(matrix_b))
    print([type(row) for row in matrix_a])
    print([type(row) for row in matrix_b])
    return [[matrix_a[i][j] + matrix_b[i][j] for j in range(len(matrix_a[0]))] for i in range(len(matrix_a))]
def subtract_matrices(matrix_a, matrix_b):
    return [[matrix_a[i][j] - matrix_b[i][j] for j in range(len(matrix_a[0]))] for i in range(len(matrix_a))]

def strassen_alg(matrix_a, matrix_b):
    n = len(matrix_a)
    print("len matriX ", n)

    if n == 1:
        return [[matrix_a[0][0] * matrix_b[0][0]]]

    half = n // 2

    a11 = [[matrix_a[i][j] for j in range(half)] for i in range(half)]
    a12 = [[matrix_a[i][j] for j in range(half, n)] for i in range(half)]
    a21 = [[matrix_a[i][j] for j in range(half)] for i in range(half, n)]
    a22 = [[matrix_a[i][j] for j in range(half, n)] for i in range(half, n)]

    b11 = [[matrix_b[i][j] for j in range(half)] for i in range(half)]
    b12 = [[matrix_b[i][j] for j in range(half, n)] for i in range(half)]
    b21 = [[matrix_b[i][j] for j in range(half)] for i in range(half, n)]
    b22 = [[matrix_b[i][j] for j in range(half, n)] for i in range(half, n)]

    p1 = strassen_alg(a11, subtract_matrices(b12, b22))
    p2 = strassen_alg(add_matrices(a11, a12), b22)
    p3 = strassen_alg(add_matrices(a21, a22), b11)
    p4 = strassen_alg(a22, subtract_matrices(b21, b11))
    p5 = strassen_alg(add_matrices(a11, a22), add_matrices(b11, b22))
    p6 = strassen_alg(subtract_matrices(a12, a22), add_matrices(b21, b22))
    p7 = strassen_alg(subtract_matrices(a11, a21), add_matrices(b11, b12))

    c11 = add_matrices(subtract_matrices(add_matrices(p5, p4), p2), p6)
    c12 = add_matrices(p1, p2)
    c21 = add_matrices(p3, p4)
    c22 = subtract_matrices(subtract_matrices(add_matrices(p5, p1), p3), p7)

    result = [[0 for _ in range(n)] for _ in range(n)]
    for i in range(half):
        for j in range(half):
            result[i][j] = c11[i][j]
            result[i][j + half] = c12[i][j]
            result[i + half][j] = c21[i][j]
            result[i + half][j + half] = c22[i][j]

    return result

def split(matrix):
    mid = len(matrix) // 2
    return (
        [[matrix[i][j] for j in range(mid)] for i in range(mid)],  # Top left
        [[matrix[i][j] for j in range(mid, len(matrix))] for i in range(mid)],  # Top right
        [[matrix[i][j] for j in range(mid)] for i in range(mid, len(matrix))],  # Bottom left
        [[matrix[i][j] for j in range(mid, len(matrix))] for i in range(mid, len(matrix))]  # Bottom right
    )
def offload_task(complexity_a, complexity_b):
    # Define the complexity threshold for offloading tasks
    offload_threshold = 'High'

    # If either matrix has a complexity above the threshold, offload the task
    if complexity_a == offload_threshold or complexity_b == offload_threshold:
        return True

    return False

def print_matrix(matrix):
    for row in matrix:
        print(' '.join([str(elem) for elem in row]))
    print()