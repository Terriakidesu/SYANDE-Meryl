(function () {

    let cart = [];

    const elements = {
        template: document.getElementById('product-card-template'),
        search_input: document.getElementById('search-input'),
        brands_filter: document.getElementById('brands-filter'),
        categories_filter: document.getElementById('categories-filter'),
        demographics_filter: document.getElementById('demographics-filter'),
        clear_filters: document.getElementById('clear-filters'),
        products_container: document.getElementById('products-container'),
        product_form: document.getElementById(`product-form`)
    };

    let allProducts = [];
    let selectedBrands = new Set();
    let selectedCategories = new Set();
    let selectedDemographics = new Set();
    let currentSearch = '';

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

    // Load products
    loadProducts();

    function loadProducts() {
        fetch('/api/inventory/variants/?limit=100')
            .then(res => res.json())
            .then(data => {
                if (data.result) {
                    // Add categories and demographics to each product
                    Promise.all(data.result.map(product =>
                        fetch(`/api/inventory/shoes/${product.shoe_id}/all`)
                            .then(res => res.json())
                            .then(details => {
                                product.categories = details.categories || [];
                                product.demographics = details.demographics || [];
                                return product;
                            })
                            .catch(err => {
                                console.error('Error loading product details:', err);
                                product.categories = [];
                                product.demographics = [];
                                return product;
                            })
                    )).then(products => {
                        allProducts = products;
                        displayProducts(allProducts);
                    });
                }
            })
            .catch(err => console.error('Error loading products:', err));
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
        let filtered = allProducts;

        // Filter by search
        if (currentSearch) {
            filtered = filtered.filter(product =>
                product.shoe_name.toLowerCase().includes(currentSearch.toLowerCase()) ||
                product.brand_name.toLowerCase().includes(currentSearch.toLowerCase())
            );
        }

        // Filter by brands
        if (selectedBrands.size > 0) {
            filtered = filtered.filter(product => selectedBrands.has(product.brand_id));
        }

        // Filter by categories (AND logic - product must have ALL selected categories)
        if (selectedCategories.size > 0) {
            filtered = filtered.filter(product =>
                product.categories &&
                selectedCategories.size === product.categories.filter(cat => selectedCategories.has(cat.category_id)).length
            );
        }

        // Filter by demographics (AND logic - product must have ALL selected demographics)
        if (selectedDemographics.size > 0) {
            filtered = filtered.filter(product =>
                product.demographics &&
                [...selectedDemographics].every(selectedId =>
                    product.demographics.some(productDemo => productDemo.demographic_id === selectedId)
                )
            );
        }

        displayProducts(filtered);
    }

    function displayProducts(products) {
        elements.products_container.innerHTML = '';

        if (products.length === 0) {
            elements.products_container.innerHTML = '<div class="col-12 text-center py-4 text-muted">No products found</div>';
            return;
        }

        products.forEach(product => {
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
            categoriesText.innerHTML = '';
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
            demographicsText.innerHTML = '';
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
            price.textContent = `₱${parseFloat(product.shoe_price).toFixed(2)}`;

            const button = cardElement.querySelector('.add-to-cart-btn');
            button.addEventListener('click', () => openModal(product));

            elements.products_container.appendChild(cardElement);
        });
    }

    function openModal(product) {
        const modal_elem = document.querySelector("#product-modal");

        modal_elem.querySelector("#shoe-name").textContent = product.shoe_name;
        modal_elem.querySelector("#shoe-brand").textContent = product.brand_name;
        modal_elem.querySelector("#shoe-price").textContent = `P ${parseFloat(product.shoe_price).toFixed(2)}`;
        modal_elem.querySelector("#total-price").textContent = `P ${parseFloat(product.shoe_price).toFixed(2)}`;

        modal_elem.querySelector("input[name=quantity]").setAttribute("data-price", product.shoe_price);


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

        let first = true;

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

            variant_container.appendChild(variant_radio);
            variant_container.appendChild(variant_label);
            variants_container.appendChild(variant_container);

            first = false;

        });

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

        cart.push(data);

        const modal_elem = document.querySelector("#product-modal");
        const modal = new bootstrap.Modal(modal_elem);
        modal.hide();

    })

    // Search input handler
    elements.search_input.addEventListener('input', (e) => {
        currentSearch = e.target.value.trim();
        filterProducts();
    });

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

        displayProducts(allProducts);
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
