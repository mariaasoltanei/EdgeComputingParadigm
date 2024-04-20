@app.route('/submit_task', methods=['POST'])
def submit_task():
    data = request.json
    task_details = {
        'matrix_size_a': data['matrix_size_a'],
        'matrix_size_b': data['matrix_size_b'],
        'submission_time': datetime.now()
    }
    # Store task details in MongoDB
    task_id = historical_data.insert_one(task_details).inserted_id
    return jsonify({'task_id': str(task_id)}), 201

@app.route('/process_task', methods=['POST'])
def process_task():
    data = request.json
    task_id = data['task_id']
    # Process task (not implemented)
    # For demonstration, let's assume task processing takes 5 seconds
    processing_time = 5
    # Update historical data with execution time
    historical_data.update_one({'_id': task_id}, {'$set': {'execution_time': processing_time}})
    return jsonify({'message': 'Task processed successfully'}), 200