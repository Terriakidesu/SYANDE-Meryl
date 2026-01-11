(function () {
    const variantModal = new bootstrap.Modal(document.getElementById("variant-modal"));
    const deleteModal = new bootstrap.Modal(document.getElementById("delete-modal"));
    const elements = {
        shoe_container_template: document.getElementById("shoe-container-template"),
        template: document.getElementById("variant-item-template"),
        shoe_list: document.getElementById("shoe-list"),
        search_form: document.getElementById("search-form"),
        page_input: document.getElementById("page-input"),
        pagination: document.getElementById("pagination"),
        add_variant_btn: document.getElementById("add-variant-btn"),
        variant_form: document.getElementById("variant-form"),
        variant_id: document.getElementById("variant-id"),
        variant_shoe: document.getElementById("variant-shoe"),
        variant_size: document.getElementById("variant-size"),
        variant_stock: document.getElementById("variant-stock"),
        variant_modal_title: document.getElementById("variant-modal-title"),
        save_variant_btn: document.getElementById("save-variant-btn"),
        delete_variant_id: document.getElementById("delete-variant-id"),
        confirm_delete_btn: document.getElementById("confirm-delete-btn")
    };

    // Prevent search form submission when modal is open
    elements.variant_form.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
        }
    });

    // Load shoes
    fetch('/api/inventory/shoes/all?limit=100')
        .then(res => res.json())
        .then(data => {
            if (data.result) {
                data.result.forEach(shoe => {
                    const option = document.createElement('option');
                    option.value = shoe.shoe_id;
                    option.textContent = shoe.shoe_name;
                    elements.variant_shoe.appendChild(option);
                });
            }
        })
        .catch(err => console.error(err));

    // Load sizes
    fetch('/api/inventory/sizes/?limit=100')
        .then(res => res.json())
        .then(data => {
            if (data.result) {
                data.result.forEach(size => {
                    const option = document.createElement('option');
                    option.value = size.size_id;
                    option.textContent = `US: ${size.us_size} | UK: ${size.uk_size} | EU: ${size.eu_size}`;
                    elements.variant_size.appendChild(option);
                });
            }
        })
        .catch(err => console.error(err));

    elements.search_form.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(elements.search_form);
        elements.page_input.value = 1;
        searchVariants(formData);
    });

    elements.search_form.querySelector('input[type="search"]').addEventListener("input", function (e) {
        if (e.target.value === "") {
            elements.page_input.value = 1;
            const formData = new FormData(elements.search_form);
            searchVariants(formData);
        }
    });

    elements.search_form.querySelector('input[type="search"]').addEventListener("change", function (e) {
        elements.page_input.value = 1;
        const formData = new FormData(elements.search_form);
        searchVariants(formData);
    });

    elements.add_variant_btn.addEventListener("click", function () {
        elements.variant_form.reset();
        elements.variant_id.value = "";
        elements.variant_modal_title.textContent = "Add Variant";
        showAllSizes();
        variantModal.show();
    });

    elements.shoe_list.addEventListener("click", function (e) {
        const editBtn = e.target.closest(".edit-btn");
        if (editBtn) {
            const card = editBtn.closest(".variant-item");
            const variantId = card.dataset.variantId;
            openEditModal(variantId);
        }
    });

    elements.shoe_list.addEventListener("click", function (e) {
        const deleteBtn = e.target.closest(".delete-btn");
        if (deleteBtn) {
            const card = deleteBtn.closest(".variant-item");
            const variantId = card.dataset.variantId;
            openDeleteModal(variantId);
        }
    });

    elements.shoe_list.addEventListener("click", function (e) {
        
        if (addVariantBtn) {
            
            elements.variant_form.reset();
            elements.variant_id.value = "";
            elements.variant_shoe.value = shoeId;
            elements.variant_modal_title.textContent = "Add Variant";
            // Hide already used sizes for this shoe
            fetch(`/api/inventory/variants/?shoe_id=${shoeId}`)
                .then(res => res.json())
                .then(data => {
                    const usedSizes = new Set(data.result.map(v => v.size_id));
                    const sizeOptions = elements.variant_size.querySelectorAll('option');
                    sizeOptions.forEach(option => {
                        if (option.value && usedSizes.has(parseInt(option.value))) {
                            option.style.display = 'none';
                        } else {
                            option.style.display = '';
                        }
                    });
                    variantModal.show();
                })
                .catch(err => {
                    console.error(err);
                    variantModal.show();
                });
        }
    });

    function openDeleteModal(variantId) {
        elements.delete_variant_id.value = variantId;
        deleteModal.show();
    }

    elements.confirm_delete_btn.addEventListener("click", function () {
        const variantId = elements.delete_variant_id.value;

        fetch(`/api/inventory/variants/delete/${variantId}`, {
            method: "DELETE",
        })
            .then(res => res.json())
            .then(data => {
                deleteModal.hide();
                refreshCurrentPage();
                if (data.success) {
                    showSuccessToast(data.message || "Variant deleted successfully");
                } else {
                    throw new Error(data.message);
                }
            })
            .catch(err => {
                if (typeof showErrorToast === "function") {
                    showErrorToast(err);
                    console.error(err);
                } else {
                    console.error(err);
                }
            });
    });

    function openEditModal(variantId) {
        fetch(`/api/inventory/variants/${variantId}`)
            .then(res => res.json())
            .then(data => {
                elements.variant_id.value = data.variant_id;
                elements.variant_shoe.value = data.shoe_id;
                elements.variant_size.value = data.size_id;
                elements.variant_stock.value = data.variant_stock;
                elements.variant_modal_title.textContent = "Edit Variant";
                showAllSizes();
                variantModal.show();
            })
            .catch(err => {
                if (typeof showErrorToast === "function") {
                    showErrorToast(err);
                    console.error(err);
                } else {
                    console.error(err);
                }
            });
    }

    elements.save_variant_btn.addEventListener("click", function () {
        if (!elements.variant_form.checkValidity()) {
            elements.variant_form.reportValidity();
            return;
        }

        const formData = new FormData();
        formData.append("shoe_id", elements.variant_shoe.value);
        formData.append("size_id", elements.variant_size.value);
        formData.append("variant_stock", elements.variant_stock.value);

        const isEdit = !!elements.variant_id.value;
        const url = isEdit ? "/api/inventory/variants/update" : "/api/inventory/variants/add";
        if (isEdit) {
            formData.append("variant_id", elements.variant_id.value);
        }

        fetch(url, {
            method: "POST",
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    variantModal.hide();
                    refreshCurrentPage();
                    if (typeof showSuccessToast === "function") {
                        showSuccessToast(data.message || "Variant saved successfully");
                    }
                } else {
                    throw new Error(data.message || "Failed to save variant");
                }
            })
            .catch(err => {
                if (typeof showErrorToast === "function") {
                    showErrorToast(err);
                    console.error(err);
                } else {
                    console.error(err);
                }
            });
    });

    function searchVariants(formData) {
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
                        items.forEach(addShoeToList);
                    }

                    renderPagination(pages);
                } catch (err) {
                    throw new Error(err);
                }
            })
            .catch(err => {
                if (typeof showErrorToast === "function") {
                    showErrorToast(err);
                    console.error(err);
                } else {
                    console.error(err);
                }
            });
    }

    function addShoeToList(shoe) {
        // Clone the shoe container template
        const shoeContainer = elements.shoe_container_template.content.cloneNode(true);

        // Get elements from the cloned template
        const shoeImage = shoeContainer.querySelector('.shoe-image');
        const shoeInfo = shoeContainer.querySelector('.shoe-info');
        const variantsContainer = shoeContainer.querySelector('.variants-container');
        const collapsibleHeader = shoeContainer.querySelector('.collapsible-header');



        // Set unique ID for collapse
        const collapseId = `collapse-${shoe.shoe_id}`;
        variantsContainer.id = collapseId;
        collapsibleHeader.setAttribute('data-bs-target', `#${collapseId}`);
        collapsibleHeader.setAttribute('aria-expanded', 'true');
        collapsibleHeader.setAttribute('aria-controls', collapseId);


        // Set shoe image
        shoeImage.src = `/shoe?shoe_id=${shoe.shoe_id}`;
        shoeImage.alt = shoe.shoe_name;

        // Set shoe info
        const shoeName = shoeContainer.querySelector('.shoe-name');
        const shoeBrand = shoeContainer.querySelector('.shoe-brand');
        shoeName.textContent = shoe.shoe_name;
        shoeBrand.textContent = shoe.brand_name;

        // Add collapse event listeners
        variantsContainer.addEventListener('show.bs.collapse', () => {
            const toggleIcon = collapsibleHeader.querySelector('.toggle-icon');
            toggleIcon.classList.add('rotated');

        });

        variantsContainer.addEventListener('hide.bs.collapse', function () {
            const toggleIcon = collapsibleHeader.querySelector('.toggle-icon');
            toggleIcon.classList.remove('rotated');

        });

        // Add each variant
        shoe.variants.forEach(variant => {
            const elem = elements.template.content.cloneNode(true);
            const card = elem.querySelector(".variant-item");
            const idEl = elem.querySelector(".variant-id");
            const detailsEl = elem.querySelector(".variant-details");

            card.dataset.variantId = variant.variant_id;
            idEl.textContent = `ID: ${variant.variant_id}`;
            detailsEl.textContent = `Size US: ${variant.us_size} | UK: ${variant.uk_size} | EU: ${variant.eu_size} (Stock: ${variant.variant_stock})`;

            variantsContainer.appendChild(elem);
        });

        elements.shoe_list.appendChild(shoeContainer);
    }

    function renderPagination(totalPages) {
        elements.pagination.innerHTML = "";
        const currentPage = parseInt(elements.page_input.value) || 1;

        if (totalPages <= 1) return;

        const prevBtn = document.createElement("button");
        prevBtn.className = `btn btn-sm ${currentPage === 1 ? "btn-secondary" : "btn-outline-primary"}`;
        prevBtn.textContent = "Prev";
        prevBtn.disabled = currentPage === 1;
        prevBtn.addEventListener("click", () => goToPage(currentPage - 1));
        elements.pagination.appendChild(prevBtn);

        for (let i = 1; i <= totalPages; i++) {
            const pageBtn = document.createElement("button");
            pageBtn.className = `btn btn-sm ${i === currentPage ? "btn-primary" : "btn-outline-primary"}`;
            pageBtn.textContent = i;
            pageBtn.addEventListener("click", () => goToPage(i));
            elements.pagination.appendChild(pageBtn);
        }

        const nextBtn = document.createElement("button");
        nextBtn.className = `btn btn-sm ${currentPage === totalPages ? "btn-secondary" : "btn-outline-primary"}`;
        nextBtn.textContent = "Next";
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.addEventListener("click", () => goToPage(currentPage + 1));
        elements.pagination.appendChild(nextBtn);
    }

    function goToPage(page) {
        elements.page_input.value = page;
        const formData = new FormData(elements.search_form);
        searchVariants(formData);
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function showAllSizes() {
        const sizeOptions = elements.variant_size.querySelectorAll('option');
        sizeOptions.forEach(option => {
            option.style.display = '';
        });
    }

    function refreshCurrentPage() {
        const formData = new FormData(elements.search_form);
        searchVariants(formData);
    }

    window.addEventListener("DOMContentLoaded", () => {
        searchVariants();
    });
})();
