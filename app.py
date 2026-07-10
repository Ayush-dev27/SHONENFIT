from flask import Flask, request, jsonify, session, send_from_directory 
from flask_cors import CORS
import sqlite3
import hashlib
from datetime import datetime

# Import both core engines you built
from generator import generate_custom_routine
from progression import process_workout_log

app = Flask(__name__)
app.secret_key = 'shonenfit-dev-secret'
CORS(app, supports_credentials=True)

DATABASE_FILE = 'shonenfit.db'

CHARACTER_DISPLAY_NAMES = {
    'itadori': 'Yuji Itadori',
    'toji': 'Toji Fushiguro',
    'maki': 'Maki Zenin',
    'tanjiro': 'Tanjiro Kamado',
    'tengen': 'Tengen Uzui',
    'inosuke': 'Inosuke Hashibira',
    'deku': 'Izuku Midoriya (Deku)',
    'bakugo': 'Katsuki Bakugo',
    'all-might': 'All Might (Prime)',
}

def ensure_database_tables():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            age INTEGER NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            current_grade TEXT DEFAULT 'Grade 4',
            total_exp INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            selected_universe TEXT NOT NULL,
            selected_character TEXT NOT NULL,
            training_strategy TEXT NOT NULL,
            age INTEGER NOT NULL,
            height_cm REAL NOT NULL,
            weight_kg REAL NOT NULL,
            medical_history TEXT,
            special_preferences TEXT,
            current_grade TEXT DEFAULT 'Grade 4',
            total_exp INTEGER DEFAULT 0,
            weekly_workout_count INTEGER DEFAULT 0,
            last_workout_logged_at TEXT,
            current_streak_weeks INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    history_columns = {
        row[1] for row in cursor.execute("PRAGMA table_info(workout_history)").fetchall()
    }

    if history_columns and 'user_id' not in history_columns:
        cursor.execute('''
            INSERT OR IGNORE INTO users (
                id, username, password_hash, age, weight, height, current_grade, total_exp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            1,
            'legacy_recruit',
            'local-dev-auth-pending',
            25,
            70,
            175,
            'Grade 4',
            0
        ))
        cursor.execute('ALTER TABLE workout_history RENAME TO workout_history_legacy')
        cursor.execute('''
            CREATE TABLE workout_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                character_id TEXT NOT NULL,
                paradigm TEXT NOT NULL,
                sets_completed INTEGER NOT NULL,
                exp_earned INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            INSERT INTO workout_history (
                id, user_id, character_id, paradigm, sets_completed, exp_earned, timestamp
            )
            SELECT id, 1, character_id, paradigm, sets_completed, exp_earned, timestamp
            FROM workout_history_legacy
        ''')
        cursor.execute('DROP TABLE workout_history_legacy')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            character_id TEXT NOT NULL,
            paradigm TEXT NOT NULL,
            sets_completed INTEGER NOT NULL,
            exp_earned INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


ensure_database_tables()

@app.route('/')
def index():
    # This serves your index.html file when you go to http://127.0.0.1:5000/
    return send_from_directory('.', 'index.html') 

@app.route('/<path:path>')
def serve_static(path):
    # This automatically catches requests for style.css, script.js, or images
    return send_from_directory('.', path) 

def upsert_user_account(cursor, username, age, weight, height, current_grade='Grade 4', total_exp=0, password_hash=None):
    safe_password_hash = password_hash or 'local-dev-auth-pending'
    cursor.execute('''
        INSERT OR IGNORE INTO users (
            username, password_hash, age, weight, height, current_grade, total_exp
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        username,
        safe_password_hash,
        age,
        weight,
        height,
        current_grade,
        total_exp
    ))
    cursor.execute('''
        UPDATE users
        SET age = ?,
            weight = ?,
            height = ?,
            current_grade = ?,
            total_exp = ?
        WHERE username = ?
    ''', (
        age,
        weight,
        height,
        current_grade,
        total_exp,
        username
    ))
    return cursor.execute(
        'SELECT id FROM users WHERE username = ?',
        (username,)
    ).fetchone()[0]

def calculate_streak(user_id=1):
    ensure_database_tables()

    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()
    rows = cursor.execute('''
        SELECT DISTINCT DATE(timestamp) AS training_date
        FROM workout_history
        WHERE user_id = ?
        ORDER BY training_date DESC
    ''', (user_id,)).fetchall()
    conn.close()

    if not rows:
        return 0

    training_dates = [
        datetime.strptime(row[0], '%Y-%m-%d').date()
        for row in rows
        if row[0]
    ]

    if not training_dates:
        return 0

    today = datetime.now().date()
    most_recent = training_dates[0]

    if (today - most_recent).days > 2:
        return 0

    streak_count = 1
    previous_date = most_recent

    for training_date in training_dates[1:]:
        if (previous_date - training_date).days <= 2:
            streak_count += 1
            previous_date = training_date
        else:
            break

    return streak_count

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json(silent=True) or {}
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''
        age = int(data.get('age', 25))
        weight = float(data.get('weight', 70))
        height = float(data.get('height', 175))

        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password are required."}), 400

        ensure_database_tables()

        conn = sqlite3.connect(DATABASE_FILE)
        conn.execute('PRAGMA foreign_keys = ON')
        cursor = conn.cursor()

        existing_user = cursor.execute(
            'SELECT id FROM users WHERE username = ?',
            (username,)
        ).fetchone()

        if existing_user:
            conn.close()
            return jsonify({"status": "error", "message": "Username already exists."}), 409

        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (
                username, password_hash, age, weight, height, current_grade, total_exp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            password_hash,
            age,
            weight,
            height,
            'Grade 4',
            0
        ))
        user_id = cursor.lastrowid

        conn.commit()
        conn.close()

        session['user_id'] = user_id
        session['username'] = username

        return jsonify({
            "status": "success",
            "message": "Account created successfully.",
            "user": {
                "id": user_id,
                "username": username,
                "age": age,
                "weight": weight,
                "height": height,
                "current_grade": "Grade 4"
            }
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json(silent=True) or {}
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''

        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password are required."}), 400

        ensure_database_tables()

        conn = sqlite3.connect(DATABASE_FILE)
        conn.execute('PRAGMA foreign_keys = ON')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        user = cursor.execute(
            'SELECT id, username, password_hash, age, weight, height, current_grade, total_exp FROM users WHERE username = ?',
            (username,)
        ).fetchone()

        conn.close()

        if not user or not verify_password(password, user['password_hash']):
            return jsonify({"status": "error", "message": "Invalid username or password."}), 401

        session['user_id'] = user['id']
        session['username'] = user['username']

        return jsonify({
            "status": "success",
            "message": "Logged in successfully.",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "age": user['age'],
                "weight": user['weight'],
                "height": user['height'],
                "current_grade": user['current_grade']
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'GET':
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401
        return jsonify({"status": "success", "user_id": user_id})

    try:
        data = request.get_json(silent=True) or {}

        username = data.get('username', 'Recruit')
        selected_universe = data.get('selectedUniverse')
        selected_character = data.get('selectedCharacter')
        training_strategy = data.get('strategyGoal')
        age = int(data.get('age', 25))
        height = float(data.get('height', 175))
        weight = float(data.get('weight', 70))
        medical_history = data.get('medicalHistory', '')
        special_preferences = data.get('specialPreferences', '')

        ensure_database_tables()

        conn = sqlite3.connect(DATABASE_FILE)
        conn.execute('PRAGMA foreign_keys = ON')
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

        user_account_id = upsert_user_account(
            cursor,
            username=username,
            age=age,
            weight=weight,
            height=height,
            current_grade='Grade 4',
            total_exp=0,
            password_hash=data.get('password_hash') or data.get('passwordHash')
        )

        session['user_id'] = user_account_id
        session['username'] = username

        conn.commit()
        conn.close()

        routine_payload = generate_custom_routine(data)

        return jsonify({
            "status": "success",
            "message": "Profile synced to database and custom pipeline initialized!",
            "initial_grade": "Grade 4",
            "current_streak": calculate_streak(user_account_id),
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


@app.route('/api/workout-complete', methods=['POST'])
def complete_workout():
    try:
        data = request.get_json() or {}
        character_id = data.get('character_id')
        sets_completed = data.get('sets_completed')

        if character_id is None or sets_completed is None:
            return jsonify({
                "status": "error",
                "message": "character_id and sets_completed are required."
            }), 400

        sets_completed = int(sets_completed)
        ensure_database_tables()

        conn = sqlite3.connect(DATABASE_FILE)
        conn.execute('PRAGMA foreign_keys = ON')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        user = cursor.execute(
            'SELECT * FROM user_profiles ORDER BY id DESC LIMIT 1'
        ).fetchone()

        if not user:
            conn.close()
            return jsonify({
                "status": "error",
                "message": "User profile not found. Complete initialization first!"
            }), 404

        user_account_id = upsert_user_account(
            cursor,
            username=user['username'],
            age=user['age'],
            weight=user['weight_kg'],
            height=user['height_cm'],
            current_grade=user['current_grade'],
            total_exp=user['total_exp']
        )

        workout_logged_today = cursor.execute('''
            SELECT id
            FROM workout_history
            WHERE user_id = ?
              AND date(timestamp) = date('now', 'localtime')
            LIMIT 1
        ''', (user_account_id,)).fetchone()

        if workout_logged_today:
            conn.close()
            return jsonify({
                "status": "error",
                "message": "Daily training cap reached! Rest and recovery are mandatory parts of a Shonen training arc."
            }), 400

        new_exp = 250
        current_total_exp = int(user['total_exp'] or 0)
        total_exp = current_total_exp + new_exp

        grade_number = max(1, 4 - (total_exp // 1000))
        current_grade = f"Grade {grade_number}"
        xp_to_next_level = 1000 - (total_exp % 1000)
        if xp_to_next_level == 1000:
            xp_to_next_level = 0 if grade_number == 1 else 1000

        paradigm = data.get('paradigm') or user['training_strategy'] or 'train-like'

        cursor.execute('''
            UPDATE user_profiles
            SET total_exp = ?,
                current_grade = ?
            WHERE id = ?
        ''', (
            total_exp,
            current_grade,
            user['id']
        ))

        cursor.execute('''
            UPDATE users
            SET total_exp = ?,
                current_grade = ?
            WHERE id = ?
        ''', (
            total_exp,
            current_grade,
            user_account_id
        ))

        cursor.execute('''
            INSERT INTO workout_history (
                user_id, character_id, paradigm, sets_completed, exp_earned
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            user_account_id,
            character_id,
            paradigm,
            sets_completed,
            new_exp
        ))

        conn.commit()
        conn.close()

        current_streak = calculate_streak(user_account_id)

        return jsonify({
            "status": "success",
            "new_exp": new_exp,
            "total_exp": total_exp,
            "current_grade": current_grade,
            "xp_to_next_level": xp_to_next_level,
            "current_streak": current_streak
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/workout-history', methods=['GET'])
def get_workout_history():
    try:
        ensure_database_tables()

        conn = sqlite3.connect(DATABASE_FILE)
        conn.execute('PRAGMA foreign_keys = ON')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        username = request.args.get('username')
        if username:
            user_account = cursor.execute(
                'SELECT id FROM users WHERE username = ?',
                (username,)
            ).fetchone()
        else:
            latest_profile = cursor.execute(
                'SELECT username FROM user_profiles ORDER BY id DESC LIMIT 1'
            ).fetchone()
            user_account = cursor.execute(
                'SELECT id FROM users WHERE username = ?',
                (latest_profile['username'],)
            ).fetchone() if latest_profile else cursor.execute(
                'SELECT id FROM users ORDER BY id DESC LIMIT 1'
            ).fetchone()

        if not user_account:
            conn.close()
            return jsonify([]), 200

        rows = cursor.execute('''
            SELECT id, user_id, character_id, paradigm, sets_completed, exp_earned, timestamp
            FROM workout_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
        ''', (user_account['id'],)).fetchall()

        history = []
        for row in rows:
            character_id = row['character_id']
            character_name = CHARACTER_DISPLAY_NAMES.get(character_id, character_id)
            paradigm = row['paradigm']
            sets_completed = row['sets_completed']
            exp_earned = row['exp_earned']
            timestamp = row['timestamp']

            history.append({
                "id": row['id'],
                "user_id": row['user_id'],
                "character_id": character_id,
                "character_name": character_name,
                "paradigm": paradigm,
                "sets_completed": sets_completed,
                "exp_earned": exp_earned,
                "timestamp": timestamp,
                "summary": f"{character_name} completed {sets_completed} sets via {paradigm} and earned {exp_earned} EXP."
            })

        conn.close()
        return jsonify(history), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000) 
