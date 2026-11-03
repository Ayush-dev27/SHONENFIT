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
