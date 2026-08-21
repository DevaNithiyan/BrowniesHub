"""
===================================================================
Brownies Hub / Sweet Crumbs Bakery - Main Flask Application
===================================================================
An entry-level full-stack bakery web application built with:
- Frontend: HTML5, CSS3, Vanilla JavaScript
- Backend: Python + Flask
- Database: MySQL (with SQL queries and fallback SQLite)

Author: Entry-Level Developer Portfolio
===================================================================
"""

import os
import re
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Import our custom database helper functions
from db import query_db, execute_db

# Load environment variables from .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask application with absolute template and static folders
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
    static_url_path='/static'
)

# Secret key is required for Flask session cookies
app.secret_key = os.getenv('SECRET_KEY', 'brownies_hub_secret_key_2026')


class VercelPathMiddleware:
    """
    WSGI middleware that fixes PATH_INFO on Vercel deployments.
    Restores the original request path from __path query parameter,
    HTTP_X_MATCHED_PATH, or REQUEST_URI.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        import urllib.parse
        qs = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(qs)
        
        # 1. Check __path query parameter injected by vercel.json rewrite
        if '__path' in params and params['__path']:
            path = params['__path'][0]
            if path and not path.startswith('/api/index'):
                if not path.startswith('/'):
                    path = '/' + path
                environ['PATH_INFO'] = path
                clean_params = {k: v for k, v in params.items() if k != '__path'}
                environ['QUERY_STRING'] = urllib.parse.urlencode(clean_params, doseq=True)
                return self.wsgi_app(environ, start_response)
                
        # 2. Check X-Matched-Path header
        matched_path = environ.get('HTTP_X_MATCHED_PATH')
        if matched_path and matched_path != '/404' and not matched_path.startswith('/api/index'):
            path = matched_path.split('?')[0]
            environ['PATH_INFO'] = path
        elif environ.get('PATH_INFO') in ('/api/index.py', '/api/index', '/api', '', None):
            raw_uri = environ.get('REQUEST_URI') or environ.get('RAW_URI') or environ.get('HTTP_X_VERCEL_PATH') or '/'
            path = raw_uri.split('?')[0]
            if path and not path.startswith('/api/index'):
                environ['PATH_INFO'] = path

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)


# -------------------------------------------------------------------
# HELPER DECORATORS & AUTH UTILITIES
# -------------------------------------------------------------------

def login_required(f):
    """Decorator to ensure customer is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to ensure admin is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'admin':
            flash('Admin access required. Please log in as administrator.', 'danger')
            return redirect(url_for('admin_login_page'))
        return f(*args, **kwargs)
    return decorated_function

def is_valid_email(email):
    """Simple regex to validate email format."""
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None


# -------------------------------------------------------------------
# CONTEXT PROCESSOR (Available in all Jinja2 HTML templates)
# -------------------------------------------------------------------
@app.context_processor
def inject_global_data():
    """Provides session info and category list to every template automatically."""
    categories = query_db("SELECT * FROM categories ORDER BY id ASC")
    return {
        'current_user': {
            'id': session.get('user_id'),
            'name': session.get('user_name'),
            'email': session.get('user_email'),
            'role': session.get('user_role'),
            'is_authenticated': 'user_id' in session,
            'is_admin': session.get('user_role') == 'admin'
        },
        'nav_categories': categories or []
    }


# ===================================================================
# 1. FRONTEND PAGE ROUTES (HTML Rendering)
# ===================================================================

@app.route('/')
def home_page():
    """Renders the Bakery Home Page with hero, categories, and featured products."""
    # Fetch 6 featured products
    featured_products = query_db("""
        SELECT p.*, c.name AS category_name 
        FROM products p 
        JOIN categories c ON p.category_id = c.id 
        ORDER BY p.id ASC 
        LIMIT 6
    """)
    categories = query_db("SELECT * FROM categories ORDER BY id ASC")
    return render_template('index.html', featured_products=featured_products, categories=categories)


@app.route('/products')
def products_page():
    """Renders the Products Catalog page with search and category filtering."""
    category_filter = request.args.get('category', 'all')
    search_query = request.args.get('search', '').strip()
    
    # Build SQL query based on filters
    sql = """
        SELECT p.*, c.name AS category_name, c.slug AS category_slug 
        FROM products p 
        JOIN categories c ON p.category_id = c.id
    """
    params = []
    conditions = []
    
    if category_filter and category_filter != 'all':
        conditions.append("(c.slug = %s OR c.id = %s)")
        params.extend([category_filter, category_filter])
        
    if search_query:
        conditions.append("(p.name LIKE %s OR p.description LIKE %s)")
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
        
    sql += " ORDER BY p.id ASC"
    
    products = query_db(sql, params)
    categories = query_db("SELECT * FROM categories ORDER BY id ASC")
    
    return render_template('products.html', 
                           products=products, 
                           categories=categories, 
                           active_category=category_filter, 
                           search_query=search_query)


@app.route('/product/<int:product_id>')
def product_details_page(product_id):
    """Renders the individual Product Details page."""
    # Fetch product by ID
    product = query_db("""
        SELECT p.*, c.name AS category_name, c.slug AS category_slug 
        FROM products p 
        JOIN categories c ON p.category_id = c.id 
        WHERE p.id = %s
    """, [product_id], one=True)
    
    if not product:
        flash('Product not found.', 'warning')
        return redirect(url_for('products_page'))
        
    # Fetch related products from the same category
    related_products = query_db("""
        SELECT p.*, c.name AS category_name 
        FROM products p 
        JOIN categories c ON p.category_id = c.id 
        WHERE p.category_id = %s AND p.id != %s 
        LIMIT 3
    """, [product['category_id'], product_id])
    
    return render_template('product-details.html', product=product, related_products=related_products)


@app.route('/cart')
def cart_page():
    """Renders the Shopping Cart page."""
    return render_template('cart.html')


@app.route('/checkout')
def checkout_page():
    """Renders the Checkout page."""
    return render_template('checkout.html')


@app.route('/order-success/<int:order_id>')
def order_success_page(order_id):
    """Renders the Order Confirmation receipt page."""
    order = query_db("SELECT * FROM orders WHERE id = %s", [order_id], one=True)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('home_page'))
        
    order_items = query_db("SELECT * FROM order_items WHERE order_id = %s", [order_id])
    return render_template('order-success.html', order=order, order_items=order_items)


@app.route('/login')
def login_page():
    """Renders the Customer Login page."""
    if 'user_id' in session and session.get('user_role') == 'customer':
        return redirect(url_for('products_page'))
    return render_template('login.html')


@app.route('/register')
def register_page():
    """Renders the Customer Registration page."""
    if 'user_id' in session:
        return redirect(url_for('home_page'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    """Clears the session and logs the user out."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home_page'))


# ===================================================================
# 2. ADMIN PAGES (Admin Authentication & Management)
# ===================================================================

@app.route('/admin/login')
def admin_login_page():
    """Renders the Admin Login page."""
    if 'user_id' in session and session.get('user_role') == 'admin':
        return redirect(url_for('admin_dashboard_page'))
    return render_template('admin-login.html')


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard_page():
    """Renders the Admin Dashboard with key business metrics."""
    # Count total products
    prod_count = query_db("SELECT COUNT(*) AS total FROM products", one=True)
    # Count total orders
    order_count = query_db("SELECT COUNT(*) AS total FROM orders", one=True)
    # Count pending orders
    pending_count = query_db("SELECT COUNT(*) AS total FROM orders WHERE status = 'Pending'", one=True)
    # Sum total revenue
    revenue_res = query_db("SELECT SUM(total_amount) AS total FROM orders WHERE status != 'Cancelled'", one=True)
    
    total_revenue = revenue_res['total'] if revenue_res and revenue_res['total'] else 0.0
    
    # Fetch 5 most recent orders
    recent_orders = query_db("""
        SELECT * FROM orders 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    stats = {
        'total_products': prod_count['total'] if prod_count else 0,
        'total_orders': order_count['total'] if order_count else 0,
        'pending_orders': pending_count['total'] if pending_count else 0,
        'total_revenue': round(float(total_revenue), 2)
    }
    
    return render_template('admin-dashboard.html', stats=stats, recent_orders=recent_orders)


@app.route('/admin/products')
@admin_required
def admin_products_page():
    """Renders the Admin Product Management page (View, Add, Edit, Delete)."""
    products = query_db("""
        SELECT p.*, c.name AS category_name 
        FROM products p 
        JOIN categories c ON p.category_id = c.id 
        ORDER BY p.id DESC
    """)
    categories = query_db("SELECT * FROM categories ORDER BY id ASC")
    return render_template('admin-products.html', products=products, categories=categories)


@app.route('/admin/orders')
@admin_required
def admin_orders_page():
    """Renders the Admin Order Management page."""
    orders = query_db("SELECT * FROM orders ORDER BY created_at DESC")
    return render_template('admin-orders.html', orders=orders)


# ===================================================================
# 3. REST API ENDPOINTS (For AJAX / Fetch Requests)
# ===================================================================

# --- A. PRODUCTS API ---

@app.route('/api/products', methods=['GET'])
def api_get_products():
    """Returns JSON list of products with optional category and search filters."""
    category = request.args.get('category', 'all')
    search = request.args.get('search', '').strip()
    
    sql = """
        SELECT p.*, c.name AS category_name, c.slug AS category_slug 
        FROM products p 
        JOIN categories c ON p.category_id = c.id
    """
    params = []
    conditions = []
    
    if category and category != 'all':
        conditions.append("(c.slug = %s OR c.id = %s)")
        params.extend([category, category])
        
    if search:
        conditions.append("(p.name LIKE %s OR p.description LIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
        
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
        
    sql += " ORDER BY p.id ASC"
    
    products = query_db(sql, params)
    return jsonify({'success': True, 'products': products})


@app.route('/api/products/<int:product_id>', methods=['GET'])
def api_get_product_detail(product_id):
    """Returns single product details as JSON."""
    product = query_db("""
        SELECT p.*, c.name AS category_name, c.slug AS category_slug 
        FROM products p 
        JOIN categories c ON p.category_id = c.id 
        WHERE p.id = %s
    """, [product_id], one=True)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
        
    return jsonify({'success': True, 'product': product})


@app.route('/api/products', methods=['POST'])
@admin_required
def api_create_product():
    """Admin endpoint to create a new bakery product."""
    data = request.get_json() if request.is_json else request.form
    
    name = data.get('name', '').strip()
    category_id = data.get('category_id')
    price = data.get('price')
    description = data.get('description', '').strip()
    image = data.get('image', '').strip()
    
    # Input validation
    if not name or not category_id or not price or not description:
        return jsonify({'success': False, 'message': 'All product fields are required.'}), 400
        
    # Default placeholder image if none provided
    if not image:
        image = "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=600&q=80"
        
    try:
        price_val = float(price)
        cat_id_val = int(category_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid price or category format.'}), 400
        
    new_id = execute_db("""
        INSERT INTO products (category_id, name, description, price, image) 
        VALUES (%s, %s, %s, %s, %s)
    """, [cat_id_val, name, description, price_val, image], return_id=True)
    
    return jsonify({'success': True, 'message': 'Product added successfully!', 'product_id': new_id}), 201


@app.route('/api/products/<int:product_id>', methods=['PUT', 'POST'])
@admin_required
def api_update_product(product_id):
    """Admin endpoint to update an existing bakery product."""
    data = request.get_json() if request.is_json else request.form
    
    name = data.get('name', '').strip()
    category_id = data.get('category_id')
    price = data.get('price')
    description = data.get('description', '').strip()
    image = data.get('image', '').strip()
    
    if not name or not category_id or not price or not description:
        return jsonify({'success': False, 'message': 'All product fields are required.'}), 400
        
    try:
        price_val = float(price)
        cat_id_val = int(category_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid price or category format.'}), 400
        
    execute_db("""
        UPDATE products 
        SET category_id = %s, name = %s, description = %s, price = %s, image = %s 
        WHERE id = %s
    """, [cat_id_val, name, description, price_val, image, product_id])
    
    return jsonify({'success': True, 'message': 'Product updated successfully!'})


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@app.route('/api/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def api_delete_product(product_id):
    """Admin endpoint to delete a product."""
    execute_db("DELETE FROM products WHERE id = %s", [product_id])
    return jsonify({'success': True, 'message': 'Product deleted successfully.'})


# --- B. USER AUTHENTICATION API ---

@app.route('/api/register', methods=['POST'])
def api_register():
    """Handles new customer account registration."""
    data = request.get_json() if request.is_json else request.form
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # 1. Validation: check empty fields
    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Please fill in all required fields.'}), 400
        
    # 2. Validation: email format
    if not is_valid_email(email):
        return jsonify({'success': False, 'message': 'Please provide a valid email address.'}), 400
        
    # 3. Validation: password length
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long.'}), 400
        
    # 4. Check if email already registered
    existing_user = query_db("SELECT id FROM users WHERE email = %s", [email], one=True)
    if existing_user:
        return jsonify({'success': False, 'message': 'An account with this email already exists.'}), 409
        
    # 5. Hash password with Werkzeug (never store plain text passwords!)
    hashed_password = generate_password_hash(password)
    
    # 6. Save user to database
    user_id = execute_db("""
        INSERT INTO users (name, email, password, role) 
        VALUES (%s, %s, %s, 'customer')
    """, [name, email, hashed_password], return_id=True)
    
    # 7. Log the user in automatically via Flask session
    session['user_id'] = user_id
    session['user_name'] = name
    session['user_email'] = email
    session['user_role'] = 'customer'
    
    return jsonify({'success': True, 'message': 'Registration successful! Welcome to Brownies Hub.'}), 201


@app.route('/api/login', methods=['POST'])
def api_login():
    """Handles customer and admin login verification."""
    data = request.get_json() if request.is_json else request.form
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    requested_role = data.get('role', None) # Optional: can specify 'admin'
    
    # Validate fields
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400
        
    # Fetch user from database
    user = query_db("SELECT * FROM users WHERE email = %s", [email], one=True)
    
    # Verify password hash
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
        
    # Check if admin role required
    if requested_role == 'admin' and user['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Access denied: Admin privileges required.'}), 403
        
    # Store user identity in Flask session
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    session['user_role'] = user['role']
    
    redirect_destination = url_for('admin_dashboard_page') if user['role'] == 'admin' else url_for('products_page')
    
    return jsonify({
        'success': True, 
        'message': f"Welcome back, {user['name']}!", 
        'role': user['role'],
        'redirect_url': redirect_destination
    })


# --- C. ORDERS API ---

@app.route('/api/orders', methods=['POST'])
def api_create_order():
    """
    Creates a new bakery order.
    Receives customer contact information and cart items array.
    Saves data into 'orders' and 'order_items' tables.
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid order data.'}), 400
        
    customer_name = data.get('customer_name', '').strip()
    phone = data.get('phone', '').strip()
    address = data.get('address', '').strip()
    items = data.get('items', [])
    
    # 1. Validation
    if not customer_name or not phone or not address:
        return jsonify({'success': False, 'message': 'Customer name, phone number, and address are required.'}), 400
        
    if not items or len(items) == 0:
        return jsonify({'success': False, 'message': 'Your cart is empty. Please add products to order.'}), 400
        
    # 2. Calculate grand total
    total_amount = 0.0
    for item in items:
        try:
            price = float(item.get('price', 0))
            qty = int(item.get('quantity', 1))
            total_amount += (price * qty)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid item price or quantity in cart.'}), 400
            
    user_id = session.get('user_id', None)
    
    # 3. Insert into 'orders' table
    order_id = execute_db("""
        INSERT INTO orders (user_id, customer_name, phone, address, total_amount, status) 
        VALUES (%s, %s, %s, %s, %s, 'Pending')
    """, [user_id, customer_name, phone, address, round(total_amount, 2)], return_id=True)
    
    # 4. Insert each item into 'order_items' table
    for item in items:
        product_id = item.get('id')
        product_name = item.get('name', 'Bakery Item')
        price = float(item.get('price', 0))
        qty = int(item.get('quantity', 1))
        subtotal = round(price * qty, 2)
        
        execute_db("""
            INSERT INTO order_items (order_id, product_id, product_name, price, quantity, subtotal) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [order_id, product_id, product_name, price, qty, subtotal])
        
    return jsonify({
        'success': True, 
        'message': 'Order placed successfully!', 
        'order_id': order_id
    }), 201


@app.route('/api/orders', methods=['GET'])
@admin_required
def api_get_orders():
    """Admin endpoint to get all orders."""
    orders = query_db("SELECT * FROM orders ORDER BY created_at DESC")
    return jsonify({'success': True, 'orders': orders})


@app.route('/api/orders/<int:order_id>', methods=['GET'])
def api_get_order_details(order_id):
    """Fetches full order details including line items."""
    order = query_db("SELECT * FROM orders WHERE id = %s", [order_id], one=True)
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
        
    items = query_db("SELECT * FROM order_items WHERE order_id = %s", [order_id])
    return jsonify({'success': True, 'order': order, 'items': items})


@app.route('/api/orders/<int:order_id>/status', methods=['PUT', 'POST'])
@admin_required
def api_update_order_status(order_id):
    """Admin endpoint to update order status (Pending, Preparing, Ready, Delivered, Cancelled)."""
    data = request.get_json() if request.is_json else request.form
    new_status = data.get('status', '').strip()
    
    allowed_statuses = ['Pending', 'Preparing', 'Ready', 'Delivered', 'Cancelled']
    if new_status not in allowed_statuses:
        return jsonify({'success': False, 'message': f'Invalid status. Allowed: {", ".join(allowed_statuses)}'}), 400
        
    execute_db("UPDATE orders SET status = %s WHERE id = %s", [new_status, order_id])
    return jsonify({'success': True, 'message': f'Order status updated to {new_status}.'})


@app.route('/logo/<path:filename>')
def serve_logo(filename):
    """Serves logo files directly from logo or static/images folder."""
    logo_dir = os.path.join(os.path.dirname(__file__), 'logo')
    if os.path.exists(os.path.join(logo_dir, filename)):
        return send_from_directory(logo_dir, filename)
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static', 'images'), filename)


# -------------------------------------------------------------------
# ERROR HANDLERS (User-Friendly Error Pages)
# -------------------------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('404.html'), 500


# -------------------------------------------------------------------
# SERVER STARTUP
# -------------------------------------------------------------------
if __name__ == '__main__':
    # Initialize DB tables if needed
    try:
        from database.init_db import init_mysql, init_sqlite
        # If DB connection fails, auto init SQLite fallback
        try:
            query_db("SELECT 1 FROM products LIMIT 1")
        except Exception:
            print("Database not initialized yet. Auto-initializing fallback...")
            init_sqlite()
    except Exception as e:
        print(f"Startup DB check notice: {e}")
        
    print("=======================================================")
    print(" Brownies Hub Bakery Application is running!")
    print(" Local URL: http://127.0.0.1:5000")
    print(" Admin URL: http://127.0.0.1:5000/admin/login")
    print("=======================================================")
    app.run(debug=True, host='0.0.0.0', port=5000)
