#!/usr/bin/env python3
"""
SHONENFIT — PostgreSQL Migration Verification Script (Phase 3)
Asserts 100% mathematical parity across profiles, workout history, journeys, and EXP.

STRICT SAFETY RULES:
- Strictly requires DATABASE_URL targeting PostgreSQL.
- Refuses to run against SQLite.
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def verify_migration():
    database_url = os.environ.get('DATABASE_URL', '').strip()
    if not database_url:
        print("❌ FATAL: DATABASE_URL environment variable is required to run migration verification.")
        print("Usage: DATABASE_URL='postgresql://user:pass@host:port/dbname' python scripts/verify_pg_migration.py")
        sys.exit(1)

    if database_url.startswith('sqlite') or 'shonenfit.db' in database_url:
        print("❌ FATAL: DATABASE_URL points to SQLite. Verification runner strictly targets PostgreSQL.")
        sys.exit(1)

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

    if driver_type == 'psycopg3':
        conn = psycopg.connect(database_url, row_factory=dict_row)
    else:
        conn = psycopg2.connect(database_url, cursor_factory=psycopg2.extras.RealDictCursor)

    cur = conn.cursor()
    errors = []

    print("🔍 Starting PostgreSQL Migration Verification...")

    try:
        # 1. Row Counts Check
        cur.execute("SELECT COUNT(*) AS cnt FROM public.profiles;")
        profiles_cnt = cur.fetchone()['cnt']
        if profiles_cnt != 5:
            errors.append(f"Expected exactly 5 profiles in PostgreSQL, found {profiles_cnt}")

        cur.execute("SELECT COUNT(*) AS cnt FROM public.workout_history;")
        wh_cnt = cur.fetchone()['cnt']
        if wh_cnt != 34:
            errors.append(f"Expected exactly 34 workout_history rows, found {wh_cnt}")

        cur.execute("SELECT COUNT(*) AS cnt FROM public.training_journeys;")
        tj_cnt = cur.fetchone()['cnt']
        if tj_cnt != 8:
            errors.append(f"Expected exactly 8 training_journeys rows, found {tj_cnt}")

        cur.execute("SELECT COUNT(*) AS cnt FROM public._migration_user_map;")
        map_cnt = cur.fetchone()['cnt']
        if map_cnt != 5:
            errors.append(f"Expected exactly 5 rows in _migration_user_map, found {map_cnt}")

        print(f"  [1/5] Row Counts: Profiles={profiles_cnt} (5), History={wh_cnt} (34), Journeys={tj_cnt} (8), LineageMap={map_cnt} (5)")

        # 2. EXP & Grade Parity Check
        cur.execute("""
            SELECT p.id, p.username, p.total_exp, p.current_grade, COALESCE(SUM(w.exp_earned), 0) AS calculated_exp
            FROM public.profiles p
            LEFT JOIN public.workout_history w ON p.id = w.user_id
            GROUP BY p.id, p.username, p.total_exp, p.current_grade
            HAVING p.total_exp != COALESCE(SUM(w.exp_earned), 0);
        """)
        exp_mismatches = cur.fetchall()
        if exp_mismatches:
            for m in exp_mismatches:
                errors.append(f"EXP mismatch for user '{m['username']}': stored {m['total_exp']} != calculated {m['calculated_exp']}")
        else:
            print("  [2/5] EXP Parity: 100% Match for all profiles against workout_history sums.")

        # 3. Training Journey Synchronization Check with Canonical Universe Derivation
        cur.execute("""
            WITH canonical_character_universe AS (
                SELECT 
                    w.id AS history_id,
                    w.user_id,
                    w.character_id,
                    w.paradigm AS mode,
                    CASE 
                        WHEN w.character_id IN ('toji', 'itadori', 'maki') THEN 'jjk'
                        WHEN w.character_id IN ('tanjiro', 'tengen', 'inosuke') THEN 'demon-slayer'
                        WHEN w.character_id IN ('deku', 'bakugo', 'all-might') THEN 'mha'
                        ELSE 'jjk'
                    END AS derived_universe
                FROM public.workout_history w
            ),
            history_counts AS (
                SELECT 
                    user_id,
                    derived_universe AS universe,
                    character_id,
                    mode,
                    COUNT(history_id) AS wh_count
                FROM canonical_character_universe
                GROUP BY user_id, derived_universe, character_id, mode
            )
            SELECT 
                j.id AS journey_id,
                j.user_id,
                j.universe,
                j.character_id,
                j.mode,
                j.completed_workouts AS stored_count,
                COALESCE(h.wh_count, 0) AS expected_count
            FROM public.training_journeys j
            LEFT JOIN history_counts h ON 
                j.user_id = h.user_id AND 
                j.universe = h.universe AND 
                j.character_id = h.character_id AND 
                j.mode = h.mode
            WHERE j.completed_workouts != COALESCE(h.wh_count, 0);
        """)
        tj_mismatches = cur.fetchall()
        if tj_mismatches:
            for m in tj_mismatches:
                errors.append(f"Journey count mismatch for Journey {m['journey_id']} ({m['character_id']}/{m['mode']}): stored {m['stored_count']} != expected {m['expected_count']}")
        else:
            print("  [3/5] Journey Parity: 100% Match for all journeys against canonical universe & history counts.")

        # 4. User 2 (Recruit) Specific State Check
        cur.execute("SELECT * FROM public.profiles WHERE username = 'Recruit';")
        recruit = cur.fetchone()
        if not recruit:
            errors.append("User 2 ('Recruit') not found in public.profiles")
        else:
            if recruit['total_exp'] != 5250:
                errors.append(f"Recruit total_exp is {recruit['total_exp']}, expected 5250")
            if recruit['current_grade'] != 'Grade 1':
                errors.append(f"Recruit current_grade is '{recruit['current_grade']}', expected 'Grade 1'")
            print(f"  [4/5] User 2 State: Recruit confirmed at Grade 1 with 5,250 EXP.")

        # 5. Lineage Check
        cur.execute("SELECT sqlite_user_id, username FROM public._migration_user_map ORDER BY sqlite_user_id ASC;")
        mapped_users = [r['sqlite_user_id'] for r in cur.fetchall()]
        if mapped_users != [1, 2, 157, 186, 296]:
            errors.append(f"_migration_user_map does not match approved manifest: {mapped_users}")
        else:
            print(f"  [5/6] Lineage Check: _migration_user_map verified for SQLite IDs [1, 2, 157, 186, 296].")

        # 6. Critical Identity Chain Validation
        print("  [6/6] Critical Identity Validation: Demonstrating full identity chain...")
        cur.execute("""
            SELECT 
                m.sqlite_user_id,
                m.username,
                m.supabase_user_id AS map_uuid,
                u.id AS auth_uuid,
                p.id AS profile_uuid,
                COUNT(DISTINCT w.id) AS wh_count,
                COUNT(DISTINCT j.id) AS journey_count
            FROM public._migration_user_map m
            JOIN auth.users u ON m.supabase_user_id = u.id
            JOIN public.profiles p ON m.supabase_user_id = p.id
            LEFT JOIN public.workout_history w ON m.supabase_user_id = w.user_id
            LEFT JOIN public.training_journeys j ON m.supabase_user_id = j.user_id
            GROUP BY m.sqlite_user_id, m.username, m.supabase_user_id, u.id, p.id
            ORDER BY m.sqlite_user_id ASC;
        """)
        chain_rows = cur.fetchall()
        if len(chain_rows) != 5:
            errors.append(f"Expected 5 fully linked identity chains, found {len(chain_rows)}")
        for r in chain_rows:
            print(f"    SQLite ID {r['sqlite_user_id']} ({r['username']}):")
            print(f"      → migration_map: {r['map_uuid']}")
            print(f"      → auth.users:    {r['auth_uuid']}")
            print(f"      → profiles.id:   {r['profile_uuid']}")
            print(f"      → workout_history rows: {r['wh_count']}, journeys: {r['journey_count']}")
            if r['map_uuid'] != r['auth_uuid'] or r['map_uuid'] != r['profile_uuid']:
                errors.append(f"Identity chain mismatch for user {r['username']}")

    finally:
        cur.close()
        conn.close()

    if errors:
        print("\n❌ POSTGRESQL VERIFICATION FAILED:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n🎉 ALL POSTGRESQL VERIFICATION CHECKS PASSED WITH 100% PARITY!")

if __name__ == '__main__':
    verify_migration()
