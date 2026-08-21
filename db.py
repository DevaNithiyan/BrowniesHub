"""
Database Connection & Query Helper for Brownies Hub
---------------------------------------------------
This module handles connecting to MySQL (or SQLite fallback for Vercel/Local)
and provides simple helper functions for running SQL queries.

Includes auto-initialization of tables & sample data for serverless environments.
"""

import os
import sqlite3
import tempfile
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
    """Returns sqlite database path, writing to OS temp directory in serverless/Vercel environments."""
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        tmp_dir = tempfile.gettempdir()
        tmp_db = os.path.join(tmp_dir, 'sweet_crumbs.db')
        root_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sweet_crumbs.db')
        if not os.path.exists(tmp_db) and os.path.exists(root_db):
            import shutil
            try:
                shutil.copyfile(root_db, tmp_db)
            except Exception:
                pass
        return tmp_db
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sweet_crumbs.db')

def ensure_sqlite_initialized(conn):
    """Auto-creates tables and sample seed data if database is fresh (vital for Vercel)."""
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM categories LIMIT 1")
        cur.close()
    except Exception:
        from werkzeug.security import generate_password_hash
        cur = conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            image TEXT
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NULL,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NULL,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            subtotal REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
        );
        """)

        # Insert seed data if categories empty
        cur.execute("SELECT COUNT(*) FROM categories")
        if cur.fetchone()[0] == 0:
            admin_pw = generate_password_hash('admin123')
            cust_pw = generate_password_hash('customer123')

            cur.executemany("INSERT INTO categories (id, name, slug, image) VALUES (?, ?, ?, ?)", [
                (1, 'Cakes', 'cakes', 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=600&q=80'),
                (2, 'Pastries', 'pastries', 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80'),
                (3, 'Breads', 'breads', 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80'),
                (4, 'Cookies', 'cookies', 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=600&q=80')
            ])

            cur.executemany("INSERT INTO users (id, name, email, password, role) VALUES (?, ?, ?, ?, ?)", [
                (1, 'Bakery Admin', 'admin@brownieshub.com', admin_pw, 'admin'),
                (2, 'Rahul Sharma', 'customer@gmail.com', cust_pw, 'customer')
            ])

            cur.executemany("INSERT INTO products (id, category_id, name, description, price, image) VALUES (?, ?, ?, ?, ?, ?)", [
                (1, 1, 'Chocolate Truffle Cake', 'Rich, decadent dark chocolate layers coated with smooth chocolate ganache and chocolate curls.', 550.00, 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=600&q=80'),
                (2, 1, 'Red Velvet Cake', 'Velvety crimson sponge layered with silky cream cheese frosting and a delicate crumb coating.', 650.00, 'https://images.unsplash.com/photo-1586788680434-30d324b2d46f?auto=format&fit=crop&w=600&q=80'),
                (3, 1, 'Black Forest Cake', 'Classic German sponge infused with cherries, layered with fresh whipped cream and dark chocolate flakes.', 600.00, 'https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?auto=format&fit=crop&w=600&q=80'),
                (4, 2, 'Butter Croissant', 'Golden, flaky French pastry made with layers of pure butter for the ultimate melt-in-mouth crispiness.', 120.00, 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80'),
                (5, 2, 'Chocolate Croissant (Pain au Chocolat)', 'Crisp, golden laminated dough filled with two batons of rich semi-sweet Belgian chocolate.', 150.00, 'https://images.unsplash.com/photo-1530610476181-d83430b64dcd?auto=format&fit=crop&w=600&q=80'),
                (6, 2, 'Cinnamon Swirl Roll', 'Warm, pillowy dough rolled with aromatic Ceylon cinnamon and brown sugar, glazed with vanilla cream.', 140.00, 'https://images.unsplash.com/photo-1509365465985-25d11c17e812?auto=format&fit=crop&w=600&q=80'),
                (7, 3, 'Artisan Garlic Bread', 'Freshly baked baguette generously brushed with roasted garlic herb butter and parsley.', 130.00, 'https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?auto=format&fit=crop&w=600&q=80'),
                (8, 3, 'Rustic Sourdough Bread', 'Slow-fermented artisan sourdough loaf with an open crumb, crispy crust, and signature tangy flavor.', 180.00, 'https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?auto=format&fit=crop&w=600&q=80'),
                (9, 3, 'French Classic Baguette', 'Traditional long crusty loaf with a golden crackly crust and airy, chewy interior.', 110.00, 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80'),
                (10, 4, 'Chunky Chocolate Chip Cookies', 'Soft-baked cookies loaded with melted milk and dark chocolate chunks with crispy edges.', 160.00, 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=600&q=80'),
                (11, 4, 'Oatmeal Raisin & Nut Cookies', 'Hearty rolled oats baked with golden raisins, toasted walnuts, and a hint of warm nutmeg.', 140.00, 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&w=600&q=80'),
                (12, 4, 'Danish Butter Cookies', 'Traditional melt-in-your-mouth piped butter cookies with a subtle vanilla and rich buttery taste.', 150.00, 'https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?auto=format&fit=crop&w=600&q=80')
            ])

            cur.executemany("INSERT INTO orders (id, user_id, customer_name, phone, address, total_amount, status) VALUES (?, ?, ?, ?, ?, ?, ?)", [
                (101, 2, 'Rahul Sharma', '+91 9876543210', '142 MG Road, Indiranagar, Bengaluru, 560038', 700.00, 'Delivered'),
                (102, 2, 'Rahul Sharma', '+91 9876543210', '142 MG Road, Indiranagar, Bengaluru, 560038', 550.00, 'Preparing'),
                (103, None, 'Pooja Verma', '+91 9123456780', 'Flat 402, Sunshine Heights, Mumbai, 400050', 310.00, 'Pending')
            ])

            cur.executemany("INSERT INTO order_items (order_id, product_id, product_name, price, quantity, subtotal) VALUES (?, ?, ?, ?, ?, ?)", [
                (101, 1, 'Chocolate Truffle Cake', 550.00, 1, 550.00),
                (101, 5, 'Chocolate Croissant', 150.00, 1, 150.00),
                (102, 1, 'Chocolate Truffle Cake', 550.00, 1, 550.00),
                (103, 4, 'Butter Croissant', 120.00, 1, 120.00),
                (103, 8, 'Rustic Sourdough Bread', 180.00, 1, 180.00)
            ])
            conn.commit()
        cur.close()

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
        ensure_sqlite_initialized(conn)
        return conn

    # Try connecting to MySQL first (if configured in env)
    if os.getenv('DB_PASSWORD') is not None and os.getenv('DB_NAME'):
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
            pass

    # Fallback to local / serverless SQLite database
    db_path = get_sqlite_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ensure_sqlite_initialized(conn)
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
            sqlite_query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(sqlite_query, args)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            cursor.close()
            return (results[0] if results else None) if one else results
        else:
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
