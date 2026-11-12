-- ==============================================================================
-- SHONENFIT — TARGET POSTGRESQL SCHEMA (PHASE 3)
-- ==============================================================================

-- 0. Supabase Auth Compatibility Schema (For Local Testing & Target Parity)
CREATE SCHEMA IF NOT EXISTS auth;
CREATE TABLE IF NOT EXISTS auth.users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE,
    raw_user_meta_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Safe fallback for auth.uid() if not natively provided by Supabase
CREATE OR REPLACE FUNCTION auth.uid() 
RETURNS UUID 
LANGUAGE sql STABLE 
AS $$
    SELECT NULLIF(current_setting('request.jwt.claim.sub', true), '')::uuid;
$$;

-- Safe creation of Supabase roles for local/standalone PostgreSQL testing
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
        CREATE ROLE authenticated NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
        CREATE ROLE anon NOLOGIN;
    END IF;
END $$;

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
-- Lineage audit metadata mapping legacy SQLite integer IDs to Supabase Auth UUIDs
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

-- ==============================================================================
-- 8. Row Level Security (RLS) Policies
-- ==============================================================================
-- Architecture: Browser -> Supabase Auth -> Flask Backend -> PostgreSQL.
-- The Flask backend connects using server-side database credentials (bypassing RLS).
-- Direct PostgREST access from browser clients (via Supabase anon/authenticated key)
-- is strictly restricted:
--   - SELECT is restricted to the authenticated user's own rows (auth.uid() = user_id/id).
--   - Direct client INSERT, UPDATE, and DELETE are strictly disallowed.
--   - All state mutations (workout logging, EXP awards, cooldown checks, track rotations)
--     must pass through Flask business logic.

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workout_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.training_journeys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.idempotency_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workout_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public._migration_user_map ENABLE ROW LEVEL SECURITY;

-- 8.1 profiles: Authenticated users can view their own profile only
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own profile' AND tablename = 'profiles') THEN
        CREATE POLICY "Users can view own profile" 
            ON public.profiles FOR SELECT 
            TO authenticated 
            USING (auth.uid() = id);
    END IF;
END $$;

-- 8.2 workout_history: Authenticated users can view their own history only
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own workout history' AND tablename = 'workout_history') THEN
        CREATE POLICY "Users can view own workout history" 
            ON public.workout_history FOR SELECT 
            TO authenticated 
            USING (auth.uid() = user_id);
    END IF;
END $$;

-- 8.3 training_journeys: Authenticated users can view their own journeys only
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own training journeys' AND tablename = 'training_journeys') THEN
        CREATE POLICY "Users can view own training journeys" 
            ON public.training_journeys FOR SELECT 
            TO authenticated 
            USING (auth.uid() = user_id);
    END IF;
END $$;

-- 8.4 idempotency_keys: Authenticated users can view their own idempotency keys only
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own idempotency keys' AND tablename = 'idempotency_keys') THEN
        CREATE POLICY "Users can view own idempotency keys" 
            ON public.idempotency_keys FOR SELECT 
            TO authenticated 
            USING (auth.uid() = user_id);
    END IF;
END $$;

-- 8.5 workout_logs: Authenticated users can view their own workout logs only
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own workout logs' AND tablename = 'workout_logs') THEN
        CREATE POLICY "Users can view own workout logs" 
            ON public.workout_logs FOR SELECT 
            TO authenticated 
            USING (auth.uid() = user_id);
    END IF;
END $$;

-- 8.6 _migration_user_map: Authenticated users can view their own lineage mapping only
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own migration lineage' AND tablename = '_migration_user_map') THEN
        CREATE POLICY "Users can view own migration lineage" 
            ON public._migration_user_map FOR SELECT 
            TO authenticated 
            USING (auth.uid() = supabase_user_id);
    END IF;
END $$;
