package com.example.matrixmultiplicationapp;

public class MatrixMultiplication {

    public static void main(String[] args) {
        int[][] matrix1 = {{1, 2, 3}, {4, 5, 6}};
        int[][] matrix2 = {{7, 8}, {9, 10}, {11, 12}};

        int[][] result = multiplyMatrices(matrix1, matrix2);

        System.out.println("Resultant Matrix:");
        printMatrix(result);
    }

    public static int[][] multiplyMatrices(int[][] matrix1, int[][] matrix2) {
        int m1Rows = matrix1.length;
        int m1Cols = matrix1[0].length;
        int m2Cols = matrix2[0].length;

        int[][] result = new int[m1Rows][m2Cols];

        for (int i = 0; i < m1Rows; i++) {
            for (int j = 0; j < m2Cols; j++) {
                for (int k = 0; k < m1Cols; k++) {
                    result[i][j] += matrix1[i][k] * matrix2[k][j];
                }
            }
        }

        return result;
    }

    public static void printMatrix(int[][] matrix) {
        for (int[] row : matrix) {
            for (int elem : row) {
                System.out.print(elem + " ");
            }
            System.out.println();
        }
    }
}