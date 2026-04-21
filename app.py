from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import sqlite3
from datetime import datetime
import os
import tempfile

# Load model
model = joblib.load('model.joblib')
features = ['work_hours', 'screen_time_hours', 'meetings_count', 'breaks_taken', 'after_hours_work', 'task_completion_rate', 'day_type_encoded', 'sleep_category_encoded']

app = Flask(__name__)

db_path = os.path.join(tempfile.gettempdir(), 'burnout.db')

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        work_hours REAL,
        screen_time_hours REAL,
        meetings_count INTEGER,
        breaks_taken INTEGER,
        after_hours_work INTEGER,
        task_completion_rate REAL,
        day_type_encoded INTEGER,
        sleep_category_encoded INTEGER,
        result TEXT,
        confidence REAL
    )''')
    conn.commit()
    conn.close()

create_table()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        required_fields = ['work_hours', 'screen_time_hours', 'meetings_count', 'breaks_taken', 'after_hours_work', 'task_completion_rate', 'day_type_encoded', 'sleep_category_encoded']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        work_hours = float(data['work_hours'])
        screen_time_hours = float(data['screen_time_hours'])
        meetings_count = int(data['meetings_count'])
        breaks_taken = int(data['breaks_taken'])
        after_hours_work = int(data['after_hours_work'])
        task_completion_rate = float(data['task_completion_rate'])
        day_type_encoded = int(data['day_type_encoded'])
        sleep_category_encoded = int(data['sleep_category_encoded'])

        input_data = pd.DataFrame([[work_hours, screen_time_hours, meetings_count, breaks_taken, after_hours_work, task_completion_rate, day_type_encoded, sleep_category_encoded]], columns=features)

        prediction = model.predict(input_data)[0]
        confidence = model.predict_proba(input_data)[0][prediction]

        result_map = {0: 'Low', 1: 'Medium', 2: 'High'}
        result = result_map.get(prediction, 'Unknown')

        timestamp = datetime.now().isoformat()
        conn = get_db_connection()
        conn.execute('INSERT INTO history (timestamp, work_hours, screen_time_hours, meetings_count, breaks_taken, after_hours_work, task_completion_rate, day_type_encoded, sleep_category_encoded, result, confidence) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (timestamp, work_hours, screen_time_hours, meetings_count, breaks_taken, after_hours_work, task_completion_rate, day_type_encoded, sleep_category_encoded, result, confidence))
        conn.commit()
        conn.close()

        return jsonify({'result': result, 'confidence': confidence})

    except ValueError as e:
        return jsonify({'error': f'Invalid input data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/history')
def history():
    try:
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM history ORDER BY id DESC LIMIT 10').fetchall()
        conn.close()
        history_list = [dict(row) for row in rows]
        return jsonify({'history': history_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5055)