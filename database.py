import sqlite3

def init_db():
    # This automatically connects to a local file named 'shonenfit.db'.
    # If the file doesn't exist, Python will create it right in your folder.
    conn = sqlite3.connect('shonenfit.db')
    conn.execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()
    
    # Writing and executing your SQL schema
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
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            
            -- Anime Target Alignment
            selected_universe TEXT NOT NULL,    -- 'jjk', 'demon-slayer', 'mha'
            selected_character TEXT NOT NULL,   -- 'toji', 'tanjiro', 'deku', etc.
            training_strategy TEXT NOT NULL,    -- 'physique' or 'train-like'
            
            -- Biological Baselines
            age INTEGER NOT NULL,
            height_cm REAL NOT NULL,
            weight_kg REAL NOT NULL,
            medical_history TEXT,
            special_preferences TEXT,
            
            -- Gamified Progression Engine
            current_grade TEXT DEFAULT 'Grade 4',
            total_exp INTEGER DEFAULT 0,
            weekly_workout_count INTEGER DEFAULT 0,
            last_workout_logged_at TEXT,
            current_streak_weeks INTEGER DEFAULT 0,
            
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')

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
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,          -- Format: 'YYYY-MM-DD' for accurate date math
            universe TEXT NOT NULL,          -- 'jjk', 'demon-slayer', 'mha'
            character_name TEXT NOT NULL,    -- 'toji', 'tanjiro', etc.
            exercise_name TEXT NOT NULL,     -- e.g., 'Barbell Romanian Deadlifts'
            set_index INTEGER NOT NULL,      -- e.g., 1, 2, or 3
            reps_completed INTEGER NOT NULL, -- Actual raw reps executed
            weight_kg REAL NOT NULL,         -- The weight load applied
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    ''') 
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("🔥 SHONENFIT Database successfully initialized with user_profiles table!")

if __name__ == '__main__':
    init_db() 

def log_workout_session(user_id, universe, character_name, sets_data):
    """
    Saves granular set-by-set information for a completed workout session.
    
    sets_data format expected:
    [
        {'exercise_name': 'Barbell Romanian Deadlifts', 'set_index': 1, 'reps': 8, 'weight': 60.0},
        {'exercise_name': 'Barbell Romanian Deadlifts', 'set_index': 2, 'reps': 8, 'weight': 60.0},
        ...
    ]
    """
    from datetime import date
    
    # Secure the date tracking format strictly as YYYY-MM-DD
    today_str = date.today().isoformat()
    
    conn = sqlite3.connect('shonenfit.db')
    cursor = conn.cursor()
    
    try:
        # Prepare our strict insert query template
        query = '''
            INSERT INTO workout_logs 
            (user_id, log_date, universe, character_name, exercise_name, set_index, reps_completed, weight_kg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        # Build the batch execution list safely
        batch_records = [
            (
                user_id, 
                today_str, 
                universe, 
                character_name, 
                s['exercise_name'], 
                s['set_index'], 
                s['reps'], 
                s['weight']
            ) for s in sets_data
        ]
        
        # Execute atomic batch insertion
        cursor.executemany(query, batch_records)
        conn.commit()
        print(f"✅ Successfully logged {len(sets_data)} discrete training sets for user {user_id}.")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Database error encountered during workout logging transaction: {e}")
        return False
        
    finally:
        conn.close() 