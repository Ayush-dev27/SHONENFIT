from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

# Import both core engines you built
from generator import generate_custom_routine
from progression import process_workout_log

app = Flask(__name__)
CORS(app)

DATABASE_FILE = 'shonenfit.db'

@app.route('/api/profile', methods=['POST'])
def create_profile():
    try:
        data = request.get_json()
        
        username = data.get('username', 'Recruit')
        selected_universe = data.get('selectedUniverse')
        selected_character = data.get('selectedCharacter')
        training_strategy = data.get('strategyGoal')
        age = int(data.get('age'))
        height = float(data.get('height'))
        weight = float(data.get('weight'))
        medical_history = data.get('medicalHistory', '')
        special_preferences = data.get('specialPreferences', '')
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_profiles (
                username, selected_universe, selected_character, training_strategy,
                age, height_cm, weight_kg, medical_history, special_preferences
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username, selected_universe, selected_character, training_strategy,
            age, height, weight, medical_history, special_preferences
        ))
        
        conn.commit()
        conn.close()
        
        routine_payload = generate_custom_routine(data)
        
        return jsonify({
            "status": "success",
            "message": "Profile synced to database and custom pipeline initialized!",
            "initial_grade": "Grade 4",
            "workout_data": routine_payload
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/workout/log', methods=['POST'])
def log_workout():
    """
    API endpoint that pulls a user's current metrics from the database,
    processes them through our progression time-lock and math rules,
    and updates their row with the newly calculated EXP, streak, and grade.
    """
    try:
        data = request.get_json()
        username = data.get('username', 'Recruit')
        
        # 1. Fetch current user metrics from shonenfit.db
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row  # Access columns by name strings
        cursor = conn.cursor()
        
        user = cursor.execute(
            'SELECT * FROM user_profiles WHERE username = ? ORDER BY id DESC LIMIT 1', 
            (username,)
        ).fetchone()
        
        if not user:
            return jsonify({"status": "error", "message": "User profile not found. Complete initialization first!"}), 404
            
        # 2. Extract state metrics to feed to our math logic module
        current_exp = user['total_exp']
        current_grade = user['current_grade']
        last_logged_str = user['last_workout_logged_at']
        weekly_count = user['weekly_workout_count']
        current_streak = user['current_streak_weeks']
        
        # 3. Process the calculations via progression.py
        calc_result = process_workout_log(
            current_exp, current_grade, last_logged_str, weekly_count, current_streak
        )
        
        # If the 24-hour time lock catches an anti-cheat event, halt and return early
        if calc_result['status'] == 'locked':
            conn.close()
            return jsonify(calc_result), 200
            
        # 4. Save the calculated metrics back to the user row in the database
        cursor.execute('''
            UPDATE user_profiles 
            SET total_exp = ?, 
                current_grade = ?, 
                weekly_workout_count = ?, 
                last_workout_logged_at = ?
            WHERE id = ?
        ''', (
            calc_result['total_exp'],
            calc_result['current_grade'],
            calc_result['weekly_count'],
            calc_result['timestamp_iso'],
            user['id']
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify(calc_result), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000) 