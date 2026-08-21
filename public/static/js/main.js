/**
 * Brownies Hub / Sweet Crumbs Bakery - Main JavaScript
 * ----------------------------------------------------
 * Handles:
 * 1. Mobile navigation menu drawer open/close
 * 2. Flash message dismissal
 * 3. Simple UI toast notifications
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Menu Drawer Toggle
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const mobileDrawer = document.getElementById('mobileNavDrawer');
    const mobileOverlay = document.getElementById('mobileMenuOverlay');
    const mobileCloseBtn = document.getElementById('mobileNavClose');

    function openMobileMenu() {
        if (mobileDrawer) mobileDrawer.classList.add('active');
        if (mobileOverlay) mobileOverlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }

    function closeMobileMenu() {
        if (mobileDrawer) mobileDrawer.classList.remove('active');
        if (mobileOverlay) mobileOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', openMobileMenu);
    }

    if (mobileCloseBtn) {
        mobileCloseBtn.addEventListener('click', closeMobileMenu);
    }

    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', closeMobileMenu);
    }

    // 2. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Initialize cart badge count on page load
    if (typeof updateCartBadge === 'function') {
        updateCartBadge();
    }
});

/**
 * Shows a friendly toast notification in the bottom right corner
 * @param {string} message - Notification text
 * @param {string} type - 'success', 'warning', or 'danger'
 */
function showToast(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.position = 'fixed';
        container.style.bottom = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = '10px';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.margin = '0';
    toast.style.boxShadow = '0 10px 25px rgba(0,0,0,0.15)';
    toast.style.borderRadius = '12px';
    toast.style.padding = '12px 20px';
    toast.style.fontWeight = '600';
    toast.style.animation = 'slideDown 0.3s ease-out';
    toast.innerHTML = `<span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
