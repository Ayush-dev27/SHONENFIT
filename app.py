from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3 

from generator import generate_custom_routine 

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing so our JS frontend can hit this API

DATABASE_FILE = 'shonenfit.db'

@app.route('/api/profile', methods=['POST'])
def create_profile():
    try:
        data = request.get_json()
        
        # Extract frontend session payload parameters
        username = data.get('username', 'Recruit')
        selected_universe = data.get('selectedUniverse')
        selected_character = data.get('selectedCharacter')
        training_strategy = data.get('strategyGoal')
        age = int(data.get('age'))
        height = float(data.get('height'))
        weight = float(data.get('weight'))
        medical_history = data.get('medicalHistory', '')
        special_preferences = data.get('specialPreferences', '')
        
        # Connect to SQLite and write the data row
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
        
        return jsonify({
            "status": "success",
            "message": "Profile synced to database. Welcome to Grade 4!",
            "initial_grade": "Grade 4"
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    # Run server locally on http://127.0.0.1:5000
    app.run(debug=True, port=5000) 