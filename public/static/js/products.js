/**
 * Brownies Hub / Sweet Crumbs Bakery - Products Page Logic
 * --------------------------------------------------------
 * Handles:
 * 1. Live search filter
 * 2. Category button filtering
 * 3. Add to Cart button triggers
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('productSearchInput');
    const categoryChips = document.querySelectorAll('.chip-btn');
    const productCards = document.querySelectorAll('.product-item-card');
    const noResultsMsg = document.getElementById('noProductsMessage');
    const productsGrid = document.getElementById('productsGrid');

    let currentCategory = 'all';
    let currentSearch = '';

    // Check URL parameters for category or search
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('category')) {
        currentCategory = urlParams.get('category').toLowerCase();
        categoryChips.forEach(chip => {
            if (chip.dataset.category === currentCategory) {
                chip.classList.add('active');
            } else {
                chip.classList.remove('active');
            }
        });
    }

    if (urlParams.has('search')) {
        currentSearch = urlParams.get('search').trim().toLowerCase();
        if (searchInput) searchInput.value = currentSearch;
    }

    /**
     * Filters DOM product cards based on active category & search keyword
     */
    function filterProducts() {
        let visibleCount = 0;
        
        productCards.forEach(card => {
            const cardCategory = (card.dataset.category || '').toLowerCase();
            const cardName = (card.dataset.name || '').toLowerCase();
            const cardDesc = (card.dataset.description || '').toLowerCase();

            const matchesCategory = (currentCategory === 'all' || cardCategory === currentCategory);
            const matchesSearch = (!currentSearch || cardName.includes(currentSearch) || cardDesc.includes(currentSearch));

            if (matchesCategory && matchesSearch) {
                card.style.display = 'flex';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        if (noResultsMsg) {
            noResultsMsg.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    // 1. Search Box input listener (Live Instant Filtering)
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearch = e.target.value.trim().toLowerCase();
            filterProducts();
        });
    }

    // 2. Category chip buttons listener
    categoryChips.forEach(chip => {
        chip.addEventListener('click', () => {
            categoryChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            currentCategory = chip.dataset.category.toLowerCase();
            filterProducts();
        });
    });

    // Run initial filter
    filterProducts();
});

/**
 * Global helper to add product to cart from a product card button
 */
function handleAddToCart(btn) {
    const id = parseInt(btn.dataset.id, 10);
    const name = btn.dataset.name;
    const price = parseFloat(btn.dataset.price);
    const image = btn.dataset.image;

    addToCart({ id, name, price, image }, 1);
}
