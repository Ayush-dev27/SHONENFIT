import os
import sqlite3
from contextlib import contextmanager

# Module-level connection pool / singleton
_pg_pool = None
_backend = None

def get_database_backend():
    """
    Determines and enforces the active database backend.
    
    Rules:
    1. Production (FLASK_ENV=production or VERCEL=1):
       - DATABASE_URL is strictly mandatory.
       - If missing: raises RuntimeError immediately.
       - SQLite fallback is strictly prohibited.
    2. Development / Testing:
       - If DATABASE_URL is set: uses PostgreSQL.
       - If DATABASE_URL is NOT set:
         - Allowed ONLY if ALLOW_SQLITE_FALLBACK=true (or USE_SQLITE=true).
         - Otherwise raises RuntimeError directing developer to configure PostgreSQL
           or explicitly opt into offline SQLite fallback.
    """
    global _backend
    if _backend is not None:
        return _backend

    database_url = os.environ.get('DATABASE_URL', '').strip()
    env = os.environ.get('FLASK_ENV', 'development').lower()
    is_production = (env == 'production') or (os.environ.get('VERCEL') == '1')
    allow_sqlite = os.environ.get('ALLOW_SQLITE_FALLBACK', '').lower() in ('true', '1') or \
                   os.environ.get('USE_SQLITE', '').lower() in ('true', '1')

    if is_production:
        if not database_url:
            raise RuntimeError(
                "FATAL: DATABASE_URL is required in production environments. "
                "SQLite fallback is strictly prohibited."
            )
        _backend = 'postgres'
        return _backend

    # In local development: if explicitly configured to use SQLite (e.g. offline testing)
    use_sqlite_explicit = os.environ.get('USE_SQLITE', '').lower() in ('true', '1')
    if use_sqlite_explicit:
        _backend = 'sqlite'
        return _backend

    if database_url:
        _backend = 'postgres'
        return _backend

    if allow_sqlite:
        _backend = 'sqlite'
        return _backend

    raise RuntimeError(
        "DATABASE_URL is not configured. To connect to PostgreSQL, set DATABASE_URL. "
        "For offline local development, explicitly set ALLOW_SQLITE_FALLBACK=true."
    )

def reset_backend_cache():
    """Utility for tests to reset cached backend resolution."""
    global _backend, _pg_pool
    _backend = None
    if _pg_pool is not None:
        try:
            _pg_pool.close()
        except Exception:
            pass
        _pg_pool = None

def is_postgres():
    return get_database_backend() == 'postgres'

def is_sqlite():
    return get_database_backend() == 'sqlite'

def extract_scalar(row, default=0):
    if not row:
        return default
    if isinstance(row, dict) or hasattr(row, 'keys'):
        return list(row.values())[0]
    return row[0]

def _get_pg_driver():
    """Attempts to import psycopg (v3) or psycopg2."""
    try:
        import psycopg
        from psycopg.rows import dict_row
        return 'psycopg3', psycopg, dict_row
    except ImportError:
        pass

    try:
        import psycopg2
        import psycopg2.extras
        return 'psycopg2', psycopg2, psycopg2.extras.RealDictCursor
    except ImportError:
        raise ImportError(
            "A PostgreSQL driver is required to connect to DATABASE_URL. "
            "Please install 'psycopg[binary,pool]' or 'psycopg2-binary'."
        )

def get_pg_connection(timeout=30.0):
    database_url = os.environ.get('DATABASE_URL')
    driver_type, driver, row_factory = _get_pg_driver()
    
    if driver_type == 'psycopg3':
        conn = driver.connect(database_url, row_factory=row_factory, autocommit=False)
        return conn
    else: # psycopg2
        conn = driver.connect(database_url, cursor_factory=row_factory)
        conn.autocommit = False
        return conn

def get_sqlite_connection(timeout=30.0):
    db_file = os.environ.get('SQLITE_DATABASE_FILE', 'shonenfit.db')
    conn = sqlite3.connect(db_file, timeout=timeout)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def get_db_connection(timeout=30.0):
    backend = get_database_backend()
    if backend == 'postgres':
        return get_pg_connection(timeout=timeout)
    else:
        return get_sqlite_connection(timeout=timeout)

@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager that yields a database cursor producing dictionary-like rows.
    Automatically commits if commit=True and no exception occurred.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor, conn
        if commit:
            conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

@contextmanager
def db_transaction():
    """
    Context manager for atomic database transactions.
    Begins transaction, yields (cursor, conn), commits on success, rolls back on error.
    """
    conn = get_db_connection()
    backend = get_database_backend()
    
    if backend == 'postgres':
        # In postgres driver, connection is in a transaction by default (autocommit=False)
        cursor = conn.cursor()
    else:
        # SQLite immediate transaction
        conn.isolation_level = None
        conn.execute('BEGIN IMMEDIATE')
        cursor = conn.cursor()

    try:
        yield cursor, conn
        if backend == 'postgres':
            conn.commit()
        else:
            conn.execute('COMMIT')
    except Exception:
        try:
            if backend == 'postgres':
                conn.rollback()
            else:
                conn.execute('ROLLBACK')
        except Exception:
            pass
        raise
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

_pg_schema_initialized = False

POSTGRES_SCHEMA_SQL = """
-- 1. Required Extensions (safely attempted if available; native in PG 13+)
DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

-- 2. Permanent Migration Lineage Mapping Table
CREATE TABLE IF NOT EXISTS public._migration_user_map (
    sqlite_user_id INTEGER PRIMARY KEY,
    supabase_user_id UUID UNIQUE NOT NULL,
    username TEXT NOT NULL,
    migrated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    migration_batch TEXT NOT NULL DEFAULT 'phase3_initial'
);

COMMENT ON TABLE public._migration_user_map IS 
'Permanent audit lineage mapping SQLite integer user IDs to Supabase Auth UUIDs. Read-only metadata.';

-- 3. Profiles Table (Consolidates users + user_profiles)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE NOT NULL,
    age INTEGER NOT NULL DEFAULT 25 CHECK (age >= 10 AND age <= 120),
    height_cm NUMERIC(5, 2) NOT NULL DEFAULT 175.00 CHECK (height_cm >= 50.0 AND height_cm <= 300.0),
    weight_kg NUMERIC(5, 2) NOT NULL DEFAULT 70.00 CHECK (weight_kg >= 20.0 AND weight_kg <= 500.0),
    current_grade TEXT NOT NULL DEFAULT 'Grade 4',
    total_exp INTEGER NOT NULL DEFAULT 0 CHECK (total_exp >= 0),
    selected_universe TEXT NOT NULL DEFAULT 'jjk',
    selected_character TEXT NOT NULL DEFAULT 'toji',
    training_strategy TEXT NOT NULL DEFAULT 'physique',
    medical_history TEXT,
    special_preferences TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_profiles_username ON public.profiles (username);

-- 4. Workout History Table (Authoritative Session Ledger)
CREATE TABLE IF NOT EXISTS public.workout_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    character_id TEXT NOT NULL,
    paradigm TEXT NOT NULL,
    sets_completed INTEGER NOT NULL CHECK (sets_completed > 0),
    exp_earned INTEGER NOT NULL DEFAULT 250 CHECK (exp_earned >= 0),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workout_history_user_ts ON public.workout_history (user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_workout_history_user_char_mode ON public.workout_history (user_id, character_id, paradigm);

-- 5. Training Journeys Table (Authoritative Persistent Progression)
CREATE TABLE IF NOT EXISTS public.training_journeys (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    universe TEXT NOT NULL,
    character_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    completed_workouts INTEGER NOT NULL DEFAULT 0 CHECK (completed_workouts >= 0),
    current_track TEXT NOT NULL DEFAULT 'track_a' CHECK (current_track IN ('track_a', 'track_b', 'track_c', 'track_d')),
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_training_journeys UNIQUE (user_id, universe, character_id, mode)
);

CREATE INDEX IF NOT EXISTS idx_training_journeys_user_active ON public.training_journeys (user_id, last_activity_at DESC);

-- 6. Idempotency Keys Table (Request Deduplication & Protection)
CREATE TABLE IF NOT EXISTS public.idempotency_keys (
    id BIGSERIAL PRIMARY KEY,
    idempotency_key TEXT UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL,
    response_body JSONB NOT NULL,
    status_code INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_idempotency_keys_lookup ON public.idempotency_keys (idempotency_key, user_id);
CREATE INDEX IF NOT EXISTS idx_idempotency_keys_created_at ON public.idempotency_keys (created_at);

-- 7. Workout Logs Table (Granular Sets / ACWR Fatigue Baseline - Optional)
CREATE TABLE IF NOT EXISTS public.workout_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    log_date DATE NOT NULL,
    universe TEXT NOT NULL,
    character_name TEXT NOT NULL,
    exercise_name TEXT NOT NULL,
    set_index INTEGER NOT NULL,
    reps_completed INTEGER NOT NULL,
    weight_kg NUMERIC(5, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workout_logs_user_date ON public.workout_logs (user_id, log_date DESC);

-- 8. Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workout_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.training_journeys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.idempotency_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workout_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public._migration_user_map ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own profile' AND tablename = 'profiles') THEN
        CREATE POLICY "Users can view own profile" 
            ON public.profiles FOR SELECT 
            TO authenticated 
            USING (auth.uid() = id);
    END IF;
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own workout history' AND tablename = 'workout_history') THEN
        CREATE POLICY "Users can view own workout history" 
            ON public.workout_history FOR SELECT 
            TO authenticated 
            USING (auth.uid() = user_id);
    END IF;
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own training journeys' AND tablename = 'training_journeys') THEN
        CREATE POLICY "Users can view own training journeys" 
            ON public.training_journeys FOR SELECT 
            TO authenticated 
            USING (auth.uid() = user_id);
    END IF;
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own idempotency keys' AND tablename = 'idempotency_keys') THEN
        CREATE POLICY "Users can view own idempotency keys" 
            ON public.idempotency_keys FOR SELECT 
            TO authenticated 
            USING (auth.uid() = user_id);
    END IF;
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own workout logs' AND tablename = 'workout_logs') THEN
        CREATE POLICY "Users can view own workout logs" 
            ON public.workout_logs FOR SELECT 
            TO authenticated 
            USING (auth.uid() = user_id);
    END IF;
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own migration lineage' AND tablename = '_migration_user_map') THEN
        CREATE POLICY "Users can view own migration lineage" 
            ON public._migration_user_map FOR SELECT 
            TO authenticated 
            USING (auth.uid() = supabase_user_id);
    END IF;
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

-- 9. Safe Dev User Fallback Seed (00000000-0000-0000-0000-000000000001)
DO $$
BEGIN
    INSERT INTO auth.users (
        id, aud, role, email, raw_user_meta_data, raw_app_meta_data, created_at, updated_at
    ) VALUES (
        '00000000-0000-0000-0000-000000000001'::uuid,
        'authenticated',
        'authenticated',
        'legacy_recruit@shonenfit.local',
        '{"username": "legacy_recruit"}'::jsonb,
        '{"provider": "email", "providers": ["email"]}'::jsonb,
        NOW(),
        NOW()
    )
    ON CONFLICT (id) DO NOTHING;
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

DO $$
BEGIN
    INSERT INTO public.profiles (
        id, username, age, height_cm, weight_kg,
        current_grade, total_exp, selected_universe,
        selected_character, training_strategy
    ) VALUES (
        '00000000-0000-0000-0000-000000000001'::uuid,
        'legacy_recruit',
        25,
        175.00,
        70.00,
        'Grade 4',
        0,
        'jjk',
        'toji',
        'physique'
    )
    ON CONFLICT (id) DO NOTHING;
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;
"""

def init_postgres_schema(force=False):
    """
    Idempotently initializes all PostgreSQL tables, indexes, constraints,
    RLS policies, and default seeds required by SHONENFIT in PostgreSQL.
    """
    global _pg_schema_initialized
    if _pg_schema_initialized and not force:
        return

    if not is_postgres():
        return

    try:
        conn = get_pg_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(POSTGRES_SCHEMA_SQL)
            conn.commit()
            cursor.close()
            _pg_schema_initialized = True
        finally:
            conn.close()
    except Exception as e:
        import logging
        logging.warning(f"[PostgreSQL Schema Init] Failed to initialize schema: {e}")
        env = os.environ.get('FLASK_ENV', 'development').lower()
        is_production = (env == 'production') or (os.environ.get('VERCEL') == '1')
        if is_production:
            raise

