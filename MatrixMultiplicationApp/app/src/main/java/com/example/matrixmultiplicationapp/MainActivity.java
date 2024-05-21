package com.example.matrixmultiplicationapp;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.Button;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONObject;

import java.io.IOException;
import java.util.Random;

import okhttp3.FormBody;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";
    private static final int MIN_MATRIX_SIZE = 10;
    private static final int MAX_MATRIX_SIZE = 100;
    private static final int TASK_INTERVAL_MS = 500;
    private final Handler mHandler = new Handler(Looper.getMainLooper());
    private final Random mRandom = new Random();

    private Button mStartButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mStartButton = findViewById(R.id.startButton);
        mStartButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startTaskGeneration();
            }
        });
    }

    private void startTaskGeneration() {
        mHandler.postDelayed(taskGenerator, TASK_INTERVAL_MS);
        mStartButton.setEnabled(false);
    }

    private final Runnable taskGenerator = new Runnable() {
        @Override
        public void run() {
            int matrixSize = getRandomMatrixSize();

            int[][] matrixA = generateRandomMatrix(matrixSize);
            int[][] matrixB = generateRandomMatrix(matrixSize);

            Log.d(TAG, "Generated matrix multiplication task: Matrix A size = " + matrixSize
                    + ", Matrix B size = " + matrixSize);

            sendTaskToServer(matrixSize, matrixA, matrixB);
            mHandler.postDelayed(taskGenerator, TASK_INTERVAL_MS);
        }
    };

    private int getRandomMatrixSize() {
        return mRandom.nextInt(MAX_MATRIX_SIZE - MIN_MATRIX_SIZE + 1) + MIN_MATRIX_SIZE;
    }
    private int[][] generateRandomMatrix(int size) {
        Random random = new Random();
        int[][] matrix = new int[size][size];
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                matrix[i][j] = random.nextInt(100);
            }
        }
        return matrix;
    }

    private void sendTaskToServer(int matrixSize, int[][] matrixA, int[][] matrixB) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    OkHttpClient client = new OkHttpClient();

                    String matrixAString = matrixToString(matrixA);
                    String matrixBString = matrixToString(matrixB);

                    JSONObject json = new JSONObject();
                    json.put("matrixSize", matrixSize);
                    json.put("matrixA", matrixAString);
                    json.put("matrixB", matrixBString);

                    RequestBody body = RequestBody.create(
                            MediaType.parse("application/json; charset=utf-8"),
                            json.toString()
                    );

                    Request request = new Request.Builder()
                            .url("http://10.0.2.2:4000/post_task")
                            .post(body)
                            .build();

                    Response response = client.newCall(request).execute();

                    if (!response.isSuccessful()) {
                        throw new IOException("Unexpected code " + response);
                    }

                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

    private String matrixToString(int[][] matrix) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < matrix.length; i++) {
            for (int j = 0; j < matrix[i].length; j++) {
                sb.append(matrix[i][j]);
                if (j < matrix[i].length - 1) {
                    sb.append(",");
                }
            }
            if (i < matrix.length - 1) {
                sb.append(";");
            }
        }
        return sb.toString();
    }
    @Override
    protected void onDestroy() {
        super.onDestroy();
        mHandler.removeCallbacks(taskGenerator);
    }
}
