"""
Database Connection & Query Helper for Brownies Hub
---------------------------------------------------
This module handles connecting to the MySQL database (or SQLite fallback)
and provides simple helper functions for running SQL queries.

Beginner-Friendly:
- query_db(): Used for SELECT queries to fetch data as Python dictionaries.
- execute_db(): Used for INSERT, UPDATE, DELETE queries.
"""

import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'sweet_crumbs')

# Flag to remember which database driver is currently active
DB_MODE = None # 'mysql' or 'sqlite'

def get_sqlite_path():
    """Returns sqlite database path, handling serverless /tmp directory if needed."""
    if os.environ.get('VERCEL'):
        tmp_db = '/tmp/sweet_crumbs.db'
        root_db = os.path.join(os.path.dirname(__file__), 'sweet_crumbs.db')
        if not os.path.exists(tmp_db) and os.path.exists(root_db):
            import shutil
            try:
                shutil.copyfile(root_db, tmp_db)
            except Exception:
                pass
        return tmp_db if os.path.exists(tmp_db) else root_db
    return os.path.join(os.path.dirname(__file__), 'sweet_crumbs.db')

def get_db_connection():
    """
    Establishes and returns a database connection.
    Attempts MySQL first; if unavailable, falls back to SQLite for easy local testing.
    """
    global DB_MODE
    
    if DB_MODE == 'sqlite':
        db_path = get_sqlite_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # Try connecting to MySQL first
    try:
        import pymysql
        import pymysql.cursors
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            connect_timeout=2
        )
        DB_MODE = 'mysql'
        return conn
    except Exception:
        # Fallback to local SQLite database if MySQL is not available
        db_path = get_sqlite_path()
        conn = sqlite3.connect(db_path)
        # Enable column name access like dictionaries
        conn.row_factory = sqlite3.Row
        DB_MODE = 'sqlite'
        return conn

def query_db(query, args=(), one=False):
    """
    Helper function to run SELECT queries.
    Returns a list of dictionaries, or a single dictionary if one=True.
    """
    conn = get_db_connection()
    try:
        if DB_MODE == 'sqlite':
            # SQLite uses '?' placeholder instead of '%s'
            sqlite_query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(sqlite_query, args)
            rows = cursor.fetchall()
            # Convert sqlite3.Row objects to standard Python dicts
            results = [dict(row) for row in rows]
            cursor.close()
            return (results[0] if results else None) if one else results
        else:
            # MySQL execution
            cursor = conn.cursor()
            cursor.execute(query, args)
            results = cursor.fetchone() if one else cursor.fetchall()
            cursor.close()
            return results
    finally:
        conn.close()

def execute_db(query, args=(), return_id=False):
    """
    Helper function to run INSERT, UPDATE, and DELETE queries.
    Returns the newly inserted row ID (if return_id=True) or affected row count.
    """
    conn = get_db_connection()
    try:
        if DB_MODE == 'sqlite':
            sqlite_query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(sqlite_query, args)
            conn.commit()
            last_id = cursor.lastrowid
            row_count = cursor.rowcount
            cursor.close()
            return last_id if return_id else row_count
        else:
            cursor = conn.cursor()
            cursor.execute(query, args)
            last_id = cursor.lastrowid
            row_count = cursor.rowcount
            cursor.close()
            return last_id if return_id else row_count
    finally:
        conn.close()
