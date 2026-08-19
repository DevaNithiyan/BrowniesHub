/**
 * Brownies Hub / Sweet Crumbs Bakery - Cart Logic
 * -----------------------------------------------
 * Manages shopping cart state using browser's localStorage.
 * Beginner-Friendly & fully reactive across all pages.
 */

const CART_STORAGE_KEY = 'brownies_hub_cart';

/**
 * Retrieves the current cart array from localStorage
 * @returns {Array} Array of cart item objects
 */
function getCart() {
    try {
        const stored = localStorage.getItem(CART_STORAGE_KEY);
        return stored ? JSON.parse(stored) : [];
    } catch (e) {
        console.error('Error reading cart from localStorage', e);
        return [];
    }
}

/**
 * Saves the cart array to localStorage and updates badge count
 * @param {Array} cart - Cart item array
 */
function saveCart(cart) {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
    updateCartBadge();
}

/**
 * Adds a product to the cart or increments quantity if already present
 * @param {Object} product - Product data {id, name, price, image, category}
 * @param {number} quantity - Number of items to add
 */
function addToCart(product, quantity = 1) {
    const cart = getCart();
    const qty = parseInt(quantity, 10) || 1;
    
    const existingIndex = cart.findIndex(item => item.id === product.id);
    if (existingIndex > -1) {
        cart[existingIndex].quantity += qty;
    } else {
        cart.push({
            id: product.id,
            name: product.name,
            price: parseFloat(product.price),
            image: product.image,
            quantity: qty
        });
    }
    
    saveCart(cart);
    showToast(`Added ${qty}x "${product.name}" to cart! 🍰`, 'success');
}

/**
 * Updates the quantity of a specific item in the cart
 * @param {number} productId 
 * @param {number} newQuantity 
 */
function updateQuantity(productId, newQuantity) {
    let cart = getCart();
    const qty = parseInt(newQuantity, 10);
    
    if (qty <= 0) {
        removeFromCart(productId);
        return;
    }
    
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity = qty;
        saveCart(cart);
        // If on cart page, re-render
        if (document.getElementById('cartItemsContainer')) {
            renderCartPage();
        }
        if (document.getElementById('checkoutSummaryContainer')) {
            renderCheckoutSummary();
        }
    }
}

/**
 * Removes an item completely from the cart
 * @param {number} productId 
 */
function removeFromCart(productId) {
    let cart = getCart();
    const itemToRemove = cart.find(i => i.id === productId);
    cart = cart.filter(item => item.id !== productId);
    saveCart(cart);
    
    if (itemToRemove) {
        showToast(`Removed "${itemToRemove.name}" from cart.`, 'info');
    }
    
    if (document.getElementById('cartItemsContainer')) {
        renderCartPage();
    }
    if (document.getElementById('checkoutSummaryContainer')) {
        renderCheckoutSummary();
    }
}

/**
 * Clears the entire cart after checkout
 */
function clearCart() {
    localStorage.removeItem(CART_STORAGE_KEY);
    updateCartBadge();
}

/**
 * Calculates total number of items
 */
function getCartCount() {
    const cart = getCart();
    return cart.reduce((total, item) => total + item.quantity, 0);
}

/**
 * Calculates total price in INR
 */
function getCartTotal() {
    const cart = getCart();
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
}

/**
 * Updates all badge counters in the DOM
 */
function updateCartBadge() {
    const count = getCartCount();
    const badges = document.querySelectorAll('.cart-badge');
    badges.forEach(badge => {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    });
}

/**
 * Populates the Cart Page table and summary
 */
function renderCartPage() {
    const container = document.getElementById('cartItemsContainer');
    const emptyState = document.getElementById('emptyCartState');
    const cartContent = document.getElementById('cartContentLayout');
    const subtotalEl = document.getElementById('cartSubtotal');
    const totalEl = document.getElementById('cartTotal');
    
    if (!container) return;
    
    const cart = getCart();
    
    if (cart.length === 0) {
        if (emptyState) emptyState.style.display = 'block';
        if (cartContent) cartContent.style.display = 'none';
        return;
    }
    
    if (emptyState) emptyState.style.display = 'none';
    if (cartContent) cartContent.style.display = 'grid';
    
    let html = '';
    cart.forEach(item => {
        const itemTotal = (item.price * item.quantity).toFixed(2);
        html += `
            <tr>
                <td>
                    <div class="cart-item-info">
                        <img src="${item.image}" alt="${item.name}" class="cart-item-img" onerror="this.src='https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=600&q=80'">
                        <div>
                            <strong style="color: var(--primary); font-size: 1rem;">${item.name}</strong>
                            <div style="color: var(--text-muted); font-size: 0.85rem;">₹${item.price.toFixed(2)} each</div>
                        </div>
                    </div>
                </td>
                <td><strong>₹${item.price.toFixed(2)}</strong></td>
                <td>
                    <div class="quantity-control">
                        <button type="button" class="qty-btn" onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                        <input type="number" class="qty-input" value="${item.quantity}" min="1" onchange="updateQuantity(${item.id}, this.value)">
                        <button type="button" class="qty-btn" onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                    </div>
                </td>
                <td><strong style="color: var(--accent-hover); font-size: 1.05rem;">₹${itemTotal}</strong></td>
                <td style="text-align: center;">
                    <button type="button" class="btn btn-sm btn-secondary" onclick="removeFromCart(${item.id})" title="Remove item" style="padding: 6px 12px; color: var(--pink-accent);">
                        ✕
                    </button>
                </td>
            </tr>
        `;
    });
    
    container.innerHTML = html;
    
    const total = getCartTotal().toFixed(2);
    if (subtotalEl) subtotalEl.textContent = `₹${total}`;
    if (totalEl) totalEl.textContent = `₹${total}`;
}

/**
 * Populates Checkout Page summary
 */
function renderCheckoutSummary() {
    const container = document.getElementById('checkoutSummaryContainer');
    const totalEl = document.getElementById('checkoutTotal');
    if (!container) return;
    
    const cart = getCart();
    if (cart.length === 0) {
        window.location.href = '/cart';
        return;
    }
    
    let html = '';
    cart.forEach(item => {
        const itemTotal = (item.price * item.quantity).toFixed(2);
        html += `
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.8rem; font-size: 0.92rem;">
                <div>
                    <strong>${item.name}</strong>
                    <div style="color: var(--text-muted); font-size: 0.8rem;">Qty: ${item.quantity} × ₹${item.price.toFixed(2)}</div>
                </div>
                <span style="font-weight: 700; color: var(--primary);">₹${itemTotal}</span>
            </div>
        `;
    });
    
    container.innerHTML = html;
    const total = getCartTotal().toFixed(2);
    if (totalEl) totalEl.textContent = `₹${total}`;
}

// Auto-run badge update on script load
document.addEventListener('DOMContentLoaded', () => {
    updateCartBadge();
    if (document.getElementById('cartItemsContainer')) {
        renderCartPage();
    }
    if (document.getElementById('checkoutSummaryContainer')) {
        renderCheckoutSummary();
    }
});
