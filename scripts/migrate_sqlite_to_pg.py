#!/usr/bin/env python3
"""
SHONENFIT — SQLite to PostgreSQL Migration Runner (Phase 3)
Approved Migration Manifest:
- MIGRATE: User IDs 1, 2, 157, 186, 296
- EXCLUDE: User IDs 5, 6, 7, 139, 155, 182, 183, 293, 295, and test fixtures 300-650

STRICT SAFETY RULES:
- Connects read-only to shonenfit.db.
- Strictly requires DATABASE_URL targeting PostgreSQL.
- Refuses to run against SQLite.
"""

import os
import sys
import sqlite3
import uuid
import json
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Approved Manifest
APPROVED_MIGRATE_IDS = [1, 2, 157, 186, 296]
EXCLUDED_ACCOUNT_IDS = [5, 6, 7, 139, 155, 182, 183, 293, 295]
SHONENFIT_UUID_NAMESPACE = uuid.UUID('c8876f5c-5bda-4c81-ba8f-adba513137a5')

def get_deterministic_uuid(username: str) -> uuid.UUID:
    """Generates an idempotent, deterministic UUIDv5 for migration mapping."""
    return uuid.uuid5(SHONENFIT_UUID_NAMESPACE, f"{username}.shonenfit.internal")

def run_migration():
    database_url = os.environ.get('DATABASE_URL', '').strip()
    if not database_url:
        print("❌ FATAL: DATABASE_URL environment variable is required to run the PostgreSQL migration.")
        print("Usage: DATABASE_URL='postgresql://user:pass@host:port/dbname' python scripts/migrate_sqlite_to_pg.py")
        sys.exit(1)

    if database_url.startswith('sqlite') or 'shonenfit.db' in database_url:
        print("❌ FATAL: DATABASE_URL points to SQLite. Migration runner strictly targets PostgreSQL.")
        sys.exit(1)

    # Import PostgreSQL driver
    try:
        import psycopg
        from psycopg.rows import dict_row
        driver_type = 'psycopg3'
    except ImportError:
        try:
            import psycopg2
            import psycopg2.extras
            driver_type = 'psycopg2'
        except ImportError:
            print("❌ FATAL: No PostgreSQL driver found. Please install psycopg or psycopg2.")
            sys.exit(1)

    sqlite_file = os.environ.get('SQLITE_DATABASE_FILE', 'shonenfit.db')
    if not os.path.exists(sqlite_file):
        print(f"❌ FATAL: Source SQLite file '{sqlite_file}' not found.")
        sys.exit(1)

    print(f"🚀 Starting SHONENFIT Data Migration...")
    print(f"  Source: SQLite ('{sqlite_file}') [READ-ONLY]")
    print(f"  Target: PostgreSQL ({database_url.split('@')[-1] if '@' in database_url else 'configured url'})")
    print(f"  Approved Manifest: IDs {APPROVED_MIGRATE_IDS}")

    # 1. Connect to SQLite read-only
    # Using uri=True with mode=ro guarantees zero writes to shonenfit.db
    sqlite_conn = sqlite3.connect(f"file:{sqlite_file}?mode=ro", uri=True)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    # 2. Connect to PostgreSQL
    if driver_type == 'psycopg3':
        pg_conn = psycopg.connect(database_url, autocommit=False)
    else:
        pg_conn = psycopg2.connect(database_url)
        pg_conn.autocommit = False
    pg_cur = pg_conn.cursor()

    try:
        # Step A: Apply target schema DDL
        schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if os.path.exists(schema_file):
            print(f"📜 Applying target PostgreSQL schema from '{schema_file}'...")
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            pg_cur.execute(schema_sql)
            pg_conn.commit()
            print("✅ Schema applied successfully.")

        # Ensure target application tables are fresh and idempotent
        pg_cur.execute("""
            TRUNCATE TABLE 
                public.workout_logs,
                public.idempotency_keys,
                public.training_journeys,
                public.workout_history,
                public.profiles,
                public._migration_user_map
            CASCADE;
        """)
        pg_conn.commit()

        # Step B: Populate _migration_user_map and profiles
        print("👤 Migrating approved user accounts...")
        for uid in APPROVED_MIGRATE_IDS:
            u = sqlite_cur.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
            if not u:
                print(f"⚠️ Warning: User ID {uid} not found in SQLite. Skipping.")
                continue

            uname = u['username']
            u_uuid = get_deterministic_uuid(uname)

            # Record in _migration_user_map
            pg_cur.execute("""
                INSERT INTO public._migration_user_map (sqlite_user_id, supabase_user_id, username, migrated_at, migration_batch)
                VALUES (%s, %s, %s, NOW(), 'phase3_initial')
                ON CONFLICT (sqlite_user_id) DO UPDATE SET
                    supabase_user_id = EXCLUDED.supabase_user_id,
                    username = EXCLUDED.username;
            """, (uid, str(u_uuid), uname))

            # Fetch latest user_profiles row for this user
            latest_prof = sqlite_cur.execute("""
                SELECT * FROM user_profiles WHERE username = ? ORDER BY id DESC LIMIT 1
            """, (uname,)).fetchone()

            sel_uni = latest_prof['selected_universe'] if latest_prof else 'jjk'
            sel_char = latest_prof['selected_character'] if latest_prof else 'toji'
            strat = latest_prof['training_strategy'] if latest_prof else 'physique'
            med = latest_prof['medical_history'] if latest_prof else None
            pref = latest_prof['special_preferences'] if latest_prof else None

            # Special case for legacy_recruit (user 1): has journey for inosuke / demon-slayer
            if uid == 1:
                sel_uni = 'demon-slayer'
                sel_char = 'inosuke'
                strat = 'physique'

            # Ensure auth.users record exists
            pg_cur.execute("""
                INSERT INTO auth.users (id, email, raw_user_meta_data, created_at)
                VALUES (%s, %s, %s::jsonb, NOW())
                ON CONFLICT (id) DO NOTHING;
            """, (
                str(u_uuid),
                f"{uname.lower()}@users.shonenfit.internal",
                json.dumps({'username': uname})
            ))

            # Insert into public.profiles
            pg_cur.execute("""
                INSERT INTO public.profiles (
                    id, username, age, height_cm, weight_kg, current_grade, total_exp,
                    selected_universe, selected_character, training_strategy,
                    medical_history, special_preferences, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    username = EXCLUDED.username,
                    age = EXCLUDED.age,
                    height_cm = EXCLUDED.height_cm,
                    weight_kg = EXCLUDED.weight_kg,
                    current_grade = EXCLUDED.current_grade,
                    total_exp = EXCLUDED.total_exp,
                    selected_universe = EXCLUDED.selected_universe,
                    selected_character = EXCLUDED.selected_character,
                    training_strategy = EXCLUDED.training_strategy,
                    medical_history = EXCLUDED.medical_history,
                    special_preferences = EXCLUDED.special_preferences,
                    updated_at = NOW();
            """, (
                str(u_uuid),
                uname,
                u['age'],
                float(u['height']),
                float(u['weight']),
                u['current_grade'],
                int(u['total_exp']),
                sel_uni,
                sel_char,
                strat,
                med,
                pref,
                u['created_at']
            ))

        pg_conn.commit()
        print(f"✅ Migrated {len(APPROVED_MIGRATE_IDS)} user profiles.")

        # Step C: Migrate workout_history
        print("🏋️ Migrating workout_history...")
        wh_rows = sqlite_cur.execute(f"""
            SELECT * FROM workout_history 
            WHERE user_id IN ({','.join(str(i) for i in APPROVED_MIGRATE_IDS)})
            ORDER BY id ASC
        """).fetchall()

        migrated_wh_count = 0
        for wh in wh_rows:
            target_uuid = str(get_deterministic_uuid(sqlite_cur.execute("SELECT username FROM users WHERE id = ?", (wh['user_id'],)).fetchone()[0]))
            pg_cur.execute("""
                INSERT INTO public.workout_history (
                    user_id, character_id, paradigm, sets_completed, exp_earned, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s);
            """, (
                target_uuid,
                wh['character_id'],
                wh['paradigm'],
                wh['sets_completed'],
                wh['exp_earned'],
                wh['timestamp']
            ))
            migrated_wh_count += 1

        pg_conn.commit()
        print(f"✅ Migrated {migrated_wh_count} workout_history records.")

        # Step D: Migrate training_journeys
        print("🗺️ Migrating training_journeys...")
        tj_rows = sqlite_cur.execute(f"""
            SELECT * FROM training_journeys 
            WHERE user_id IN ({','.join(str(i) for i in APPROVED_MIGRATE_IDS)})
            ORDER BY id ASC
        """).fetchall()

        migrated_tj_count = 0
        for tj in tj_rows:
            target_uuid = str(get_deterministic_uuid(sqlite_cur.execute("SELECT username FROM users WHERE id = ?", (tj['user_id'],)).fetchone()[0]))
            pg_cur.execute("""
                INSERT INTO public.training_journeys (
                    user_id, universe, character_id, mode, completed_workouts, current_track, last_activity_at, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, universe, character_id, mode) DO UPDATE SET
                    completed_workouts = EXCLUDED.completed_workouts,
                    current_track = EXCLUDED.current_track,
                    last_activity_at = EXCLUDED.last_activity_at;
            """, (
                target_uuid,
                tj['universe'],
                tj['character_id'],
                tj['mode'],
                tj['completed_workouts'],
                tj['current_track'],
                tj['last_activity_at'],
                tj['created_at']
            ))
            migrated_tj_count += 1

        pg_conn.commit()
        print(f"✅ Migrated {migrated_tj_count} training_journeys records.")
        print("\n🎉 MIGRATION FINISHED SUCCESSFULLY!")

    except Exception as e:
        pg_conn.rollback()
        print(f"❌ MIGRATION FAILED WITH ERROR: {e}")
        raise
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == '__main__':
    run_migration()
