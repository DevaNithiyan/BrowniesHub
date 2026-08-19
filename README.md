# 🧁 Brownies Hub / Sweet Crumbs Bakery
> **Entry-Level Full-Stack Bakery Web Application for Developer Interviews**

Brownies Hub is a full-stack, responsive bakery web application built using **HTML5, CSS3, Vanilla JavaScript, Python (Flask), and MySQL / SQL**.

It is designed specifically for freshers and junior developers to demonstrate a clear understanding of frontend architecture, REST APIs, session authentication, database modeling, and CRUD operations without unnecessary over-engineering.

---

## 📸 Key Features

### 👤 Customer Experience
* **Bakery Showcase**: Hero section, bakery category cards (Cakes, Pastries, Breads, Cookies), featured products, and bakery story.
* **Menu Catalog & Live Search**: Instant live keyword search (e.g. *"cake"*, *"croissant"*) and dynamic category filters.
* **Product Details**: High-resolution image view, description, pure butter & ingredient highlights, quantity selector (+/-), and related suggestions.
* **Shopping Cart (localStorage)**: Real-time item additions, increment/decrement quantity, removal, subtotal & grand total in Indian Rupees (₹), and synced navbar badge counter.
* **Customer Authentication**: Account registration with email validation, password hashing (`Werkzeug`), and secure login sessions.
* **Checkout & Order Receipt**: Customer name, phone number, and delivery address form; stores order in MySQL database with auto-generated receipt (#Order ID, items, status).
* **100% Mobile Responsive**: Touch-friendly hamburger drawer navigation and responsive flexbox/grid layouts that look great on phones, tablets, and desktops.

### 🛡️ Admin Portal
* **Secure Admin Login**: Role-based access control ensuring only administrators access management features.
* **Analytics Dashboard**: Real-time business KPI cards (Total Products, Total Orders, Total Revenue in ₹, Pending Orders) and recent orders stream.
* **Product CRUD Management**: View all products in a data table, Add new products with category/price/image, Edit product details, and Delete products.
* **Order Management**: View customer orders and addresses, inspect line items in a popup modal, and update status (`Pending` ➔ `Preparing` ➔ `Ready` ➔ `Delivered` ➔ `Cancelled`).

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Vanilla, Responsive Grid & Flexbox), Vanilla JavaScript (ES6) |
| **Backend** | Python 3, Flask (RESTful routing, Sessions, Jinja2 Templates) |
| **Security** | Werkzeug Password Hashing (`scrypt`/`pbkdf2`), Session Cookies |
| **Database** | MySQL / Relational SQL (Tables: `users`, `categories`, `products`, `orders`, `order_items`) |
| **Storage** | Browser `localStorage` (Shopping Cart) |

---

## 📂 Project Structure

```text
brownieshub/
│
├── app.py                     # Main Flask application with routes and API endpoints
├── db.py                      # Database connector (MySQL with SQLite local fallback)
├── requirements.txt           # Python dependencies
├── .env                       # Active environment configuration
├── .env.example               # Template environment configuration
├── .gitignore                 # Files excluded from git
├── README.md                  # Project documentation & interview preparation guide
├── test_app.py                # Automated route & API test suite
│
├── database/
│   ├── schema.sql             # SQL table definitions
│   ├── seed.sql               # Initial seed data (12 products, categories, demo users)
│   └── init_db.py             # 1-Click Database initializer script
│
├── templates/
│   ├── base.html              # Shared header, mobile drawer, navbar, and footer
│   ├── index.html             # Bakery homepage
│   ├── products.html          # Menu catalog with live search & filters
│   ├── product-details.html   # Product details page
│   ├── login.html             # Customer login form
│   ├── register.html          # Customer registration form
│   ├── cart.html              # Shopping cart page
│   ├── checkout.html          # Checkout form & order review
│   ├── order-success.html     # Order confirmation receipt page
│   ├── admin-login.html       # Admin portal login
│   ├── admin-dashboard.html   # Admin metrics dashboard
│   ├── admin-products.html    # Admin product list & Add/Edit modal
│   └── admin-orders.html      # Admin orders & status dropdown
│
└── static/
    ├── css/
    │   └── style.css          # Vanilla CSS styling with mobile responsive breakpoints
    └── js/
        ├── main.js            # Mobile drawer navigation & toast notifications
        ├── cart.js            # LocalStorage cart management & badge updates
        ├── products.js        # Search filtering & category chip selection
        └── admin.js           # Admin product CRUD & order status updates
```

---

## 🚀 Complete Step-by-Step Local Setup

### Step 1: Open the Project in VS Code
Open VS Code, select **File** ➔ **Open Folder...**, and select the `brownieshub` folder.

### Step 2: Create a Virtual Environment
Open the VS Code Terminal (`Ctrl + \`` or `Terminal` ➔ `New Terminal`) and run:

**On Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database

#### Option A: Automated 1-Click Setup (Recommended)
Simply run the included initializer script:
```bash
python database/init_db.py
```
*If MySQL is running locally, it creates the `sweet_crumbs` database and inserts all tables and seed data automatically. If MySQL is not running, it initializes a local SQLite database so you can test immediately without setup errors!*

#### Option B: Manual MySQL Setup (via MySQL Workbench / Command Line)
1. Log in to MySQL:
   ```sql
   CREATE DATABASE sweet_crumbs;
   USE sweet_crumbs;
   ```
2. Run `database/schema.sql` to create the tables.
3. Run `database/seed.sql` to load the categories, 12 bakery products, and demo accounts.
4. Verify your `.env` file matches your MySQL credentials:
   ```ini
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=sweet_crumbs
   ```

### Step 5: Start the Flask Application
```bash
python app.py
```

### Step 6: Open in Browser
Open your browser and navigate to:
* **Customer Website**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
* **Admin Portal**: [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)

---

## ☁️ Cloud Hosting & Deployment Guide

You can easily host Brownies Hub live on **Render** or **Vercel** for free.

### 🟣 A. Deploy on Render (Recommended for Full Python/WSGI Support)

1. Push your project to a GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Brownies Hub"
   git branch -M main
   git remote add origin https://github.com/BlackHawk46x/BrowniesHub.git
   git push -u origin main
   ```
2. Go to [render.com](https://render.com) and log in.
3. Click **New +** ➔ **Web Service**.
4. Connect your GitHub repository.
5. Configure the service:
   * **Name**: `brownies-hub`
   * **Environment**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt && python database/init_db.py`
   * **Start Command**: `gunicorn app:app`
6. Under **Environment Variables**, add:
   * `SECRET_KEY`: `your_random_secret_key_here`
   *(Optional: If connecting to a cloud MySQL like Aiven / Railway, add `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`)*
7. Click **Deploy Web Service**. Your bakery website will be live at `https://brownies-hub.onrender.com`!

---

### ▲ B. Deploy on Vercel

1. Install the Vercel CLI (or connect via GitHub on [vercel.com](https://vercel.com)):
   ```bash
   npm i -g vercel
   ```
2. In the `brownieshub` directory, run:
   ```bash
   vercel
   ```
3. Follow the CLI prompts:
   * Set up and deploy: `Y`
   * Which scope: Select your account
   * Link to existing project: `N`
   * Project name: `brownies-hub`
   * Directory located: `./`
4. Deploy to production:
   ```bash
   vercel --prod
   ```
5. Your website will be live at `https://brownies-hub.vercel.app`!

---

## 🔑 Demo Login Accounts

| Role | Email | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@brownieshub.com` | `admin123` | Access Admin Dashboard, Add/Edit/Delete products, Update order statuses |
| **Customer** | `customer@gmail.com` | `customer123` | Browse menu, Add to cart, Checkout |

*(Both login pages also feature a 1-click **"Auto-Fill Demo Credentials"** button for interview demonstrations!)*

---

## 📱 Mobile & Responsive Preview

The website is engineered to be fully responsive:
* **Mobile Drawer Navigation**: Tap the hamburger menu (☰) on mobile screens to open the slide-out navigation menu.
* **Flexible Grids**: Product cards adjust seamlessly from 1 column on mobile to 2 columns on tablet and 3–4 columns on desktop.
* **Touch-Friendly Controls**: Large buttons, clear quantity selectors (+/-), and sticky summary cards prevent layout distortion on smaller viewports.

---

## 🎯 Interview Questions I Should Be Able To Answer

### 1. What is Flask?
**Answer:** Flask is a lightweight micro-web framework for Python. It provides the core essentials for web development (routing, request handling, Jinja2 template rendering, and session management) while giving developers freedom to structure their project cleanly without unnecessary boilerplate.

### 2. Why did you use Python for this project?
**Answer:** Python is readable, beginner-friendly, and has rich built-in support for web development, secure password hashing, and database connectors. Flask makes it simple to build both server-rendered HTML pages and RESTful JSON APIs in a few lines of code.

### 3. What is MySQL?
**Answer:** MySQL is an open-source Relational Database Management System (RDBMS) that organizes data into structured tables with rows and columns. It ensures data consistency, supports ACID transactions, and enforces relationships using foreign keys.

### 4. What is SQL?
**Answer:** SQL (Structured Query Language) is the standard language used to interact with relational databases to perform operations like `SELECT` (read), `INSERT` (create), `UPDATE` (modify), and `DELETE` (remove).

### 5. What is a Primary Key?
**Answer:** A Primary Key is a column (or set of columns) that uniquely identifies each row in a database table (e.g., `id` in the `products` table). It cannot contain `NULL` values and must be unique for every record.

### 6. What is a Foreign Key?
**Answer:** A Foreign Key is a column in one table that links to the Primary Key of another table (e.g., `category_id` in `products` references `id` in `categories`). It enforces referential integrity so that products cannot be assigned to non-existent categories.

### 7. How does the frontend communicate with Flask?
**Answer:** The frontend communicates with Flask in two ways:
1. **Server-Side Rendering (SSR)**: When the user navigates to URLs like `/` or `/products`, Flask renders Jinja2 HTML templates populated with database data.
2. **Asynchronous AJAX / Fetch API**: JavaScript sends asynchronous JSON requests (e.g., `POST /api/orders` or `PUT /api/orders/1/status`) to Flask endpoints without refreshing the page.

### 8. What is an API?
**Answer:** API stands for Application Programming Interface. It defines a set of rules and endpoints through which the client-side JavaScript can send and receive data (typically in JSON format) to and from the backend server.

### 9. What is a GET request?
**Answer:** A `GET` request is an HTTP method used to retrieve data from the server without modifying any data (e.g., `GET /api/products` or `GET /product/1`).

### 10. What is a POST request?
**Answer:** A `POST` request is an HTTP method used to submit new data to the server to create a resource or perform an action (e.g., `POST /api/register` or `POST /api/orders`).

### 11. What is a PUT request?
**Answer:** A `PUT` request is an HTTP method used to update or replace an existing resource on the server (e.g., `PUT /api/orders/101/status` to update an order's status).

### 12. What is a DELETE request?
**Answer:** A `DELETE` request is an HTTP method used to remove a specified resource from the database (e.g., `DELETE /api/products/5`).

### 13. How does User Login work in your application?
**Answer:** 
1. The user submits their email and password via the login form.
2. Flask queries the `users` table for the matching email.
3. If found, Flask verifies the entered password against the stored password hash using `check_password_hash()`.
4. If verified, Flask stores the user's `id`, `name`, and `role` in the encrypted server-side `session` cookie.

### 14. Why should passwords be hashed instead of stored as plain text?
**Answer:** Storing plain text passwords is a critical security vulnerability. If the database is compromised, user credentials would be exposed. Password hashing (using algorithms like `scrypt` or `pbkdf2`) is a one-way cryptographic function: the original password cannot be decrypted, but can only be verified by comparing hashes.

### 15. How does the shopping cart work?
**Answer:** The cart is managed on the client side using the browser's `localStorage`. When a user adds an item or modifies quantities, the cart JavaScript updates the stored JSON array, recalculates subtotals and totals in ₹, and updates the cart badge counter across all pages without needing a server call.

### 16. How is an order stored in MySQL?
**Answer:** When the customer clicks "Place Order", the checkout data is split into two relational tables:
1. **`orders` table**: Stores the overall order header (customer name, phone, delivery address, grand total, and status).
2. **`order_items` table**: Stores each individual product in the cart with `order_id`, `product_id`, `product_name`, `price`, `quantity`, and `subtotal`.

### 17. How did you connect Python with MySQL?
**Answer:** We used the `PyMySQL` / `mysql-connector-python` libraries. In `db.py`, we created helper functions (`query_db` for `SELECT` and `execute_db` for `INSERT`/`UPDATE`/`DELETE`) that read credentials from `.env`, establish a connection, execute the parameterized SQL queries, and return dictionary results.

### 18. What happens when a product or category is deleted?
**Answer:** In `schema.sql`, we defined `ON DELETE CASCADE` on the `products.category_id` foreign key. If a category is deleted, all associated products are automatically removed. For orders, `ON DELETE SET NULL` is used so order history remains intact even if a product is later removed from the menu.

### 19. What did you personally implement in this project?
**Answer:** I built the full-stack architecture from scratch:
- Created the database schema and seed data with foreign key constraints.
- Developed all Flask backend routing, session authentication, and REST endpoints.
- Designed the responsive frontend using modern Vanilla CSS with a warm bakery theme.
- Implemented client-side cart logic in Vanilla JavaScript with `localStorage` persistence.
- Built the Admin Dashboard with full CRUD capabilities for products and real-time order status tracking.

### 20. What would you improve in Version 2?
**Answer:** In Version 2, I would add:
1. Online payment gateway integration (such as Razorpay / Stripe test mode).
2. Image file upload with AWS S3 or Cloudinary storage instead of image URLs.
3. Automated email/SMS order confirmations using SendGrid or Twilio.
4. Customer order history dashboard to re-order previous favorites.
5. Pagination for the product catalog when scaling to hundreds of bakery items.

---

## 📜 License & Acknowledgments
Built with ❤️ for fresher developer portfolio presentations. Free to use, customize, and study.
