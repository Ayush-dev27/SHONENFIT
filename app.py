from flask import Flask, request, jsonify, session, send_from_directory 
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import hashlib
import os
from datetime import datetime, timezone, timedelta
from database import log_workout_session
from progression import calculate_fatigue_status 
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

CHARACTER_UNIVERSE_MAP = {
    'itadori': 'jjk',
    'yuji': 'jjk',
    'toji': 'jjk',
    'maki': 'jjk',
    'tanjiro': 'demon-slayer',
    'tengen': 'demon-slayer',
    'inosuke': 'demon-slayer',
    'deku': 'mha',
    'bakugo': 'mha',
    'all-might': 'mha',
}

UNIVERSE_DISPLAY_NAMES = {
    'jjk': 'Jujutsu Kaisen',
    'demon-slayer': 'Demon Slayer',
    'mha': 'My Hero Academia',
}

CHARACTER_IMAGES = {
    'itadori': 'images/itadori.jpg',
    'toji': 'images/toji.jpg',
    'maki': 'images/maki.jpg',
    'tanjiro': 'images/tanjiro.jpg',
    'tengen': 'images/tengen.jpg',
    'inosuke': 'images/inosuke.jpg',
    'deku': 'images/deku.jpg',
    'bakugo': 'images/bakugo.jpg',
    'all-might': 'images/all-might.jpg',
}

CHARACTER_TEMPLATES_KEYS = list(CHARACTER_DISPLAY_NAMES.keys())

CANONICAL_CHARACTERS = [
    'itadori',
    'toji',
    'maki',
    'tanjiro',
    'tengen',
    'inosuke',
    'deku',
    'bakugo',
    'all-might',
]

CHARACTER_ALIAS_MAP = {
    'all-might': 'all-might',
    'all_might': 'all-might',
    'allmight': 'all-might',
    'all might': 'all-might',
    'all might (prime)': 'all-might',
    'all': 'all-might',
    'might': 'all-might',
    'yuji': 'itadori',
    'itadori': 'itadori',
    'yuji itadori': 'itadori',
    'toji': 'toji',
    'fushiguro': 'toji',
    'toji fushiguro': 'toji',
    'maki': 'maki',
    'zenin': 'maki',
    'maki zenin': 'maki',
    'tanjiro': 'tanjiro',
    'kamado': 'tanjiro',
    'tanjiro kamado': 'tanjiro',
    'tengen': 'tengen',
    'uzui': 'tengen',
    'tengen uzui': 'tengen',
    'inosuke': 'inosuke',
    'hashibira': 'inosuke',
    'inosuke hashibira': 'inosuke',
    'deku': 'deku',
    'izuku': 'deku',
    'midoriya': 'deku',
    'izuku midoriya': 'deku',
    'izuku midoriya (deku)': 'deku',
    'bakugo': 'bakugo',
    'katsuki': 'bakugo',
    'katsuki bakugo': 'bakugo',
}

def normalize_character_id(raw_char: str) -> str:
    if not raw_char:
        return 'toji'
    clean = str(raw_char).lower().strip()
    if clean in CHARACTER_ALIAS_MAP:
        return CHARACTER_ALIAS_MAP[clean]

    # Keyword / token matching for robust matching
    if 'might' in clean:
        return 'all-might'
    if 'yuji' in clean or 'itadori' in clean:
        return 'itadori'
    if 'toji' in clean or 'fushiguro' in clean:
        return 'toji'
    if 'maki' in clean or 'zenin' in clean:
        return 'maki'
    if 'tanjiro' in clean or 'kamado' in clean:
        return 'tanjiro'
    if 'tengen' in clean or 'uzui' in clean:
        return 'tengen'
    if 'inosuke' in clean or 'hashibira' in clean:
        return 'inosuke'
    if 'deku' in clean or 'midoriya' in clean or 'izuku' in clean:
        return 'deku'
    if 'bakugo' in clean or 'katsuki' in clean:
        return 'bakugo'

    # Fallback slug match
    slug = clean.replace(' ', '-').replace('_', '-')
    for k in CANONICAL_CHARACTERS:
        if k in slug:
            return k

    return clean

def normalize_universe_id(raw_uni: str, character_id: str = None) -> str:
    clean = str(raw_uni or '').lower().strip()
    if 'jujutsu' in clean or clean == 'jjk':
        return 'jjk'
    if 'demon' in clean or clean == 'demon-slayer':
        return 'demon-slayer'
    if 'hero' in clean or clean == 'mha':
        return 'mha'
    if character_id:
        canon_c = normalize_character_id(character_id)
        return CHARACTER_UNIVERSE_MAP.get(canon_c, 'jjk')
    return 'jjk'

def normalize_mode_id(raw_mode: str) -> str:
    clean = str(raw_mode or 'train-like').lower().replace('_', '-').strip()
    return 'physique' if 'physique' in clean else 'train-like'

def calculate_grade_from_exp(total_exp: int):
    """
    Authoritative grade and threshold calculation matching frontend thresholds:
    - Special Grade: 10,000+ EXP
    - Grade 1: 5,000 - 9,999 EXP
    - Grade 2: 2,500 - 4,999 EXP
    - Grade 3: 1,000 - 2,499 EXP
    - Grade 4: 0 - 999 EXP
    """
    exp = max(0, int(total_exp or 0))
    if exp >= 10000:
        return "Special Grade", 0
    elif exp >= 5000:
        return "Grade 1", 10000 - exp
    elif exp >= 2500:
        return "Grade 2", 5000 - exp
    elif exp >= 1000:
        return "Grade 3", 2500 - exp
    else:
        return "Grade 4", 1000 - exp

def get_db_connection(timeout=30.0):
    conn = sqlite3.connect(DATABASE_FILE, timeout=timeout)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def ensure_database_tables():
    conn = get_db_connection(timeout=30.0)
    try:
        conn.execute('PRAGMA journal_mode=WAL')
    except Exception:
        pass
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_journeys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            universe TEXT NOT NULL,
            character_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            completed_workouts INTEGER DEFAULT 0,
            current_track TEXT DEFAULT 'track_a',
            last_activity_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, universe, character_id, mode)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS idempotency_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idempotency_key TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            endpoint TEXT NOT NULL,
            response_body TEXT NOT NULL,
            status_code INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Safe idempotent migration and deduplication for training_journeys
    try:
        all_journeys = cursor.execute('''
            SELECT id, user_id, universe, character_id, mode, completed_workouts, current_track, last_activity_at
            FROM training_journeys
        ''').fetchall()

        for j in all_journeys:
            j_id = j[0]
            u_id = j[1]
            raw_u = j[2]
            raw_c = j[3]
            raw_m = j[4]
            workouts_cnt = int(j[5] or 0)
            cur_track = j[6]
            last_ts = j[7]

            canon_c = normalize_character_id(raw_c)
            canon_u = normalize_universe_id(raw_u, canon_c)
            canon_m = normalize_mode_id(raw_m)

            if raw_c != canon_c or raw_u != canon_u or raw_m != canon_m:
                canonical_row = cursor.execute('''
                    SELECT id, completed_workouts, current_track, last_activity_at
                    FROM training_journeys
                    WHERE user_id = ? AND universe = ? AND character_id = ? AND mode = ? AND id != ?
                ''', (u_id, canon_u, canon_c, canon_m, j_id)).fetchone()

                if canonical_row:
                    canon_row_id = canonical_row[0]
                    canon_cnt = int(canonical_row[1] or 0)
                    canon_ts = str(canonical_row[3] or '')
                    best_workouts = max(canon_cnt, workouts_cnt)
                    t_idx = best_workouts % 4
                    t_track = f"track_{chr(97 + t_idx)}"
                    best_ts = max(canon_ts, str(last_ts or ''))

                    cursor.execute('''
                        UPDATE training_journeys
                        SET completed_workouts = ?, current_track = ?, last_activity_at = ?
                        WHERE id = ?
                    ''', (best_workouts, t_track, best_ts, canon_row_id))

                    cursor.execute('DELETE FROM training_journeys WHERE id = ?', (j_id,))
                else:
                    cursor.execute('''
                        UPDATE training_journeys
                        SET universe = ?, character_id = ?, mode = ?
                        WHERE id = ?
                    ''', (canon_u, canon_c, canon_m, j_id))
    except Exception as e:
        pass

    # Safe idempotent backfill for existing workout_history records
    try:
        existing_groups = cursor.execute('''
            SELECT user_id, character_id, paradigm, COUNT(*) as cnt, MAX(timestamp) as last_ts
            FROM workout_history
            GROUP BY user_id, character_id, paradigm
        ''').fetchall()
        for g in existing_groups:
            uid = g[0]
            raw_c = str(g[1] or '').lower().strip()
            c_key = normalize_character_id(raw_c)
            p_mode = normalize_mode_id(str(g[2] or ''))
            u_key = normalize_universe_id(CHARACTER_UNIVERSE_MAP.get(c_key, 'jjk'), c_key)
            c_count = g[3]
            t_idx = c_count % 4
            c_track = f"track_{chr(97 + t_idx)}"
            l_ts = g[4] or datetime.now().isoformat()
            cursor.execute('''
                INSERT OR IGNORE INTO training_journeys (
                    user_id, universe, character_id, mode, completed_workouts, current_track, last_activity_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (uid, u_key, c_key, p_mode, c_count, c_track, l_ts))
    except Exception as e:
        pass

    # Safe idempotent progression consistency repair:
    # If a user's total_exp in users table is less than SUM(exp_earned) from verified workout_history,
    # safely repair users.total_exp and users.current_grade to reflect genuine successful history.
    try:
        user_sums = cursor.execute('''
            SELECT u.id, u.username, u.total_exp, COALESCE(SUM(w.exp_earned), 0) as hist_exp
            FROM users u
            JOIN workout_history w ON u.id = w.user_id
            GROUP BY u.id
        ''').fetchall()
        for u_row in user_sums:
            u_id, u_name, current_exp, hist_exp = u_row[0], u_row[1], int(u_row[2] or 0), int(u_row[3] or 0)
            if hist_exp > current_exp:
                correct_grade, _ = calculate_grade_from_exp(hist_exp)
                cursor.execute('''
                    UPDATE users
                    SET total_exp = ?, current_grade = ?
                    WHERE id = ?
                ''', (hist_exp, correct_grade, u_id))
                cursor.execute('''
                    UPDATE user_profiles
                    SET total_exp = ?, current_grade = ?
                    WHERE id = (SELECT id FROM user_profiles WHERE username = ? ORDER BY id DESC LIMIT 1)
                ''', (hist_exp, correct_grade, u_name))
    except Exception as e:
        pass

    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash or not password:
        return False
    if password_hash.startswith('pbkdf2:') or password_hash.startswith('scrypt:'):
        return check_password_hash(password_hash, password)
    # Legacy unsalted SHA-256 fallback for existing accounts
    return hashlib.sha256(password.encode('utf-8')).hexdigest() == password_hash


ensure_database_tables()

@app.route('/')
def index():
    # This serves your index.html file when you go to http://127.0.0.1:5000/
    return send_from_directory('.', 'index.html') 

@app.route('/<path:path>')
def serve_static(path):
    # This automatically catches requests for style.css, script.js, images, or falls back to SPA index.html
    if os.path.exists(path) and os.path.isfile(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')


def resolve_request_user(cursor):
    """
    Authoritatively resolves the currently authenticated user strictly from the session.
    Never trusts client-provided user_id or username parameters as identity.
    """
    session_user_id = session.get('user_id')
    if session_user_id:
        try:
            acc = cursor.execute('SELECT * FROM users WHERE id = ?', (int(session_user_id),)).fetchone()
            if acc:
                return acc
        except (ValueError, TypeError):
            pass

    session_username = session.get('username')
    if session_username:
        acc = cursor.execute('SELECT * FROM users WHERE username = ?', (str(session_username),)).fetchone()
        if acc:
            return acc

    return None

def format_journey_dict(row, is_active=False):
    char_id = normalize_character_id(row['character_id'])
    uni_id = normalize_universe_id(row['universe'], char_id)
    mode_id = normalize_mode_id(row['mode'])
    completed_workouts = int(row['completed_workouts'] or 0)
    track_idx = completed_workouts % 4
    track_key = f"track_{chr(97 + track_idx)}"
    track_name = f"Track {chr(65 + track_idx)}"

    return {
        'id': row['id'],
        'user_id': row['user_id'],
        'universe': uni_id,
        'universe_name': UNIVERSE_DISPLAY_NAMES.get(uni_id, uni_id),
        'character_id': char_id,
        'character_name': CHARACTER_DISPLAY_NAMES.get(char_id, char_id.title()),
        'mode': mode_id,
        'mode_label': 'Physique Like Them' if mode_id == 'physique' else 'Train Like Them',
        'completed_workouts': completed_workouts,
        'current_day': completed_workouts + 1,
        'current_track': track_key,
        'current_track_name': track_name,
        'last_activity_at': row['last_activity_at'],
        'image': CHARACTER_IMAGES.get(char_id, 'images/toji.jpg'),
        'is_active': is_active
    }

def get_or_create_journey(cursor, user_id, universe, character_id, mode):
    char_key = normalize_character_id(character_id)
    uni_key = normalize_universe_id(universe, char_key)
    mode_key = normalize_mode_id(mode)

    completed_count = cursor.execute('''
        SELECT COUNT(*) FROM workout_history 
        WHERE user_id = ? AND character_id = ? AND paradigm = ?
    ''', (user_id, char_key, mode_key)).fetchone()[0]

    track_idx = completed_count % 4
    current_track = f"track_{chr(97 + track_idx)}"

    cursor.execute('''
        INSERT INTO training_journeys (
            user_id, universe, character_id, mode, completed_workouts, current_track, last_activity_at
        ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, universe, character_id, mode) DO UPDATE SET
            completed_workouts = excluded.completed_workouts,
            current_track = excluded.current_track,
            last_activity_at = CURRENT_TIMESTAMP
    ''', (user_id, uni_key, char_key, mode_key, completed_count, current_track))

    journey_row = cursor.execute('''
        SELECT id, user_id, universe, character_id, mode, completed_workouts, current_track, last_activity_at, created_at
        FROM training_journeys 
        WHERE user_id = ? AND universe = ? AND character_id = ? AND mode = ?
    ''', (user_id, uni_key, char_key, mode_key)).fetchone()

    if isinstance(journey_row, sqlite3.Row):
        journey_dict = dict(journey_row)
    elif journey_row:
        cols = ['id', 'user_id', 'universe', 'character_id', 'mode', 'completed_workouts', 'current_track', 'last_activity_at', 'created_at']
        journey_dict = dict(zip(cols, journey_row))
    else:
        journey_dict = {}

    return journey_dict, completed_count

def upsert_user_account(cursor, username, age, weight, height, current_grade=None, total_exp=None, password_hash=None):
    safe_password_hash = password_hash or 'local-dev-auth-pending'
    existing = cursor.execute(
        'SELECT id, current_grade, total_exp FROM users WHERE username = ?',
        (username,)
    ).fetchone()

    if existing:
        user_id = existing[0]
        if total_exp is not None and current_grade is not None:
            cursor.execute('''
                UPDATE users
                SET age = ?, weight = ?, height = ?, current_grade = ?, total_exp = ?
                WHERE id = ?
            ''', (age, weight, height, current_grade, total_exp, user_id))
        else:
            cursor.execute('''
                UPDATE users
                SET age = ?, weight = ?, height = ?
                WHERE id = ?
            ''', (age, weight, height, user_id))
        return user_id
    else:
        init_grade = current_grade or 'Grade 4'
        init_exp = total_exp if total_exp is not None else 0
        cursor.execute('''
            INSERT INTO users (
                username, password_hash, age, weight, height, current_grade, total_exp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            safe_password_hash,
            age,
            weight,
            height,
            init_grade,
            init_exp
        ))
        return cursor.lastrowid

def calculate_streak(user_id=1):
    conn = get_db_connection()
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

    today_local = datetime.now().date()
    today_utc = datetime.now(timezone.utc).date()
    most_recent = training_dates[0]

    # Check whether the most recent workout is from today or yesterday.
    # If the most recent workout was before yesterday (gap >= 2 days), the streak is broken (0).
    diff_days = min((today_local - most_recent).days, (today_utc - most_recent).days)
    if diff_days > 1:
        return 0

    streak_count = 1
    expected_previous_day = most_recent - timedelta(days=1)

    for training_date in training_dates[1:]:
        if training_date == expected_previous_day:
            streak_count += 1
            expected_previous_day -= timedelta(days=1)
        elif training_date > expected_previous_day:
            # Same calendar day (already filtered by DISTINCT, but defensive)
            continue
        else:
            # A missing calendar day breaks the consecutive streak immediately
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

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        user = cursor.execute(
            'SELECT id, username, password_hash, age, weight, height, current_grade, total_exp FROM users WHERE username = ?',
            (username,)
        ).fetchone()

        if not user or not verify_password(password, user['password_hash']):
            conn.close()
            return jsonify({"status": "error", "message": "Invalid username or password."}), 401

        # Transparent password upgrade for legacy SHA-256 hashes
        if not (user['password_hash'].startswith('pbkdf2:') or user['password_hash'].startswith('scrypt:')):
            try:
                new_hash = hash_password(password)
                cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_hash, user['id']))
                conn.commit()
            except Exception:
                pass

        conn.close()

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


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out successfully."}), 200


@app.route('/api/profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'GET':
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        user_account = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        user_profile = cursor.execute(
            'SELECT * FROM user_profiles WHERE username = ? ORDER BY id DESC LIMIT 1',
            (user_account['username'],)
        ).fetchone() if user_account else None

        completed_workouts_count = cursor.execute(
            'SELECT COUNT(*) FROM workout_history WHERE user_id = ?',
            (user_id,)
        ).fetchone()[0] if user_account else 0

        if user_account and user_profile:
            norm_c = normalize_character_id(user_profile['selected_character'])
            norm_m = normalize_mode_id(user_profile['training_strategy'])
            norm_u = normalize_universe_id(user_profile['selected_universe'], norm_c)

            journey_workouts_count = cursor.execute('''
                SELECT COUNT(*) FROM workout_history
                WHERE user_id = ? AND character_id = ? AND paradigm = ?
            ''', (user_id, norm_c, norm_m)).fetchone()[0]

            journey_row, _ = get_or_create_journey(cursor, user_id, norm_u, norm_c, norm_m)
            conn.commit()
            conn.close()

            profile_data = {
                'selectedUniverse': norm_u,
                'selectedCharacter': norm_c,
                'strategyGoal': norm_m,
                'age': user_profile['age'],
                'height': user_profile['height_cm'],
                'weight': user_profile['weight_kg'],
                'medicalHistory': user_profile['medical_history'],
                'specialPreferences': user_profile['special_preferences'],
                'user_id': user_id,
                'completed_workouts_count': journey_workouts_count,
            }
            routine_payload = generate_custom_routine(profile_data, completed_workouts_count=journey_workouts_count)
            return jsonify({
                "status": "success",
                "user_id": user_id,
                "profile": dict(user_profile),
                "journey": format_journey_dict(journey_row, is_active=True),
                "workout_data": routine_payload,
                "current_streak": calculate_streak(user_id),
                "completed_workouts_count": completed_workouts_count,
                "journey_completed_count": journey_workouts_count,
                "current_grade": user_account['current_grade'],
                "total_exp": user_account['total_exp']
            }), 200

        conn.close()
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "username": user_account['username'] if user_account else 'Recruit',
            "user": dict(user_account) if user_account else None,
            "completed_workouts_count": completed_workouts_count
        }), 200

    try:
        data = request.get_json(silent=True) or {}

        session_username = session.get('username')
        session_user_id = session.get('user_id')

        requested_username = (data.get('username') or '').strip()

        # If already authenticated, the session identity is authoritative
        if session_username:
            if requested_username and requested_username != session_username:
                return jsonify({
                    "status": "error",
                    "message": "Forbidden: Cannot modify another user's profile."
                }), 403
            username = session_username
        elif requested_username:
            username = requested_username
        else:
            username = 'Recruit'

        selected_universe = data.get('selectedUniverse')
        selected_character = data.get('selectedCharacter')
        training_strategy = data.get('strategyGoal')
        age = int(data.get('age', 25))
        height = float(data.get('height', 175))
        weight = float(data.get('weight', 70))
        medical_history = data.get('medicalHistory', '')
        special_preferences = data.get('specialPreferences', '')

        ensure_database_tables()

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        user_account_id = upsert_user_account(
            cursor,
            username=username,
            age=age,
            weight=weight,
            height=height,
            password_hash=data.get('password_hash') or data.get('passwordHash')
        )

        if session_user_id and user_account_id != session_user_id:
            conn.close()
            return jsonify({
                "status": "error",
                "message": "Forbidden: Cannot modify another user's profile."
            }), 403

        user_acc = cursor.execute(
            'SELECT current_grade, total_exp FROM users WHERE id = ?',
            (user_account_id,)
        ).fetchone()
        user_current_grade = user_acc['current_grade'] if user_acc else 'Grade 4'
        user_total_exp = int(user_acc['total_exp'] or 0) if user_acc else 0

        cursor.execute('''
            INSERT INTO user_profiles (
                username, selected_universe, selected_character, training_strategy,
                age, height_cm, weight_kg, medical_history, special_preferences,
                current_grade, total_exp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username, selected_universe, selected_character, training_strategy,
            age, height, weight, medical_history, special_preferences,
            user_current_grade, user_total_exp
        ))

        completed_workouts_count = cursor.execute(
            'SELECT COUNT(*) FROM workout_history WHERE user_id = ?',
            (user_account_id,)
        ).fetchone()[0]

        norm_c = normalize_character_id(selected_character)
        norm_m = normalize_mode_id(training_strategy)
        norm_u = normalize_universe_id(selected_universe, norm_c)

        journey_row, journey_workouts_count = get_or_create_journey(
            cursor, user_account_id, norm_u, norm_c, norm_m
        )

        session['user_id'] = user_account_id
        session['username'] = username

        conn.commit()
        conn.close()

        data['user_id'] = user_account_id
        data['completed_workouts_count'] = journey_workouts_count
        data['selectedUniverse'] = norm_u
        data['selectedCharacter'] = norm_c
        data['strategyGoal'] = norm_m
        routine_payload = generate_custom_routine(data, completed_workouts_count=journey_workouts_count)

        return jsonify({
            "status": "success",
            "message": "Profile synced to database and custom pipeline initialized!",
            "initial_grade": user_current_grade,
            "current_grade": user_current_grade,
            "total_exp": user_total_exp,
            "current_streak": calculate_streak(user_account_id),
            "completed_workouts_count": completed_workouts_count,
            "journey_completed_count": journey_workouts_count,
            "journey": format_journey_dict(journey_row, is_active=True),
            "workout_data": routine_payload
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/workout/log', methods=['POST'])
def log_workout():
    """
    API endpoint that pulls a user's current metrics from the database,
    processes them through our progression time-lock and math rules,
    logs granular set histories, and appends a dynamic fatigue status score.
    """
    try:
        ensure_database_tables()
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        auth_user = resolve_request_user(cursor)
        if not auth_user:
            conn.close()
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        data = request.get_json() or {}
        incoming_sets = data.get('sets', []) # Captured from the checked frontend items
        
        # 1. Fetch current user metrics from shonenfit.db
        cursor.execute(
            'SELECT * FROM user_profiles WHERE username = ? ORDER BY id DESC LIMIT 1',
            (auth_user['username'],)
        )
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({"status": "error", "message": "User profile not found. Complete initialization first."}), 404
            
        # 2. Extract state metrics to feed to our math logic module
        current_exp = user['total_exp']
        current_grade = user['current_grade']
        last_logged_str = user['last_workout_logged_at']
        weekly_count = user['weekly_workout_count']
        current_streak = user['current_streak_weeks']
        
        # 3. Process the core level progression calculations
        calc_result = process_workout_log(
            current_exp, current_grade, last_logged_str, weekly_count, current_streak
        )
        
        # If the 24-hour time lock catches an anti-cheat event, halt immediately
        if calc_result['status'] == 'locked':
            conn.close()
            return jsonify(calc_result), 200
            
        # 4. Success Pipeline: Save the granular set records to our new table
        if incoming_sets:
            log_workout_session(
                user_id=user['id'],
                universe=user['selected_universe'],
                character_name=user['selected_character'],
                sets_data=incoming_sets
            )
            
        # 5. Compute the real-time Fatigue Engine baseline score
        fatigue_metrics = calculate_fatigue_status(user['id'])
        
        # Inject the live balance metrics safely into our frontend response payload
        calc_result['fatigue_ratio'] = fatigue_metrics['ratio']
        calc_result['fatigue_status'] = fatigue_metrics['status']
        calc_result['fatigue_message'] = fatigue_metrics['message']
        
        # 6. Save the calculated metrics back to the user row in the database
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
    
@app.route('/api/complete-workout', methods=['POST'])
@app.route('/api/workout-complete', methods=['POST'])
def complete_workout():
    conn = None
    try:
        data = request.get_json(silent=True) or {}
        character_id = data.get('character') or data.get('character_id') or data.get('selected_character') or 'toji'
        track_param = data.get('track') or data.get('daily_track') or 'track_a'
        user_id_param = data.get('user_id') or data.get('userId')
        exp_earned = int(data.get('exp_earned') or data.get('exp') or data.get('exp_gained') or 250)

        # Enforce set completion requirements
        raw_sets = data.get('sets_completed')
        sets_list = data.get('sets')
        if raw_sets is not None:
            try:
                sets_completed = int(raw_sets)
            except (ValueError, TypeError):
                sets_completed = 0
        elif isinstance(sets_list, list) and len(sets_list) > 0:
            sets_completed = len(sets_list)
        else:
            sets_completed = 0

        if sets_completed <= 0:
            return jsonify({
                "success": False,
                "status": "incomplete",
                "message": "Workout incomplete. Complete all required sets before recording your training arc."
            }), 400

        paradigm = data.get('paradigm') or data.get('strategy') or data.get('strategyGoal') or 'train-like'

        ensure_database_tables()

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Authoritative session authentication
        auth_user = resolve_request_user(cursor)
        if not auth_user:
            conn.close()
            return jsonify({"success": False, "status": "error", "message": "Unauthorized"}), 401

        # 2. Prevent user identity spoofing
        if user_id_param and str(user_id_param).isdigit() and int(user_id_param) != auth_user['id']:
            conn.close()
            return jsonify({"success": False, "status": "error", "message": "Forbidden: Cannot log workouts for another user"}), 403

        user_account_id = auth_user['id']
        username = auth_user['username']

        # 3. Check idempotency key for request deduplication
        idempotency_key = request.headers.get('X-Idempotency-Key') or data.get('idempotency_key')
        if idempotency_key:
            cached = cursor.execute(
                'SELECT response_body, status_code FROM idempotency_keys WHERE idempotency_key = ? AND user_id = ?',
                (str(idempotency_key), user_account_id)
            ).fetchone()
            if cached:
                conn.close()
                import json
                return jsonify(json.loads(cached['response_body'])), cached['status_code']

        # 4. Acquire immediate write lock for atomic execution
        conn.isolation_level = None
        conn.execute('BEGIN IMMEDIATE')

        user_account = cursor.execute('SELECT * FROM users WHERE id = ?', (user_account_id,)).fetchone()
        user = cursor.execute('SELECT * FROM user_profiles WHERE username = ? ORDER BY id DESC LIMIT 1', (username,)).fetchone()

        age = user['age'] if user else (user_account['age'] or 25)
        weight = user['weight_kg'] if user else (user_account['weight'] or 70.0)
        height = user['height_cm'] if user else (user_account['height'] or 175.0)
        current_grade = user_account['current_grade'] or (user['current_grade'] if user else 'Grade 4')
        current_total_exp = int(user_account['total_exp'] or 0)

        # ------------------------------------------------------------------
        # CRITICAL: 24-HOUR WORKOUT RESTRICTION ENFORCEMENT
        # Authoritative database check on persisted workout history
        # ------------------------------------------------------------------
        latest_history = cursor.execute('''
            SELECT timestamp, (julianday('now') - julianday(timestamp)) * 24.0 AS hours_elapsed
            FROM workout_history
            WHERE user_id = ?
            ORDER BY id DESC LIMIT 1
        ''', (user_account_id,)).fetchone()

        last_hours_elapsed = None
        if latest_history and latest_history['hours_elapsed'] is not None:
            last_hours_elapsed = float(latest_history['hours_elapsed'])
        elif user and user['last_workout_logged_at']:
            try:
                raw_time = str(user['last_workout_logged_at']).replace('Z', '+00:00')
                last_time = datetime.fromisoformat(raw_time)
                if last_time.tzinfo is None:
                    last_time = last_time.replace(tzinfo=timezone.utc)
                now_utc = datetime.now(timezone.utc)
                last_hours_elapsed = (now_utc - last_time).total_seconds() / 3600.0
            except Exception:
                last_hours_elapsed = None

        if last_hours_elapsed is not None and last_hours_elapsed < 24.0:
            conn.execute('ROLLBACK')
            conn.close()
            remaining_hours = max(0.0, 24.0 - last_hours_elapsed)
            hours = int(remaining_hours)
            minutes = int((remaining_hours - hours) * 60)
            return jsonify({
                "success": False,
                "status": "locked",
                "message": f"Daily training cap reached! You have already registered a workout within the last 24 hours. Recovery is mandatory before your next training arc. Cooldown active for {hours}h {minutes}m.",
                "time_remaining_seconds": int(remaining_hours * 3600),
                "total_exp": current_total_exp,
                "current_grade": current_grade,
                "exp_earned": 0,
                "exp": 0
            }), 200

        # Unlocked: Award EXP and persist completed session atomically
        total_exp = current_total_exp + exp_earned
        current_grade, xp_to_next_level = calculate_grade_from_exp(total_exp)

        if user:
            cursor.execute('''
                UPDATE user_profiles
                SET total_exp = ?,
                    current_grade = ?,
                    weekly_workout_count = COALESCE(weekly_workout_count, 0) + 1,
                    last_workout_logged_at = CURRENT_TIMESTAMP
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
                user_id, character_id, paradigm, sets_completed, exp_earned, timestamp
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            user_account_id,
            character_id,
            paradigm,
            sets_completed,
            exp_earned
        ))

        completed_workouts_count = cursor.execute(
            'SELECT COUNT(*) FROM workout_history WHERE user_id = ?',
            (user_account_id,)
        ).fetchone()[0]

        norm_char = normalize_character_id(character_id)
        norm_mode = normalize_mode_id(paradigm)
        norm_uni = normalize_universe_id(user['selected_universe'] if user else None, norm_char)

        # Authoritative count of completed workouts for THIS character/mode journey
        journey_workouts_count = cursor.execute('''
            SELECT COUNT(*) FROM workout_history
            WHERE user_id = ? AND character_id = ? AND paradigm = ?
        ''', (user_account_id, norm_char, norm_mode)).fetchone()[0]

        next_track_idx = journey_workouts_count % 4
        next_track_key = f"track_{chr(97 + next_track_idx)}"

        cursor.execute('''
            INSERT INTO training_journeys (
                user_id, universe, character_id, mode, completed_workouts, current_track, last_activity_at
            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, universe, character_id, mode) DO UPDATE SET
                completed_workouts = excluded.completed_workouts,
                current_track = excluded.current_track,
                last_activity_at = CURRENT_TIMESTAMP
        ''', (user_account_id, norm_uni, norm_char, norm_mode, journey_workouts_count, next_track_key))

        journey_row = cursor.execute('''
            SELECT id, user_id, universe, character_id, mode, completed_workouts, current_track, last_activity_at, created_at
            FROM training_journeys
            WHERE user_id = ? AND universe = ? AND character_id = ? AND mode = ?
        ''', (user_account_id, norm_uni, norm_char, norm_mode)).fetchone()

        if isinstance(journey_row, sqlite3.Row):
            journey_dict = dict(journey_row)
        elif journey_row:
            cols = ['id', 'user_id', 'universe', 'character_id', 'mode', 'completed_workouts', 'current_track', 'last_activity_at', 'created_at']
            journey_dict = dict(zip(cols, journey_row))
        else:
            journey_dict = {}

        profile_data = {
            'selectedUniverse': norm_uni,
            'selectedCharacter': norm_char,
            'strategyGoal': norm_mode,
            'age': age,
            'height': height,
            'weight': weight,
            'medicalHistory': user['medical_history'] if user else 'None',
            'specialPreferences': user['special_preferences'] if user else 'None',
            'user_id': user_account_id,
            'completed_workouts_count': journey_workouts_count,
        }
        next_workout_data = generate_custom_routine(profile_data, completed_workouts_count=journey_workouts_count)
        new_track = next_workout_data.get('daily_track', 'track_a')

        current_streak = calculate_streak(user_account_id)

        response_payload = {
            "success": True,
            "status": "success",
            "new_track": new_track,
            "track": new_track,
            "exp": exp_earned,
            "exp_earned": exp_earned,
            "exp_gained": exp_earned,
            "new_exp": exp_earned,
            "total_exp": total_exp,
            "current_grade": current_grade,
            "xp_to_next_level": xp_to_next_level,
            "current_streak": current_streak,
            "completed_sessions": completed_workouts_count,
            "completed_workouts_count": completed_workouts_count,
            "journey_completed_count": journey_workouts_count,
            "journey": format_journey_dict(journey_dict, is_active=True),
            "workout_data": next_workout_data,
            "message": f"Workout completed! Claimed +{exp_earned} EXP."
        }

        if idempotency_key:
            import json
            cursor.execute('''
                INSERT OR REPLACE INTO idempotency_keys (
                    idempotency_key, user_id, endpoint, response_body, status_code
                ) VALUES (?, ?, ?, ?, ?)
            ''', (str(idempotency_key), user_account_id, '/api/complete-workout', json.dumps(response_payload), 200))

        conn.execute('COMMIT')
        conn.close()

        return jsonify(response_payload), 200

    except Exception as e:
        if conn:
            try:
                conn.execute('ROLLBACK')
                conn.close()
            except Exception:
                pass
        return jsonify({"success": False, "status": "error", "message": str(e)}), 400


@app.route('/api/workout-history', methods=['GET'])
def get_workout_history():
    try:
        ensure_database_tables()

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        auth_user = resolve_request_user(cursor)
        if not auth_user:
            conn.close()
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        # Check for user spoofing via query parameters
        param_uid = request.args.get('user_id')
        if param_uid and str(param_uid) != str(auth_user['id']):
            conn.close()
            return jsonify({"status": "error", "message": "Forbidden: Cannot access another user's workout history"}), 403

        param_uname = request.args.get('username')
        if param_uname and str(param_uname) != str(auth_user['username']):
            conn.close()
            return jsonify({"status": "error", "message": "Forbidden: Cannot access another user's workout history"}), 403

        rows = cursor.execute('''
            SELECT id, user_id, character_id, paradigm, sets_completed, exp_earned, timestamp
            FROM workout_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
        ''', (auth_user['id'],)).fetchall()

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


@app.route('/api/journeys', methods=['GET'])
def get_user_journeys():
    try:
        ensure_database_tables()
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        user = resolve_request_user(cursor)
        if not user:
            conn.close()
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        # Check for user spoofing via query parameters
        param_uid = request.args.get('user_id')
        if param_uid and str(param_uid) != str(user['id']):
            conn.close()
            return jsonify({"status": "error", "message": "Forbidden: Cannot access another user's journeys"}), 403

        param_uname = request.args.get('username')
        if param_uname and str(param_uname) != str(user['username']):
            conn.close()
            return jsonify({"status": "error", "message": "Forbidden: Cannot access another user's journeys"}), 403

        # Get latest active profile to know current character & mode
        active_profile = cursor.execute(
            'SELECT * FROM user_profiles WHERE username = ? ORDER BY id DESC LIMIT 1',
            (user['username'],)
        ).fetchone()

        active_char = normalize_character_id(active_profile['selected_character']) if active_profile else None
        active_mode = normalize_mode_id(active_profile['training_strategy']) if active_profile else None

        rows = cursor.execute('''
            SELECT * FROM training_journeys
            WHERE user_id = ?
            ORDER BY datetime(last_activity_at) DESC, id DESC
        ''', (user['id'],)).fetchall()

        journeys = []
        for r in rows:
            # Synchronize completed_workouts with authoritative workout_history
            wh_count = cursor.execute('''
                SELECT COUNT(*) FROM workout_history
                WHERE user_id = ? AND character_id = ? AND paradigm = ?
            ''', (user['id'], r['character_id'], r['mode'])).fetchone()[0]

            if wh_count != r['completed_workouts']:
                t_idx = wh_count % 4
                t_track = f"track_{chr(97 + t_idx)}"
                cursor.execute('''
                    UPDATE training_journeys
                    SET completed_workouts = ?, current_track = ?
                    WHERE id = ?
                ''', (wh_count, t_track, r['id']))
                conn.commit()
                r = cursor.execute('SELECT * FROM training_journeys WHERE id = ?', (r['id'],)).fetchone()

            is_active = (r['character_id'] == active_char and r['mode'] == active_mode)
            journeys.append(format_journey_dict(r, is_active=is_active))

        conn.close()
        return jsonify({
            "status": "success",
            "journeys": journeys,
            "count": len(journeys)
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/journeys/start', methods=['POST'])
def start_or_get_journey():
    try:
        ensure_database_tables()
        data = request.get_json(silent=True) or {}

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        user = resolve_request_user(cursor)
        if not user:
            conn.close()
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        # Prevent user identity spoofing
        client_uid = data.get('user_id') or data.get('userId')
        if client_uid and str(client_uid).isdigit() and int(client_uid) != user['id']:
            conn.close()
            return jsonify({"status": "error", "message": "Forbidden: Cannot start journeys for another user"}), 403

        raw_char = data.get('character') or data.get('character_id') or data.get('selectedCharacter') or 'toji'
        char_key = normalize_character_id(raw_char)
        raw_uni = data.get('universe') or data.get('selectedUniverse')
        uni_key = normalize_universe_id(raw_uni, char_key)
        raw_mode = data.get('mode') or data.get('strategy') or data.get('strategyGoal') or 'train-like'
        mode_key = normalize_mode_id(raw_mode)

        journey_row, completed_count = get_or_create_journey(cursor, user['id'], uni_key, char_key, mode_key)

        # Update or insert active profile for this user
        cursor.execute('''
            INSERT INTO user_profiles (
                username, selected_universe, selected_character, training_strategy,
                age, height_cm, weight_kg, medical_history, special_preferences,
                total_exp, current_grade, weekly_workout_count, last_workout_logged_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL)
        ''', (
            user['username'], uni_key, char_key, mode_key,
            user['age'], user['height'], user['weight'],
            data.get('medicalHistory', 'None'), data.get('specialPreferences', 'None'),
            user['total_exp'], user['current_grade']
        ))

        profile_data = {
            'selectedUniverse': uni_key,
            'selectedCharacter': char_key,
            'strategyGoal': mode_key,
            'age': user['age'],
            'height': user['height'],
            'weight': user['weight'],
            'medicalHistory': data.get('medicalHistory', 'None'),
            'specialPreferences': data.get('specialPreferences', 'None'),
            'user_id': user['id'],
            'completed_workouts_count': completed_count,
        }
        routine_payload = generate_custom_routine(profile_data, completed_workouts_count=completed_count)

        conn.commit()
        conn.close()

        formatted = format_journey_dict(journey_row, is_active=True)
        return jsonify({
            "status": "success",
            "journey": formatted,
            "workout_data": routine_payload
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/journeys/resume', methods=['POST'])
def resume_journey():
    try:
        ensure_database_tables()
        data = request.get_json(silent=True) or {}

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        user = resolve_request_user(cursor)
        if not user:
            conn.close()
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        # Prevent user identity spoofing
        client_uid = data.get('user_id') or data.get('userId')
        if client_uid and str(client_uid).isdigit() and int(client_uid) != user['id']:
            conn.close()
            return jsonify({"status": "error", "message": "Forbidden: Cannot access another user's journey"}), 403

        journey_id = data.get('journey_id') or data.get('id')
        journey_row = None

        if journey_id:
            try:
                existing_j = cursor.execute('SELECT user_id FROM training_journeys WHERE id = ?', (int(journey_id),)).fetchone()
                if existing_j and existing_j['user_id'] != user['id']:
                    conn.close()
                    return jsonify({"status": "error", "message": "Forbidden: Cannot access another user's journey"}), 403

                journey_row = cursor.execute('''
                    SELECT * FROM training_journeys WHERE id = ? AND user_id = ?
                ''', (int(journey_id), user['id'])).fetchone()
            except (ValueError, TypeError):
                journey_row = None

        if not journey_row:
            raw_char = data.get('character') or data.get('character_id') or data.get('selectedCharacter')
            raw_mode = data.get('mode') or data.get('strategy') or data.get('strategyGoal')
            if raw_char:
                char_key = normalize_character_id(raw_char)
                mode_key = normalize_mode_id(raw_mode)
                raw_uni = data.get('universe') or data.get('selectedUniverse')
                uni_key = normalize_universe_id(raw_uni, char_key)
                journey_row, _ = get_or_create_journey(cursor, user['id'], uni_key, char_key, mode_key)

        if not journey_row:
            conn.close()
            return jsonify({"status": "error", "message": "Journey not found"}), 404

        char_key = journey_row['character_id']
        uni_key = journey_row['universe']
        mode_key = journey_row['mode']

        completed_count = cursor.execute('''
            SELECT COUNT(*) FROM workout_history
            WHERE user_id = ? AND character_id = ? AND paradigm = ?
        ''', (user['id'], char_key, mode_key)).fetchone()[0]

        track_idx = completed_count % 4
        current_track = f"track_{chr(97 + track_idx)}"

        cursor.execute('''
            UPDATE training_journeys
            SET completed_workouts = ?, current_track = ?, last_activity_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (completed_count, current_track, journey_row['id']))

        cursor.execute('''
            INSERT INTO user_profiles (
                username, selected_universe, selected_character, training_strategy,
                age, height_cm, weight_kg, medical_history, special_preferences,
                total_exp, current_grade
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'None', 'None', ?, ?)
        ''', (
            user['username'], uni_key, char_key, mode_key,
            user['age'], user['height'], user['weight'],
            user['total_exp'], user['current_grade']
        ))

        profile_data = {
            'selectedUniverse': uni_key,
            'selectedCharacter': char_key,
            'strategyGoal': mode_key,
            'age': user['age'],
            'height': user['height'],
            'weight': user['weight'],
            'medicalHistory': 'None',
            'specialPreferences': 'None',
            'user_id': user['id'],
            'completed_workouts_count': completed_count,
        }
        routine_payload = generate_custom_routine(profile_data, completed_workouts_count=completed_count)

        conn.commit()
        journey_row = cursor.execute('SELECT * FROM training_journeys WHERE id = ?', (journey_row['id'],)).fetchone()
        conn.close()

        formatted = format_journey_dict(journey_row, is_active=True)
        return jsonify({
            "status": "success",
            "journey": formatted,
            "workout_data": routine_payload
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/dev/reset-today', methods=['POST'])
def dev_reset_today():
    """
    DEVELOPER UTILITY: Bypasses the training cap and ACWR restrictions by 
    purging today's training log entries from the local SQLite database.
    Scoped strictly to the authenticated user.
    """
    ensure_database_tables()
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    auth_user = resolve_request_user(cursor)
    if not auth_user:
        conn.close()
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    today_str = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # 1. Clear entries from the detailed workout metrics log table for this user
        cursor.execute(
            "DELETE FROM workout_logs WHERE user_id = ? AND DATE(log_date) = DATE(?)", 
            (auth_user['id'], today_str)
        )
        
        # 2. Clear entries from the high-level summary workout history table for this user
        cursor.execute(
            "DELETE FROM workout_history WHERE user_id = ? AND DATE(timestamp) = DATE(?)", 
            (auth_user['id'], today_str)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "success", 
            "message": f"Time Chamber activated. Purged today's log entries for {auth_user['username']}."
        }), 200
        
    except Exception as e:
        conn.close()
        return jsonify({
            "status": "error", 
            "message": f"Dev reset failed: {str(e)}"
        }), 500 


if __name__ == '__main__':
    app.run(debug=True, port=5000) 

