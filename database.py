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
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("🔥 SHONENFIT Database successfully initialized with user_profiles table!")

if __name__ == '__main__':
    init_db() 
