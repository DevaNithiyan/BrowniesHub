/**
 * Brownies Hub / Sweet Crumbs Bakery - Admin Management Logic
 * -----------------------------------------------------------
 * Handles:
 * 1. Product Add/Edit/Delete Modals and API calls
 * 2. Order status update dropdowns
 * 3. View order items detail modal
 */

// Global function to open any modal by ID
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('active');
}

// Global function to close any modal by ID
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
}

// -------------------------------------------------------------
// PRODUCT MANAGEMENT
// -------------------------------------------------------------

function openAddProductModal() {
    document.getElementById('productForm').reset();
    document.getElementById('productId').value = '';
    document.getElementById('productModalTitle').textContent = 'Add New Bakery Product';
    document.getElementById('saveProductBtn').textContent = 'Add Product';
    openModal('productModal');
}

function openEditProductModal(btn) {
    const id = btn.dataset.id;
    const name = btn.dataset.name;
    const categoryId = btn.dataset.categoryId;
    const price = btn.dataset.price;
    const image = btn.dataset.image;
    const description = btn.dataset.description;

    document.getElementById('productId').value = id;
    document.getElementById('productName').value = name;
    document.getElementById('productCategory').value = categoryId;
    document.getElementById('productPrice').value = price;
    document.getElementById('productImage').value = image;
    document.getElementById('productDescription').value = description;

    document.getElementById('productModalTitle').textContent = 'Edit Bakery Product';
    document.getElementById('saveProductBtn').textContent = 'Save Changes';
    openModal('productModal');
}

async function handleSaveProduct(event) {
    event.preventDefault();
    const id = document.getElementById('productId').value;
    const name = document.getElementById('productName').value.trim();
    const categoryId = document.getElementById('productCategory').value;
    const price = document.getElementById('productPrice').value;
    const image = document.getElementById('productImage').value.trim();
    const description = document.getElementById('productDescription').value.trim();

    if (!name || !categoryId || !price || !description) {
        showToast('Please fill in all required fields.', 'danger');
        return;
    }

    const payload = {
        name: name,
        category_id: categoryId,
        price: price,
        image: image,
        description: description
    };

    const isEdit = Boolean(id);
    const url = isEdit ? `/api/products/${id}` : '/api/products';
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        if (result.success) {
            showToast(result.message || 'Product saved successfully!', 'success');
            closeModal('productModal');
            setTimeout(() => window.location.reload(), 800);
        } else {
            showToast(result.message || 'Error saving product', 'danger');
        }
    } catch (err) {
        console.error('Error:', err);
        showToast('Failed to save product. Please try again.', 'danger');
    }
}

async function handleDeleteProduct(target, fallbackName) {
    const productId = (target && target.dataset) ? target.dataset.id : target;
    const productName = (target && target.dataset) ? target.dataset.name : (fallbackName || 'this product');

    if (!confirm(`Are you sure you want to delete "${productName}"? This action cannot be undone.`)) {
        return;
    }

    try {
        const response = await fetch(`/api/products/${productId}`, {
            method: 'DELETE'
        });

        const result = await response.json();
        if (result.success) {
            showToast(result.message || 'Product deleted successfully!', 'info');
            setTimeout(() => window.location.reload(), 700);
        } else {
            showToast(result.message || 'Failed to delete product', 'danger');
        }
    } catch (err) {
        console.error('Error deleting product:', err);
        showToast('Network error while deleting product.', 'danger');
    }
}

// -------------------------------------------------------------
// ORDER MANAGEMENT
// -------------------------------------------------------------

async function handleOrderStatusChange(selectEl, orderId) {
    const newStatus = selectEl.value;
    
    try {
        const response = await fetch(`/api/orders/${orderId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });

        const result = await response.json();
        if (result.success) {
            showToast(`Order #${orderId} status updated to ${newStatus}!`, 'success');
        } else {
            showToast(result.message || 'Failed to update order status', 'danger');
        }
    } catch (err) {
        console.error('Error updating order status:', err);
        showToast('Error updating order status.', 'danger');
    }
}

async function viewOrderDetails(orderId) {
    try {
        const response = await fetch(`/api/orders/${orderId}`);
        const result = await response.json();

        if (result.success) {
            const order = result.order;
            const items = result.items;

            document.getElementById('modalOrderId').textContent = `#${order.id}`;
            document.getElementById('modalCustomerName').textContent = order.customer_name;
            document.getElementById('modalCustomerPhone').textContent = order.phone;
            document.getElementById('modalCustomerAddress').textContent = order.address;
            document.getElementById('modalOrderStatus').textContent = order.status;
            document.getElementById('modalOrderTotal').textContent = `₹${parseFloat(order.total_amount).toFixed(2)}`;

            let itemsHtml = '';
            items.forEach(item => {
                itemsHtml += `
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border-subtle); font-size: 0.9rem;">
                        <div>
                            <strong>${item.product_name}</strong>
                            <div style="color: var(--text-muted); font-size: 0.8rem;">Qty: ${item.quantity} × ₹${parseFloat(item.price).toFixed(2)}</div>
                        </div>
                        <span style="font-weight: 700; color: var(--primary);">₹${parseFloat(item.subtotal).toFixed(2)}</span>
                    </div>
                `;
            });

            document.getElementById('modalOrderItems').innerHTML = itemsHtml;
            openModal('orderDetailsModal');
        }
    } catch (err) {
        console.error('Error loading order details:', err);
        showToast('Failed to load order details.', 'danger');
    }
}
