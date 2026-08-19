"""
Database Initialization Script for Sweet Crumbs / Brownies Hub
--------------------------------------------------------------
This script sets up the database schema and loads sample seed data.
It can initialize either MySQL or a local SQLite database.
"""

import os
import sys
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'sweet_crumbs')

def init_mysql():
    """Initializes MySQL database with tables and seed data."""
    try:
        import pymysql
        print(f"Connecting to MySQL server at {DB_HOST}:{DB_PORT}...")
        
        # Connect to MySQL server without selecting database first
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            autocommit=True
        )
        cursor = conn.cursor()
        
        # Create database if it does not exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"Database `{DB_NAME}` ensured.")
        cursor.close()
        conn.close()

        # Connect to the target database
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            autocommit=True
        )
        cursor = conn.cursor()

        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Split and execute individual queries
        for statement in schema_sql.split(';'):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)
        print("Schema tables created successfully in MySQL.")

        # Read and execute seed.sql
        seed_path = os.path.join(os.path.dirname(__file__), 'seed.sql')
        with open(seed_path, 'r', encoding='utf-8') as f:
            seed_sql = f.read()

        for statement in seed_sql.split(';'):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)
        print("Seed data inserted successfully in MySQL.")

        cursor.close()
        conn.close()
        print("MySQL database initialization completed successfully!")
        return True

    except Exception as e:
        print(f"[Warning] MySQL connection error: {e}")
        print("Could not connect to MySQL. Checking SQLite fallback...")
        return False

def init_sqlite():
    """Initializes local SQLite database as fallback for testing."""
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sweet_crumbs.db')
    print(f"Creating local SQLite database at: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing tables
    cursor.executescript("""
    DROP TABLE IF EXISTS order_items;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS categories;
    DROP TABLE IF EXISTS users;

    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'customer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        image TEXT
    );

    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        image TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
    );

    CREATE TABLE orders (
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

    CREATE TABLE order_items (
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

    # Seed data
    admin_pw = generate_password_hash('admin123')
    cust_pw = generate_password_hash('customer123')

    cursor.executemany("INSERT INTO categories (id, name, slug, image) VALUES (?, ?, ?, ?)", [
        (1, 'Cakes', 'cakes', 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=600&q=80'),
        (2, 'Pastries', 'pastries', 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80'),
        (3, 'Breads', 'breads', 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80'),
        (4, 'Cookies', 'cookies', 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=600&q=80')
    ])

    cursor.executemany("INSERT INTO users (id, name, email, password, role) VALUES (?, ?, ?, ?, ?)", [
        (1, 'Bakery Admin', 'admin@brownieshub.com', admin_pw, 'admin'),
        (2, 'Rahul Sharma', 'customer@gmail.com', cust_pw, 'customer')
    ])

    cursor.executemany("INSERT INTO products (id, category_id, name, description, price, image) VALUES (?, ?, ?, ?, ?, ?)", [
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

    cursor.executemany("INSERT INTO orders (id, user_id, customer_name, phone, address, total_amount, status) VALUES (?, ?, ?, ?, ?, ?, ?)", [
        (101, 2, 'Rahul Sharma', '+91 9876543210', '142 MG Road, Indiranagar, Bengaluru, 560038', 700.00, 'Delivered'),
        (102, 2, 'Rahul Sharma', '+91 9876543210', '142 MG Road, Indiranagar, Bengaluru, 560038', 550.00, 'Preparing'),
        (103, None, 'Pooja Verma', '+91 9123456780', 'Flat 402, Sunshine Heights, Mumbai, 400050', 310.00, 'Pending')
    ])

    cursor.executemany("INSERT INTO order_items (order_id, product_id, product_name, price, quantity, subtotal) VALUES (?, ?, ?, ?, ?, ?)", [
        (101, 1, 'Chocolate Truffle Cake', 550.00, 1, 550.00),
        (101, 5, 'Chocolate Croissant', 150.00, 1, 150.00),
        (102, 1, 'Chocolate Truffle Cake', 550.00, 1, 550.00),
        (103, 4, 'Butter Croissant', 120.00, 1, 120.00),
        (103, 8, 'Rustic Sourdough Bread', 180.00, 1, 180.00)
    ])

    conn.commit()
    conn.close()
    print("Local database initialized successfully!")

if __name__ == '__main__':
    print("========================================")
    print(" Initializing Brownies Hub Database")
    print("========================================")
    success = init_mysql()
    if not success:
        print("\nNote: MySQL server was not reachable. Initialized fallback SQLite database so you can test right away!")
        init_sqlite()
    print("\nDatabase is ready!")
