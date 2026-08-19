-- ========================================================
-- Sweet Crumbs / Brownies Hub Database Seed Data
-- ========================================================

-- 1. INSERT CATEGORIES
INSERT INTO categories (id, name, slug, image) VALUES
(1, 'Cakes', 'cakes', 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=600&q=80'),
(2, 'Pastries', 'pastries', 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80'),
(3, 'Breads', 'breads', 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80'),
(4, 'Cookies', 'cookies', 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=600&q=80');

-- 2. INSERT DEMO USERS
-- Admin: admin@brownieshub.com / password: admin123
-- Customer: customer@gmail.com / password: customer123
-- (Password hashes generated with Werkzeug generate_password_hash)
INSERT INTO users (id, name, email, password, role) VALUES
(1, 'Bakery Admin', 'admin@brownieshub.com', 'scrypt:32768:8:1$uB0oP9wG2b6R0D5L$670e28f114c00ffc1bc16ecfa0922849e7b233a017d21b1b4bb1198542c38661ceb342ba9d28591ef520263f69a53ba2a46cbaefeeea4ecf7f32fc01c4ce5bb7', 'admin'),
(2, 'Rahul Sharma', 'customer@gmail.com', 'scrypt:32768:8:1$n4T9rXk2vM8Z1Q0L$a35123bb0b4cc575c3dbca1ef7e221d604e38c92a9cb2740bc135f5c90b6c66cf17f7b3dfbe32cf62e08e64627ef45cce6aeefecddb59c40db2460e6f6630f9a', 'customer');

-- 3. INSERT 12 SAMPLE BAKERY PRODUCTS
INSERT INTO products (id, category_id, name, description, price, image) VALUES
-- CAKES (category_id = 1)
(1, 1, 'Chocolate Truffle Cake', 'Rich, decadent dark chocolate layers coated with smooth chocolate ganache and chocolate curls.', 550.00, 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=600&q=80'),
(2, 1, 'Red Velvet Cake', 'Velvety crimson sponge layered with silky cream cheese frosting and a delicate crumb coating.', 650.00, 'https://images.unsplash.com/photo-1586788680434-30d324b2d46f?auto=format&fit=crop&w=600&q=80'),
(3, 1, 'Black Forest Cake', 'Classic German sponge infused with cherries, layered with fresh whipped cream and dark chocolate flakes.', 600.00, 'https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?auto=format&fit=crop&w=600&q=80'),

-- PASTRIES (category_id = 2)
(4, 2, 'Butter Croissant', 'Golden, flaky French pastry made with layers of pure butter for the ultimate melt-in-mouth crispiness.', 120.00, 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80'),
(5, 2, 'Chocolate Croissant (Pain au Chocolat)', 'Crisp, golden laminated dough filled with two batons of rich semi-sweet Belgian chocolate.', 150.00, 'https://images.unsplash.com/photo-1530610476181-d83430b64dcd?auto=format&fit=crop&w=600&q=80'),
(6, 2, 'Cinnamon Swirl Roll', 'Warm, pillowy dough rolled with aromatic Ceylon cinnamon and brown sugar, glazed with vanilla cream.', 140.00, 'https://images.unsplash.com/photo-1509365465985-25d11c17e812?auto=format&fit=crop&w=600&q=80'),

-- BREADS (category_id = 3)
(7, 3, 'Artisan Garlic Bread', 'Freshly baked baguette generously brushed with roasted garlic herb butter and parsley.', 130.00, 'https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?auto=format&fit=crop&w=600&q=80'),
(8, 3, 'Rustic Sourdough Bread', 'Slow-fermented artisan sourdough loaf with an open crumb, crispy crust, and signature tangy flavor.', 180.00, 'https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?auto=format&fit=crop&w=600&q=80'),
(9, 3, 'French Classic Baguette', 'Traditional long crusty loaf with a golden crackly crust and airy, chewy interior.', 110.00, 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80'),

-- COOKIES (category_id = 4)
(10, 4, 'Chunky Chocolate Chip Cookies', 'Soft-baked cookies loaded with melted milk and dark chocolate chunks with crispy edges.', 160.00, 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=600&q=80'),
(11, 4, 'Oatmeal Raisin & Nut Cookies', 'Hearty rolled oats baked with golden raisins, toasted walnuts, and a hint of warm nutmeg.', 140.00, 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&w=600&q=80'),
(12, 4, 'Danish Butter Cookies', 'Traditional melt-in-your-mouth piped butter cookies with a subtle vanilla and rich buttery taste.', 150.00, 'https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?auto=format&fit=crop&w=600&q=80');

-- 4. INSERT SAMPLE ORDERS FOR DEMO
INSERT INTO orders (id, user_id, customer_name, phone, address, total_amount, status) VALUES
(101, 2, 'Rahul Sharma', '+91 9876543210', '142 MG Road, Indiranagar, Bengaluru, 560038', 700.00, 'Delivered'),
(102, 2, 'Rahul Sharma', '+91 9876543210', '142 MG Road, Indiranagar, Bengaluru, 560038', 550.00, 'Preparing'),
(103, NULL, 'Pooja Verma', '+91 9123456780', 'Flat 402, Sunshine Heights, Mumbai, 400050', 310.00, 'Pending');

-- 5. INSERT SAMPLE ORDER ITEMS
INSERT INTO order_items (order_id, product_id, product_name, price, quantity, subtotal) VALUES
(101, 1, 'Chocolate Truffle Cake', 550.00, 1, 550.00),
(101, 5, 'Chocolate Croissant', 150.00, 1, 150.00),
(102, 1, 'Chocolate Truffle Cake', 550.00, 1, 550.00),
(103, 4, 'Butter Croissant', 120.00, 1, 120.00),
(103, 8, 'Rustic Sourdough Bread', 180.00, 1, 180.00);
