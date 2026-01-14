(function () {

    let cart = [];
    let allProducts = [];
    let currentPage = 1;
    const itemsPerPage = 12;
    let totalProducts = 0;
    let totalPages = 0;
    let currentSearch = '';
    let selectedBrands = new Set();
    let selectedCategories = new Set();
    let selectedDemographics = new Set();
    let isLoading = false;

    const elements = {
        template: document.getElementById('product-card-template'),
        search_input: document.getElementById('search-input'),
        brands_filter: document.getElementById('brands-filter'),
        categories_filter: document.getElementById('categories-filter'),
        demographics_filter: document.getElementById('demographics-filter'),
        clear_filters: document.getElementById('clear-filters'),
        products_container: document.getElementById('products-container'),
        pagination_container: document.getElementById('pagination-container'),
        product_form: document.getElementById(`product-form`),
        cart_container: document.getElementById('cart-container'),
        cart_empty: document.getElementById('cart-empty'),
        cart_items: document.getElementById('cart-items'),
        cart_footer: document.getElementById('cart-footer'),
        cart_total: document.getElementById('cart-total'),
        checkout_btn: document.getElementById('checkout-btn'),
        checkout_modal: document.getElementById('checkout-modal'),
        checkout_form: document.getElementById('checkout-form'),
        customer_name: document.getElementById('customer-name'),
        total_amount: document.getElementById('total-amount'),
        cash_received: document.getElementById('cash-received'),
        change_amount: document.getElementById('change-amount')
    };

    // Load brands
    fetch('/api/inventory/brands/suggestions')
        .then(res => res.json())
        .then(data => {
            if (data.brands) {
                populateFilter(data.brands, elements.brands_filter, 'brand', selectedBrands);
            }
        })
        .catch(err => console.error('Error loading brands:', err));

    // Load suggestions data (categories and demographics)
    fetch('/api/inventory/shoes/suggestions')
        .then(res => res.json())
        .then(data => {
            if (data.categories) {
                populateFilter(data.categories, elements.categories_filter, 'category', selectedCategories);
            }
            if (data.demographics) {
                populateFilter(data.demographics, elements.demographics_filter, 'demographic', selectedDemographics);
            }
        })
        .catch(err => console.error('Error loading filters:', err));

    // Load cart from localStorage
    loadCart();

    // Load products
    loadProducts();

    // Cart management functions
    function loadCart() {
        const savedCart = localStorage.getItem('pos_cart');
        if (savedCart) {
            cart = JSON.parse(savedCart);
        }
        displayCart();
    }

    function saveCart() {
        localStorage.setItem('pos_cart', JSON.stringify(cart));
    }

    function addToCart(productData) {
        // Find if item already exists in cart
        const existingItem = cart.find(item =>
            item.variant_id === productData.variant_id
        );

        if (existingItem) {
            existingItem.quantity = parseInt(existingItem.quantity) + parseInt(productData.quantity);
        } else {
            cart.push(productData);
        }

        saveCart();
        displayCart();
    }

    function removeFromCart(index) {
        cart.splice(index, 1);
        saveCart();
        displayCart();
    }

    function updateCartQuantity(index, newQuantity) {
        if (newQuantity <= 0) {
            removeFromCart(index);
            return;
        }
        cart[index].quantity = newQuantity;
        saveCart();
        displayCart();
    }

    function displayCart() {
        // Clear cart items container using replaceChildren()
        elements.cart_items.replaceChildren();

        if (cart.length === 0) {
            elements.cart_empty.style.display = 'block';
            elements.cart_items.style.display = 'none';
            elements.cart_footer.style.display = 'none';
            return;
        }

        elements.cart_empty.style.display = 'none';
        elements.cart_items.style.display = 'block';
        elements.cart_footer.style.display = 'block';

        let total = 0;

        cart.forEach((item, index) => {

            let product;
            let variant;
            for (let p of allProducts) {
                p.variants.forEach(v => {
                    if (v.variant_id === parseInt(item.variant_id)) {
                        product = p;
                        variant = v;
                    }
                });
                if (product) break;
            }

            if (!product) return;

            const markup_price = parseFloat(product.shoe_price) * (1 + (parseFloat(product.markup) / 100));
            const itemTotal = markup_price * parseInt(item.quantity);
            total += itemTotal;

            const cartItem = document.createElement('div');
            cartItem.className = 'd-flex flex-column mb-3 p-2 border rounded';

            const itemHeader = document.createElement('div');
            itemHeader.className = 'd-flex justify-content-between align-items-start';

            const itemInfo = document.createElement('div');
            itemInfo.className = 'flex-grow-1';

            const itemTitle = document.createElement('h6');
            itemTitle.className = 'mb-1';
            itemTitle.textContent = product.shoe_name;

            const itemBrand = document.createElement('small');
            itemBrand.className = 'text-muted';
            itemBrand.textContent = product.brand_name;

            const itemSize = document.createElement('small');
            itemSize.className = 'text-muted d-block';
            itemSize.textContent = `Size: ${variant.us_size} US / ${variant.uk_size} UK / ${variant.eu_size} EU`;

            itemInfo.appendChild(itemTitle);
            itemInfo.appendChild(itemBrand);
            itemInfo.appendChild(document.createElement('br'));
            itemInfo.appendChild(itemSize);

            const removeBtn = document.createElement('button');
            removeBtn.className = 'btn btn-sm btn-outline-danger';
            removeBtn.onclick = () => removeFromCart(index);

            const removeIcon = document.createElement('i');
            removeIcon.className = 'fa-solid fa-trash';
            removeBtn.appendChild(removeIcon);

            itemHeader.appendChild(itemInfo);
            itemHeader.appendChild(removeBtn);

            const itemFooter = document.createElement('div');
            itemFooter.className = 'd-flex justify-content-between align-items-center mt-2';

            const quantityControls = document.createElement('div');
            quantityControls.className = 'd-flex align-items-center';

            const decreaseBtn = document.createElement('button');
            decreaseBtn.className = 'btn btn-sm btn-outline-secondary';
            decreaseBtn.onclick = () => updateCartQuantity(index, parseInt(item.quantity) - 1);
            decreaseBtn.textContent = '-';

            const quantitySpan = document.createElement('span');
            quantitySpan.className = 'mx-2';
            quantitySpan.textContent = `Qty: ${item.quantity}`;

            const increaseBtn = document.createElement('button');
            increaseBtn.className = 'btn btn-sm btn-outline-secondary';
            increaseBtn.onclick = () => updateCartQuantity(index, parseInt(item.quantity) + 1);
            increaseBtn.textContent = '+';

            quantityControls.appendChild(decreaseBtn);
            quantityControls.appendChild(quantitySpan);
            quantityControls.appendChild(increaseBtn);

            const itemPrice = document.createElement('div');
            itemPrice.className = 'fw-bold';
            itemPrice.textContent = `₱${itemTotal.toFixed(2)}`;

            itemFooter.appendChild(quantityControls);
            itemFooter.appendChild(itemPrice);

            cartItem.appendChild(itemHeader);
            cartItem.appendChild(itemFooter);

            elements.cart_items.appendChild(cartItem);
        });

        elements.cart_total.textContent = `₱${total.toFixed(2)}`;
    }

    // Make functions global for onclick handlers
    window.removeFromCart = removeFromCart;
    window.updateCartQuantity = updateCartQuantity;

    function showLoadingSpinner() {
        if (isLoading) return;
        isLoading = true;

        // Clear containers using replaceChildren()
        elements.products_container.replaceChildren();
        elements.pagination_container.replaceChildren();

        // Create loading container in products area
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'col-12 text-center py-5';

        // Create spinner
        const spinnerDiv = document.createElement('div');
        spinnerDiv.className = 'spinner-border text-primary';
        spinnerDiv.setAttribute('role', 'status');

        const spinnerSpan = document.createElement('span');
        spinnerSpan.className = 'visually-hidden';
        spinnerSpan.textContent = 'Loading...';
        spinnerDiv.appendChild(spinnerSpan);

        // Create loading text
        const textDiv = document.createElement('div');
        textDiv.className = 'mt-2 text-muted';
        textDiv.textContent = 'Loading products...';

        // Assemble and append to products container
        loadingDiv.appendChild(spinnerDiv);
        loadingDiv.appendChild(textDiv);
        elements.products_container.appendChild(loadingDiv);
    }

    function hideLoadingSpinner() {
        isLoading = false;

        // Remove the loading spinner from document body
        const spinner = document.querySelector('.position-fixed.bottom-0');
        if (spinner) {
            spinner.remove();
        }
    }

    function loadProducts(page = 1) {

        showLoadingSpinner();

        // Build query parameters
        const params = new URLSearchParams({
            page: page,
            limit: itemsPerPage
        });

        if (currentSearch) {
            params.append('query', currentSearch);
        }

        if (selectedBrands.size > 0) {
            params.append('brand_ids', Array.from(selectedBrands).join(','));
        }

        if (selectedCategories.size > 0) {
            params.append('category_ids', Array.from(selectedCategories).join(','));
        }

        if (selectedDemographics.size > 0) {
            params.append('demographic_ids', Array.from(selectedDemographics).join(','));
        }

        fetch(`/api/inventory/shoes/all?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                hideLoadingSpinner();

                if (data.result) {
                    // Process variants - they are now included in the API response
                    window.scrollTo({
                        "top": 0
                    });

                    data.result.forEach(product => {
                        // Ensure variants is an array
                        if (!product.variants) {
                            product.variants = [];
                        }
                    });

                    allProducts = data.result;
                    totalProducts = data.count || 0;
                    totalPages = data.pages || 0;
                    currentPage = page;

                    displayProducts(allProducts);
                    displayCart(); // Update cart display with product details
                }
            })
            .catch(err => {
                hideLoadingSpinner();
                console.error('Error loading products:', err);

                // Clear containers using replaceChildren()
                elements.products_container.replaceChildren();
                elements.pagination_container.replaceChildren();

                // Create error container
                const errorDiv = document.createElement('div');
                errorDiv.className = 'col-12 text-center py-4 text-danger';

                const errorIcon = document.createElement('i');
                errorIcon.className = 'fa-solid fa-exclamation-triangle fa-2x mb-2';

                const errorText = document.createElement('div');
                errorText.textContent = 'Error loading products. Please try again.';

                errorDiv.appendChild(errorIcon);
                errorDiv.appendChild(errorText);
                elements.products_container.appendChild(errorDiv);
            });
    }

    function populateFilter(items, container, type, selectedSet) {
        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'form-check';

            const input = document.createElement('input');
            input.className = 'form-check-input';
            input.type = 'checkbox';
            input.id = `${type}-${item[`${type}_id`]}`;
            input.value = item[`${type}_id`];

            const label = document.createElement('label');
            label.className = 'form-check-label';
            label.htmlFor = input.id;
            label.textContent = item[`${type}_name`] || item[`${type}_Code`];

            input.addEventListener('change', () => {
                if (input.checked) {
                    selectedSet.add(parseInt(input.value));
                } else {
                    selectedSet.delete(parseInt(input.value));
                }
                filterProducts();
            });

            div.appendChild(input);
            div.appendChild(label);
            container.appendChild(div);
        });
    }

    function filterProducts() {
        // Reset to page 1 when filters change
        currentPage = 1;
        loadProducts(1);
    }

    function displayProducts(products) {
        // Clear containers using replaceChildren()
        elements.products_container.replaceChildren();
        elements.pagination_container.replaceChildren();

        if (products.length === 0) {
            // Create no products message
            const noProductsDiv = document.createElement('div');
            noProductsDiv.className = 'col-12 text-center py-4 text-muted';
            noProductsDiv.textContent = 'No products found';
            elements.products_container.appendChild(noProductsDiv);
            return;
        }

        // With server-side pagination, we display all products returned (which should be exactly itemsPerPage)
        products.forEach(product => {


            if (!product.variants) return;

            const markup_price = parseFloat(product.shoe_price) * (1 + (parseInt(product.markup) / 100));

            const cardElement = elements.template.content.cloneNode(true);

            const img = cardElement.querySelector('.card-img-top');
            img.src = `/shoe?shoe_id=${product.shoe_id}`;
            img.alt = product.shoe_name;
            img.onerror = function () {
                this.src = '/assets/public/products/default/default.jpeg';
            };

            const title = cardElement.querySelector('.card-title');
            title.textContent = product.shoe_name;

            const brand = cardElement.querySelector('.brand-text');
            brand.textContent = product.brand_name;

            // Categories
            const categoriesText = cardElement.querySelector('.categories-text');
            // Clear existing content
            categoriesText.replaceChildren();
            if (product.categories && product.categories.length > 0) {
                product.categories.forEach(cat => {
                    const badge = document.createElement('span');
                    badge.className = 'badge bg-primary me-1 mb-1';
                    badge.textContent = cat.category_name;
                    badge.style.cursor = 'pointer';
                    badge.title = 'Click to filter by this category';
                    badge.addEventListener('click', () => {
                        const checkbox = document.getElementById(`category-${cat.category_id}`);
                        if (checkbox) {
                            checkbox.checked = true;
                            selectedCategories.add(cat.category_id);
                            filterProducts();
                        }
                    });
                    categoriesText.appendChild(badge);
                });
            } else {
                categoriesText.textContent = 'None';
            }

            // Demographics
            const demographicsText = cardElement.querySelector('.demographics-text');
            // Clear existing content
            demographicsText.replaceChildren();
            if (product.demographics && product.demographics.length > 0) {
                product.demographics.forEach(demo => {
                    const badge = document.createElement('span');
                    badge.className = 'badge bg-success me-1 mb-1';
                    badge.textContent = demo.demographic_Code;
                    badge.style.cursor = 'pointer';
                    badge.title = 'Click to filter by this demographic';
                    badge.addEventListener('click', () => {
                        const checkbox = document.getElementById(`demographic-${demo.demographic_id}`);
                        if (checkbox) {
                            checkbox.checked = true;
                            selectedDemographics.add(demo.demographic_id);
                            filterProducts();
                        }
                    });
                    demographicsText.appendChild(badge);
                });
            } else {
                demographicsText.textContent = 'None';
            }

            // Variants
            const variantsText = cardElement.querySelector('.variants-text');
            if (product.variants && product.variants.length > 0) {

                for (let i = 0; i < 2; i++) {

                    const variant_elem = document.createElement("div");
                    variant_elem.className = "d-flex flex-row justify-content-between";
                    const size_elem = document.createElement("span");
                    const stock_elem = document.createElement("span");

                    if (i < product.variants.length) {
                        const variant = product.variants[i];
                        size_elem.textContent = `US:${variant.us_size} UK:${variant.uk_size} EU:${variant.eu_size}`;
                        stock_elem.textContent = `Stock:${variant.variant_stock}`;

                    } else {
                        size_elem.style.whiteSpace = "pre";
                        size_elem.textContent = ` `;

                        stock_elem.style.whiteSpace = "pre";
                        stock_elem.textContent = ` `;
                    }

                    variant_elem.appendChild(size_elem);
                    variant_elem.appendChild(stock_elem);

                    variantsText.appendChild(variant_elem);
                }

                const variant_elem = document.createElement("div");
                variant_elem.style.whiteSpace = "pre";
                variant_elem.style.fontSize = "10pt";
                variant_elem.textContent = product.variants.length > 2 ? `+${Math.abs(product.variants.length - 2)} more` : " ";
                variantsText.appendChild(variant_elem);



            } else {
                variantsText.textContent = 'Sizes: None';
            }

            const price = cardElement.querySelector('.price-text');
            price.textContent = `₱${parseFloat(markup_price).toFixed(2)}`;

            const button = cardElement.querySelector('.add-to-cart-btn');
            button.addEventListener('click', () => openModal(product));

            elements.products_container.appendChild(cardElement);
        });

        renderPagination(totalPages);
    }

    function openModal(product) {

        const markup_price = parseFloat(product.shoe_price) * (1 + (parseFloat(product.markup) / 100));


        const modal_elem = document.querySelector("#product-modal");

        modal_elem.querySelector("#shoe-image").src = `/shoe?shoe_id=${product.shoe_id}`;
        modal_elem.querySelector("#shoe-name").textContent = product.shoe_name;
        modal_elem.querySelector("#shoe-brand").textContent = product.brand_name;
        modal_elem.querySelector("#shoe-price").textContent = `P ${parseFloat(markup_price).toFixed(2)}`;
        modal_elem.querySelector("#total-price").textContent = `P ${parseFloat(markup_price).toFixed(2)}`;

        modal_elem.querySelector("input[name=quantity]").setAttribute("data-price", markup_price);


        const demographicContainer = document.querySelector("#modal-demographics-container");
        demographicContainer.replaceChildren();

        product.demographics.forEach(demo => {

            const demographic_elem = document.createElement("span");
            demographic_elem.className = "badge bg-success me-1 mb-1";
            demographic_elem.textContent = demo.demographic_Code;

            demographicContainer.appendChild(demographic_elem);

        });

        const categoryContainer = document.querySelector("#modal-categories-container");
        categoryContainer.replaceChildren();

        product.categories.forEach(category => {

            const category_elem = document.createElement("span");
            category_elem.className = "badge bg-primary me-1 mb-1";
            category_elem.textContent = category.category_name;

            categoryContainer.appendChild(category_elem);

        });

        const variants_container = document.querySelector("#modal-variant-container");
        variants_container.replaceChildren();

        const stock_display = document.getElementById("selected-variant-stock");

        let first = true;
        let first_variant_stock = 0;

        product.variants.forEach(variant => {

            const variant_container = document.createElement("div");
            variant_container.className = "variant-radio";

            const variant_label = document.createElement("label");
            variant_label.setAttribute("for", `variant-${variant.variant_id}`);
            variant_label.textContent = `US: ${variant.us_size} UK: ${variant.uk_size} EU: ${variant.eu_size}`;

            const variant_radio = document.createElement("input");
            variant_radio.setAttribute("id", `variant-${variant.variant_id}`);
            variant_radio.setAttribute("type", "radio");
            variant_radio.setAttribute("name", "variant_id");
            variant_radio.setAttribute("value", variant.variant_id);
            variant_radio.checked = first;

            if (first) {
                first_variant_stock = variant.variant_stock;
            }

            // Add event listener to update stock display
            variant_radio.addEventListener('change', () => {
                stock_display.textContent = `Stock: ${variant.variant_stock}`;
            });

            variant_container.appendChild(variant_radio);
            variant_container.appendChild(variant_label);
            variants_container.appendChild(variant_container);

            first = false;

        });

        // Set initial stock display
        if (product.variants.length > 0) {
            stock_display.textContent = `Stock: ${first_variant_stock}`;
        } else {
            stock_display.textContent = "No sizes available";
        }

        const modal = new bootstrap.Modal(modal_elem);
        modal.show();
    }

    elements.product_form.querySelector("input[name=quantity]").addEventListener("change", function (e) {

        const price = parseFloat(this.getAttribute("data-price"));
        const total_price = price * this.value

        const total_price_elem = document.getElementById('total-price');
        total_price_elem.textContent = `P ${total_price.toFixed(2)}`;

    });

    elements.product_form.addEventListener("submit", function (e) {
        e.preventDefault();

        const inputs = this.querySelectorAll("input");

        let data = {};

        inputs.forEach(input => {
            data[input.name] = input.value;
        })

        // Check stock availability
        const selectedVariant = this.querySelector('input[name="variant_id"]:checked');
        if (selectedVariant) {
            const variantId = selectedVariant.value;
            const product = allProducts.find(p => p.variants.some(v => v.variant_id == variantId));
            if (product) {
                const variant = product.variants.find(v => v.variant_id == variantId);
                if (variant && variant.variant_stock < data.quantity) {
                    alert(`Insufficient stock. Available: ${variant.variant_stock}`);
                    return;
                }
            }
        }

        addToCart(data);

        // Hide the modal
        const modalElem = document.getElementById('product-modal');
        const modal = bootstrap.Modal.getInstance(modalElem);
        if (modal) {
            modal.hide();
        } else {
            // Fallback: directly hide the modal
            modalElem.style.display = 'none';
            modalElem.classList.remove('show');
            document.body.classList.remove('modal-open');
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
        }

    })

    // Checkout functionality
    elements.checkout_btn.addEventListener('click', () => {
        if (cart.length === 0) {
            alert('Your cart is empty!');
            return;
        }

        // Calculate total
        let total = 0;
        cart.forEach((item, index) => {
            let product;
            let variant;
            for (let p of allProducts) {
                p.variants.forEach(v => {
                    if (v.variant_id === parseInt(item.variant_id)) {
                        product = p;
                        variant = v;
                    }
                });
                if (product) break;
            }

            if (product) {
                const markup_price = parseFloat(product.shoe_price) * (1 + (parseFloat(product.markup) / 100));
                total += markup_price * parseInt(item.quantity);
            }
        });

        elements.total_amount.value = `₱${total.toFixed(2)}`;
        elements.cash_received.value = '';
        elements.change_amount.value = '₱0.00';

        const checkoutModal = new bootstrap.Modal(elements.checkout_modal);
        checkoutModal.show();
    });

    elements.cash_received.addEventListener('input', (e) => {
        const cash = parseFloat(e.target.value) || 0;
        const totalText = elements.total_amount.value.replace('₱', '');
        const total = parseFloat(totalText) || 0;
        const change = cash - total;

        if (cash >= total) {
            elements.change_amount.value = `₱${change.toFixed(2)}`;
        } else {
            elements.change_amount.value = `₱${Math.abs(change).toFixed(2)} (Due)`;
        }
    });

    elements.checkout_form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const customerName = elements.customer_name.value.trim();
        const cashReceived = parseFloat(elements.cash_received.value) || 0;
        const totalText = elements.total_amount.value.replace('₱', '');
        const total = parseFloat(totalText) || 0;

        if (cashReceived < total) {
            alert('Cash received is less than total amount!');
            return;
        }

        // Prepare sale data
        const items = cart.map(item => `${item.variant_id}:${item.quantity}`).join(',');

        try {
            const response = await fetch('/api/sales/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    customer_name: customerName,
                    total_amount: total,
                    cash_received: cashReceived,
                    change_amount: cashReceived - total,
                    items: items
                })
            });

            const result = await response.json();

            if (result.success) {
                alert('Sale completed successfully!');
                cart = [];
                saveCart();
                displayCart(); // Refresh cart display
                // Close the checkout modal
                const checkoutModal = bootstrap.Modal.getInstance(elements.checkout_modal);
                if (checkoutModal) checkoutModal.hide();
            } else {
                alert('Error completing sale: ' + result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error completing sale. Please try again.');
        }
    });

    // Search input handler
    elements.search_input.addEventListener('input', (e) => {
        currentSearch = e.target.value.trim();
        filterProducts();
    });

    // Pagination functions
    function renderPagination(totalPages) {
        const paginationNav = elements.pagination_container.closest('nav');

        if (totalPages <= 1) {
            // Hide pagination when there's only one page or no pages
            if (paginationNav) {
                paginationNav.style.display = 'none';
            }
            return;
        }

        // Show pagination when there are multiple pages
        if (paginationNav) {
            paginationNav.style.display = 'block';
        }

        elements.pagination_container.innerHTML = '';

        const ul = elements.pagination_container;

        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        const prevLink = document.createElement('a');
        prevLink.className = 'page-link';
        prevLink.href = '#';
        prevLink.textContent = 'Previous';
        prevLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage > 1) {
                goToPage(currentPage - 1);
            }
        });
        prevLi.appendChild(prevLink);
        ul.appendChild(prevLi);

        // Page numbers
        const maxVisiblePages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        for (let i = startPage; i <= endPage; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${i === currentPage ? 'active' : ''}`;
            const link = document.createElement('a');
            link.className = 'page-link';
            link.href = '#';
            link.textContent = i;
            link.addEventListener('click', (e) => {
                e.preventDefault();
                goToPage(i);
            });
            li.appendChild(link);
            ul.appendChild(li);
        }

        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        const nextLink = document.createElement('a');
        nextLink.className = 'page-link';
        nextLink.href = '#';
        nextLink.textContent = 'Next';
        nextLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage < totalPages) {
                goToPage(currentPage + 1);
            }
        });
        nextLi.appendChild(nextLink);
        ul.appendChild(nextLi);
    }

    function goToPage(page) {
        loadProducts(page);
    }

    // Clear filters
    elements.clear_filters.addEventListener('click', () => {
        selectedBrands.clear();
        selectedCategories.clear();
        selectedDemographics.clear();
        currentSearch = '';
        elements.search_input.value = '';

        // Uncheck all checkboxes
        document.querySelectorAll('#brands-filter input[type="checkbox"]').forEach(cb => cb.checked = false);
        document.querySelectorAll('#categories-filter input[type="checkbox"]').forEach(cb => cb.checked = false);
        document.querySelectorAll('#demographics-filter input[type="checkbox"]').forEach(cb => cb.checked = false);

        // Reload products from server
        currentPage = 1;
        loadProducts(1);
    });

    window.addEventListener('DOMContentLoaded', () => {
        // Initial load is done above

        // Handle collapsible filter sections
        document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(button => {
            const targetId = button.getAttribute('data-bs-target');
            const target = document.querySelector(targetId);
            const icon = button.querySelector('.toggle-icon');

            if (target && icon) {
                target.addEventListener('show.bs.collapse', () => {
                    icon.classList.remove('collapsed');
                });

                target.addEventListener('hide.bs.collapse', () => {
                    icon.classList.add('collapsed');
                });
            }
        });
    });
})();
