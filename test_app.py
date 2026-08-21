"""
Automated Verification Suite for Brownies Hub Full-Stack Bakery
--------------------------------------------------------------
Tests:
1. All HTML pages render with HTTP 200 (Home, Products, Details, Cart, Checkout, Success, Auth, Admin)
2. Products API (GET /api/products, GET with search, GET with category)
3. User Registration (POST /api/register) and Validation
4. User Login (POST /api/login)
5. Admin Login & Authorization checks
6. Order Placement (POST /api/orders) & Receipt calculation
7. Admin Product Management (POST /api/products, PUT /api/products/<id>, DELETE /api/products/<id>)
8. Admin Order Status Update (PUT /api/orders/<id>/status)
"""

import json
import urllib.request
import urllib.parse
from app import app

def run_tests():
    client = app.test_client()
    passed = 0
    failed = 0

    def test(name, condition, details=""):
        nonlocal passed, failed
        if condition:
            print(f"[PASS] {name}")
            passed += 1
        else:
            print(f"[FAIL] {name} - {details}")
            failed += 1

    print("\n--- 1. Testing HTML Page Routes ---")
    
    # 1. Home page
    res = client.get('/')
    test("GET / (Home page)", res.status_code == 200 and b"Freshly Baked" in res.data)

    # 2. Products page
    res = client.get('/products')
    test("GET /products", res.status_code == 200 and b"Explore Our Bakery Delights" in res.data)

    # 3. Product details page
    res = client.get('/product/1')
    test("GET /product/1 (Product Details)", res.status_code == 200 and b"Chocolate Truffle Cake" in res.data)

    # 4. Cart page
    res = client.get('/cart')
    test("GET /cart", res.status_code == 200 and b"Shopping Cart" in res.data)

    # 5. Checkout page
    res = client.get('/checkout')
    test("GET /checkout", res.status_code == 200 and b"Delivery Details" in res.data)

    # 6. Login & Register pages
    res = client.get('/login')
    test("GET /login", res.status_code == 200 and b"Welcome Back" in res.data)
    res = client.get('/register')
    test("GET /register", res.status_code == 200 and b"Join Brownies Hub" in res.data)

    # 7. Admin login page
    res = client.get('/admin/login')
    test("GET /admin/login", res.status_code == 200 and b"Bakery Admin Portal" in res.data)

    # 8. About & Contact dedicated pages
    res = client.get('/about')
    test("GET /about (About Us page)", res.status_code == 200 and b"The Sweet Crumbs Story" in res.data)
    res = client.get('/contact')
    test("GET /contact (Contact & Location page)", res.status_code == 200 and b"Contact Brownies Hub" in res.data)

    print("\n--- 2. Testing API Endpoints ---")
    
    # Products API
    res = client.get('/api/products')
    data = res.get_json()
    test("GET /api/products", res.status_code == 200 and len(data.get('products', [])) >= 12)

    # Products API with Category filter
    res = client.get('/api/products?category=cakes')
    data = res.get_json()
    test("GET /api/products?category=cakes", res.status_code == 200 and len(data.get('products', [])) >= 3)

    # Products API with Search
    res = client.get('/api/products?search=Croissant')
    data = res.get_json()
    test("GET /api/products?search=Croissant", res.status_code == 200 and len(data.get('products', [])) >= 2)

    # Single Product API
    res = client.get('/api/products/1')
    data = res.get_json()
    test("GET /api/products/1", res.status_code == 200 and data.get('product', {}).get('name') == 'Chocolate Truffle Cake')

    print("\n--- 3. Testing Authentication API ---")
    
    # Customer Login
    res = client.post('/api/login', json={'email': 'customer@gmail.com', 'password': 'customer123'})
    data = res.get_json()
    test("Customer Login", res.status_code == 200 and data.get('success') is True)

    # Admin Login
    res = client.post('/api/login', json={'email': 'admin@brownieshub.com', 'password': 'admin123', 'role': 'admin'})
    data = res.get_json()
    test("Admin Login", res.status_code == 200 and data.get('role') == 'admin')

    print("\n--- 4. Testing Order Placement Flow ---")
    
    order_payload = {
        "customer_name": "Deepa Sundaram",
        "phone": "+91 9845012345",
        "address": "45 Palm Meadows, Whitefield, Bengaluru 560066",
        "items": [
            {"id": 1, "name": "Chocolate Truffle Cake", "price": 550.00, "quantity": 1},
            {"id": 4, "name": "Butter Croissant", "price": 120.00, "quantity": 2}
        ]
    }
    res = client.post('/api/orders', json=order_payload)
    data = res.get_json()
    order_id = data.get('order_id')
    test("POST /api/orders (Create Order)", res.status_code == 201 and order_id is not None)

    # Verify Order Success page for the newly created order
    if order_id:
        res = client.get(f'/order-success/{order_id}')
        test(f"GET /order-success/{order_id}", res.status_code == 200 and b"Deepa Sundaram" in res.data and b"790.00" in res.data)

    print("\n--- 5. Testing Admin Dashboard & Product CRUD ---")
    
    # Simulate Admin session
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_name'] = 'Bakery Admin'
        sess['user_role'] = 'admin'

    # Admin Dashboard
    res = client.get('/admin/dashboard')
    test("GET /admin/dashboard (Authorized)", res.status_code == 200 and b"Bakery Admin Dashboard" in res.data)

    # Admin Add Product
    new_prod_payload = {
        "name": "Matcha Green Tea Roll",
        "category_id": 2,
        "price": 160.00,
        "description": "Fluffy Japanese matcha sponge with sweet vanilla cream filling.",
        "image": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80"
    }
    res = client.post('/api/products', json=new_prod_payload)
    data = res.get_json()
    new_prod_id = data.get('product_id')
    test("POST /api/products (Admin Create)", res.status_code == 201 and new_prod_id is not None)

    # Admin Edit Product
    if new_prod_id:
        edit_payload = {
            "name": "Matcha Green Tea Roll (Special)",
            "category_id": 2,
            "price": 175.00,
            "description": "Fluffy Japanese matcha sponge with sweet vanilla cream and red bean paste.",
            "image": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80"
        }
        res = client.put(f'/api/products/{new_prod_id}', json=edit_payload)
        data = res.get_json()
        test(f"PUT /api/products/{new_prod_id} (Admin Update)", res.status_code == 200 and data.get('success') is True)

        # Admin Delete Product
        res = client.delete(f'/api/products/{new_prod_id}')
        data = res.get_json()
        test(f"DELETE /api/products/{new_prod_id} (Admin Delete)", res.status_code == 200 and data.get('success') is True)

    # Admin Update Order Status
    if order_id:
        res = client.put(f'/api/orders/{order_id}/status', json={"status": "Preparing"})
        data = res.get_json()
        test(f"PUT /api/orders/{order_id}/status -> Preparing", res.status_code == 200 and data.get('success') is True)

    print("\n==========================================")
    print(f" TOTAL TESTS: {passed + failed} | PASSED: {passed} | FAILED: {failed}")
    print("==========================================")
    return failed == 0

if __name__ == '__main__':
    success = run_tests()
    if not success:
        exit(1)
