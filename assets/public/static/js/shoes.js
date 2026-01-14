(function () {
    const shoeModal = new bootstrap.Modal(document.getElementById("shoe-modal"));
    const deleteModal = new bootstrap.Modal(document.getElementById("delete-modal"));
    const elements = {
        template: document.getElementById("shoe-item-template"),
        shoe_list: document.getElementById("shoe-list"),
        search_form: document.getElementById("search-form"),
        page_input: document.getElementById("page-input"),
        pagination: document.getElementById("pagination"),
        add_shoe_btn: document.getElementById("add-shoe-btn"),
        shoe_form: document.getElementById("shoe-form"),
        shoe_id: document.getElementById("shoe-id"),
        shoe_name: document.getElementById("shoe-name"),
        brand_input: document.getElementById("brand-input"),
        brand_id: document.getElementById("brand-id"),
        brand_suggestions: document.getElementById("brand-suggestions"),
        category_input: document.getElementById("category-input"),
        category_ids: document.getElementById("category-ids"),
        category_suggestions: document.getElementById("category-suggestions"),
        category_selected: document.getElementById("category-selected"),
        demographic_input: document.getElementById("demographic-input"),
        demographic_ids: document.getElementById("demographic-ids"),
        demographic_suggestions: document.getElementById("demographic-suggestions"),
        demographic_selected: document.getElementById("demographic-selected"),
        shoe_price: document.getElementById("shoe-price"),
        markup: document.getElementById("markup"),
        first_sale_at: document.getElementById("first-sale-at"),
        shoe_file: document.getElementById("shoe-file"),
        shoe_modal_title: document.getElementById("shoe-modal-title"),
        save_shoe_btn: document.getElementById("save-shoe-btn"),
        delete_shoe_id: document.getElementById("delete-shoe-id"),
        confirm_delete_btn: document.getElementById("confirm-delete-btn"),
        current_image_container: document.getElementById("current-image-container"),
        current_shoe_image: document.getElementById("current-shoe-image"),
        image_preview_container: document.getElementById("image-preview-container"),
        image_preview: document.getElementById("image-preview"),
        remove_image_btn: document.getElementById("remove-image-btn")
    };

    // Store for managing selected categories and demographics
    let selectedCategories = {}; // { categoryId: categoryName }
    let selectedDemographics = {}; // { demographicId: demographicName }
    let selectedBrand = null; // { brandId: brandName }
    let allBrands = [];
    let allCategories = [];
    let allDemographics = [];

    // Load suggestions data
    fetch('/api/inventory/shoes/suggestions')
        .then(res => res.json())
        .then(data => {
            if (data.categories) {
                allCategories = data.categories;
            }
            if (data.demographics) {
                allDemographics = data.demographics;
            }
        })
        .catch(err => console.error(err));

    // Load brands
    fetch('/api/inventory/brands/suggestions')
        .then(res => res.json())
        .then(data => {
            if (data.brands) {
                allBrands = data.brands;
            }
        })
        .catch(err => console.error(err));

    elements.search_form.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(elements.search_form);
        elements.page_input.value = 1;
        searchShoes(formData);
    });

    // Prevent search form submission when modal is open
    elements.shoe_form.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
        }
    });

    elements.search_form.querySelector('input[type="search"]').addEventListener("input", function (e) {
        if (e.target.value === "") {
            elements.page_input.value = 1;
            const formData = new FormData(elements.search_form);
            searchShoes(formData);
        }
    });

    elements.search_form.querySelector('input[type="search"]').addEventListener("change", function (e) {
        elements.page_input.value = 1;
        const formData = new FormData(elements.search_form);
        searchShoes(formData);
    });

    elements.add_shoe_btn.addEventListener("click", function () {
        elements.shoe_form.reset();
        elements.shoe_id.value = "";
        elements.brand_id.value = "";
        elements.brand_input.value = "";
        selectedBrand = null;
        selectedCategories = {};
        selectedDemographics = {};
        renderSelectedCategories();
        renderSelectedDemographics();
        elements.current_image_container.style.display = 'none';
        elements.current_shoe_image.src = '';
        clearImagePreview();
        elements.shoe_modal_title.textContent = "Add Shoe";
        shoeModal.show();
    });

    // Brand suggestions
    elements.brand_input.addEventListener("input", function () {
        const query = this.value.trim().toLowerCase();

        const filtered = allBrands.filter(brand =>
            brand.brand_name.toLowerCase().includes(query)
        );

        if (filtered.length === 0) {
            elements.brand_suggestions.style.display = 'none';
            return;
        }

        elements.brand_suggestions.innerHTML = '';
        filtered.forEach((brand, index) => {
            const item = document.createElement('button');
            item.type = 'button';
            item.className = 'list-group-item list-group-item-action';
            if (index === 0) item.classList.add('active');
            item.textContent = brand.brand_name;
            item.dataset.brandId = brand.brand_id;
            item.dataset.brandName = brand.brand_name;
            item.addEventListener('click', function (e) {
                e.preventDefault();
                selectedBrand = { id: brand.brand_id, name: brand.brand_name };
                elements.brand_id.value = brand.brand_id;
                elements.brand_input.value = brand.brand_name;
                elements.brand_suggestions.style.display = 'none';
            });
            elements.brand_suggestions.appendChild(item);
        });

        elements.brand_suggestions.style.display = 'block';
    });

    elements.brand_input.addEventListener("keydown", function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (elements.brand_suggestions.style.display !== 'none') {
                const firstItem = elements.brand_suggestions.querySelector('.list-group-item');
                if (firstItem) {
                    const brandId = firstItem.dataset.brandId;
                    const brandName = firstItem.dataset.brandName;
                    if (brandId && brandName) {
                        selectedBrand = { id: brandId, name: brandName };
                        elements.brand_id.value = brandId;
                        elements.brand_input.value = brand.brand_name;
                        elements.brand_suggestions.style.display = 'none';
                    }
                }
            }
        }
    });

    // Category suggestions
    elements.category_input.addEventListener("input", function () {
        const query = this.value.trim().toLowerCase();

        const filtered = allCategories.filter(cat =>
            !selectedCategories[cat.category_id] &&
            (query === '' || cat.category_name.toLowerCase().includes(query))
        );

        if (filtered.length === 0) {
            elements.category_suggestions.style.display = 'none';
            return;
        }

        elements.category_suggestions.innerHTML = '';
        filtered.forEach((cat, index) => {
            const item = document.createElement('button');
            item.type = 'button';
            item.className = 'list-group-item list-group-item-action';
            if (index === 0) item.classList.add('active');
            item.textContent = cat.category_name;
            item.dataset.categoryId = cat.category_id;
            item.dataset.categoryName = cat.category_name;
            item.addEventListener('click', function (e) {
                e.preventDefault();
                selectedCategories[cat.category_id] = cat.category_name;
                renderSelectedCategories();
                elements.category_input.value = '';
                elements.category_suggestions.style.display = 'none';
            });
            elements.category_suggestions.appendChild(item);
        });

        elements.category_suggestions.style.display = 'block';
    });

    elements.category_input.addEventListener("keydown", function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (elements.category_suggestions.style.display !== 'none') {
                const firstItem = elements.category_suggestions.querySelector('.list-group-item');
                if (firstItem) {
                    const categoryId = firstItem.dataset.categoryId;
                    const categoryName = firstItem.dataset.categoryName;
                    if (categoryId && categoryName) {
                        selectedCategories[categoryId] = categoryName;
                        renderSelectedCategories();
                        elements.category_input.value = '';
                        elements.category_suggestions.style.display = 'none';
                    }
                }
            }
        }
    });

    // Demographic suggestions
    elements.demographic_input.addEventListener("input", function () {
        const query = this.value.trim().toLowerCase();

        if (!allDemographics || allDemographics.length === 0) {
            elements.demographic_suggestions.style.display = 'none';
            return;
        }

        const filtered = allDemographics.filter(demo => {
            const demoName = demo.demographic_Code || '';
            return !selectedDemographics[demo.demographic_id] &&
                (query === '' || demoName.toLowerCase().includes(query));
        });

        if (filtered.length === 0) {
            elements.demographic_suggestions.style.display = 'none';
            return;
        }

        elements.demographic_suggestions.innerHTML = '';
        filtered.forEach((demo, index) => {
            const item = document.createElement('button');
            item.type = 'button';
            item.className = 'list-group-item list-group-item-action';
            if (index === 0) item.classList.add('active');
            item.textContent = demo.demographic_Code || '';
            item.dataset.demographicId = demo.demographic_id;
            item.dataset.demographicName = demo.demographic_Code || '';
            item.addEventListener('click', function (e) {
                e.preventDefault();
                selectedDemographics[demo.demographic_id] = demo.demographic_Code;
                renderSelectedDemographics();
                elements.demographic_input.value = '';
                elements.demographic_suggestions.style.display = 'none';
            });
            elements.demographic_suggestions.appendChild(item);
        });

        elements.demographic_suggestions.style.display = 'block';
    });

    elements.demographic_input.addEventListener("keydown", function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (elements.demographic_suggestions.style.display !== 'none') {
                const firstItem = elements.demographic_suggestions.querySelector('.list-group-item');
                if (firstItem) {
                    const demographicId = firstItem.dataset.demographicId;
                    const demographicName = firstItem.dataset.demographicName;
                    if (demographicId && demographicName) {
                        selectedDemographics[demographicId] = demographicName;
                        renderSelectedDemographics();
                        elements.demographic_input.value = '';
                        elements.demographic_suggestions.style.display = 'none';
                    }
                }
            }
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function (e) {
        if (e.target !== elements.brand_input) {
            elements.brand_suggestions.style.display = 'none';
        }
        if (e.target !== elements.category_input) {
            elements.category_suggestions.style.display = 'none';
        }
        if (e.target !== elements.demographic_input) {
            elements.demographic_suggestions.style.display = 'none';
        }
    });

    // Image preview functionality
    elements.shoe_file.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                elements.image_preview.src = e.target.result;
                elements.image_preview_container.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else {
            clearImagePreview();
        }
    });

    elements.remove_image_btn.addEventListener('click', function () {
        clearImagePreview();
        elements.shoe_file.value = '';
    });

    function clearImagePreview() {
        elements.image_preview.src = '';
        elements.image_preview_container.style.display = 'none';
    }

    elements.shoe_list.addEventListener("click", function (e) {
        const editBtn = e.target.closest(".edit-btn");
        if (editBtn) {
            const card = editBtn.closest(".shoe-item");
            const shoeId = card.dataset.shoeId;
            openEditModal(shoeId);
        }
    });

    elements.shoe_list.addEventListener("click", function (e) {
        const deleteBtn = e.target.closest(".delete-btn");
        if (deleteBtn) {
            const card = deleteBtn.closest(".shoe-item");
            const shoeId = card.dataset.shoeId;
            openDeleteModal(shoeId);
        }
    });

    function openDeleteModal(shoeId) {
        elements.delete_shoe_id.value = shoeId;
        deleteModal.show();
    }

    function renderSelectedCategories() {
        elements.category_selected.innerHTML = '';
        elements.category_ids.value = Object.keys(selectedCategories).join(',');

        Object.entries(selectedCategories).forEach(([catId, catName]) => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-primary d-flex align-items-center gap-2';
            badge.innerHTML = `${catName} <button type="button" class="btn-close btn-close-white" style="font-size: 0.7rem;"></button>`;
            badge.querySelector('.btn-close').addEventListener('click', () => {
                delete selectedCategories[catId];
                renderSelectedCategories();
            });
            elements.category_selected.appendChild(badge);
        });
    }

    function renderSelectedDemographics() {
        elements.demographic_selected.innerHTML = '';
        elements.demographic_ids.value = Object.keys(selectedDemographics).join(',');

        Object.entries(selectedDemographics).forEach(([demoId, demoName]) => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-success d-flex align-items-center gap-2';
            badge.innerHTML = `${demoName} <button type="button" class="btn-close btn-close-white" style="font-size: 0.7rem;"></button>`;
            badge.querySelector('.btn-close').addEventListener('click', () => {
                delete selectedDemographics[demoId];
                renderSelectedDemographics();
            });
            elements.demographic_selected.appendChild(badge);
        });
    }

    elements.confirm_delete_btn.addEventListener("click", function () {
        const shoeId = elements.delete_shoe_id.value;

        fetch(`/api/inventory/shoes/delete/${shoeId}`, {
            method: "DELETE",
        })
            .then(res => res.json())
            .then(data => {
                deleteModal.hide();
                refreshCurrentPage();
                if (data.success) {
                    showSuccessToast(data.message || "Shoe deleted successfully");
                } else {
                    throw new Error(data.message);
                }
            })
            .catch(err => {
                if (typeof showErrorToast === "function") {
                    showErrorToast(err);
                } else {
                    console.error(err);
                }
            });
    });

    function openEditModal(shoeId) {
        fetch(`/api/inventory/shoes/${shoeId}/all`)
            .then(res => res.json())
            .then(data => {
                elements.shoe_id.value = data.shoe_id;
                elements.shoe_name.value = data.shoe_name;
                elements.brand_id.value = data.brand_id;

                // Set brand name in input
                const brand = allBrands.find(b => b.brand_id == data.brand_id);
                if (brand) {
                    elements.brand_input.value = brand.brand_name;
                    selectedBrand = { id: brand.brand_id, name: brand.brand_name };
                }


                elements.shoe_price.value = data.shoe_price;
                elements.markup.value = data.markup;
                elements.first_sale_at.value = data.first_sale_at;

                // Populate selected categories
                selectedCategories = {};
                if (data.categories && Array.isArray(data.categories)) {
                    data.categories.forEach(cat => {
                        selectedCategories[cat.category_id] = cat.category_name;
                    });
                }
                renderSelectedCategories();

                // Populate selected demographics
                selectedDemographics = {};
                if (data.demographics && Array.isArray(data.demographics)) {
                    data.demographics.forEach(demo => {
                        selectedDemographics[demo.demographic_id] = demo.demographic_Code;
                    });
                }
                renderSelectedDemographics();

                // Show current image
                elements.current_shoe_image.src = `/shoe?shoe_id=${shoeId}`;
                elements.current_image_container.style.display = 'block';

                elements.shoe_modal_title.textContent = "Edit Shoe";
                shoeModal.show();
            })
            .catch(err => {
                if (typeof showErrorToast === "function") {
                    showErrorToast(err);
                } else {
                    console.error(err);
                }
            });
    }

    elements.save_shoe_btn.addEventListener("click", function () {
        if (!elements.shoe_form.checkValidity()) {
            elements.shoe_form.reportValidity();
            return;
        }

        const formData = new FormData();
        formData.append("shoe_name", elements.shoe_name.value);
        formData.append("brand_id", elements.brand_id.value);
        formData.append("category_ids", elements.category_ids.value);
        formData.append("demographic_ids", elements.demographic_ids.value);
        formData.append("shoe_price", elements.shoe_price.value);
        formData.append("markup", elements.markup.value);
        formData.append("first_sale_at", elements.first_sale_at.value);

        if (elements.shoe_file.files.length > 0) {
            formData.append("file", elements.shoe_file.files[0]);
        }

        const isEdit = !!elements.shoe_id.value;
        const url = isEdit ? "/api/inventory/shoes/update" : "/api/inventory/shoes/add";
        if (isEdit) {
            formData.append("shoe_id", elements.shoe_id.value);
        }

        fetch(url, {
            method: "POST",
            body: formData
        })
            .then(res => res.json())
            .then(data => {
            if (data.success) {
                shoeModal.hide();
                refreshCurrentPage();
                if (typeof showSuccessToast === "function") {
                    showSuccessToast(data.message || "Shoe saved successfully");
                }
            } else {
                throw new Error(data.message || "Failed to save shoe");
            }
        })
            .catch(err => {
                if (typeof showErrorToast === "function") {
                    showErrorToast(err);
                } else {
                    console.error(err);
                }
            });
    });

    function searchShoes(formData) {
        const url = new URL(elements.search_form.action, window.location.origin);
        url.search = new URLSearchParams(formData).toString();

        fetch(url, {
            method: "GET",
            headers: { "Accept": "application/json" }
        })
            .then(res => res.json())
            .then(response => {
                try {
                    const { result: items, count, pages } = response;
                    elements.shoe_list.replaceChildren();

                    if (count === 0) {
                        elements.shoe_list.innerHTML = '<div class="text-center py-4 text-muted">No items found</div>';
                    } else {
                        items.forEach(addItemToList);
                    }

                    renderPagination(pages);
                } catch (err) {
                    throw new Error(err);
                }
            })
            .catch(err => {
                if (typeof showErrorToast === "function") {
                    showErrorToast(err);
                } else {
                    console.error(err);
                }
            });
    }

    function addItemToList(item) {
        const elem = elements.template.content.cloneNode(true);
        const card = elem.querySelector(".shoe-item");
        const imageEl = elem.querySelector(".shoe-image img");
        const idEl = elem.querySelector(".shoe-id");
        const nameEl = elem.querySelector(".shoe-name");
        const priceEl = elem.querySelector(".shoe-price");
        const markupEl = elem.querySelector(".shoe-markup");
        const markupPriceEl = elem.querySelector(".shoe-markup-price");
        const brandsEl = elem.querySelector(".shoe-brand");
        const categoriesEl = elem.querySelector(".shoe-categories");
        const demographicsEl = elem.querySelector(".shoe-demographics");
        const detailsEl = elem.querySelector(".shoe-details");
        const categoriesListEl = elem.querySelector(".categories-list");
        const demographicsListEl = elem.querySelector(".demographics-list");

        card.dataset.shoeId = item.shoe_id;
        imageEl.src = `/shoe?shoe_id=${item.shoe_id}`;
        idEl.textContent = `ID: ${item.shoe_id}`;
        nameEl.textContent = item.shoe_name;
        priceEl.textContent = `₱${parseFloat(item.shoe_price).toFixed(2)}`;
        markupEl.textContent = `${item.markup}%`;
        markupPriceEl.textContent = `₱${(parseFloat(item.shoe_price) * (1 + parseFloat(item.markup) / 100)).toFixed(2)}`;

        // Get brand, categories and demographics
        const brand = item.brand_name || "-";
        const categories = item.categories || [];
        const demographics = item.demographics || [];

        // Display brand
        brandsEl.textContent = brand;

        // Display first 2 categories with +n more
        if (categories.length > 0) {
            const displayCats = categories.slice(0, 2).map(c => c.category_name);
            if (categories.length > 2) {
                displayCats.push(`+${categories.length - 2} more`);
            }
            categoriesEl.textContent = displayCats.join(", ");
        }

        // Display first 2 demographics with +n more
        if (demographics.length > 0) {
            const displayDemos = demographics.slice(0, 2).map(d => d.demographic_Code);
            if (demographics.length > 2) {
                displayDemos.push(`+${demographics.length - 2} more`);
            }
            demographicsEl.textContent = displayDemos.join(", ");
        }

        // Populate details section
        categories.forEach(cat => {
            const badge = document.createElement("span");
            badge.className = "badge bg-primary me-1 mb-1";
            badge.textContent = cat.category_name;
            categoriesListEl.appendChild(badge);
        });

        demographics.forEach(demo => {
            const badge = document.createElement("span");
            badge.className = "badge bg-success me-1 mb-1";
            badge.textContent = demo.demographic_Code;
            demographicsListEl.appendChild(badge);
        });

        // Click to expand/collapse
        card.addEventListener("click", function (e) {
            // Don't expand if clicking buttons
            if (e.target.closest(".edit-btn") || e.target.closest(".delete-btn")) {
                return;
            }
            const isVisible = detailsEl.style.display !== "none";
            detailsEl.style.display = isVisible ? "none" : "block";

            // Toggle chevron rotation
            const chevron = card.querySelector(".shoe-chevron");
            if (chevron) {
                if (isVisible) {
                    chevron.style.transform = "rotate(0deg)";
                } else {
                    chevron.style.transform = "rotate(180deg)";
                }
            }
        });

        elements.shoe_list.appendChild(elem);
    }

    function renderPagination(totalPages) {
        elements.pagination.innerHTML = "";
        const currentPage = parseInt(elements.page_input.value) || 1;

        if (totalPages <= 1) return;

        // Previous button
        const prevLi = document.createElement("li");
        prevLi.className = "page-item";
        if (currentPage === 1) prevLi.classList.add("disabled");
        const prevA = document.createElement("a");
        prevA.className = "page-link";
        prevA.href = "#";
        prevA.textContent = "Prev";
        prevA.addEventListener("click", (e) => { e.preventDefault(); goToPage(currentPage - 1); });
        prevLi.appendChild(prevA);
        elements.pagination.appendChild(prevLi);

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            const pageLi = document.createElement("li");
            pageLi.className = "page-item";
            if (i === currentPage) pageLi.classList.add("active");
            const pageA = document.createElement("a");
            pageA.className = "page-link";
            pageA.href = "#";
            pageA.textContent = i;
            pageA.addEventListener("click", (e) => { e.preventDefault(); goToPage(i); });
            pageLi.appendChild(pageA);
            elements.pagination.appendChild(pageLi);
        }

        // Next button
        const nextLi = document.createElement("li");
        nextLi.className = "page-item";
        if (currentPage === totalPages) nextLi.classList.add("disabled");
        const nextA = document.createElement("a");
        nextA.className = "page-link";
        nextA.href = "#";
        nextA.textContent = "Next";
        nextA.addEventListener("click", (e) => { e.preventDefault(); goToPage(currentPage + 1); });
        nextLi.appendChild(nextA);
        elements.pagination.appendChild(nextLi);
    }

    function goToPage(page) {
        elements.page_input.value = page;
        const formData = new FormData(elements.search_form);
        searchShoes(formData);
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function refreshCurrentPage() {
        const formData = new FormData(elements.search_form);
        searchShoes(formData);
    }

    window.addEventListener("DOMContentLoaded", () => {
        searchShoes();
    });
})();
