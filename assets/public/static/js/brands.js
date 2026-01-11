(function () {
    // Get Bootstrap modal instances
    const brandModal = new bootstrap.Modal(document.getElementById("brand-modal"));
    const deleteModal = new bootstrap.Modal(document.getElementById("delete-modal"));
    const elements = {
        template: document.getElementById("brand-item-template"),
        brand_list: document.getElementById("brand-list"),
        search_form: document.getElementById("search-form"),
        page_input: document.getElementById("page-input"),
        pagination: document.getElementById("pagination"),
        add_brand_btn: document.getElementById("add-brand-btn"),
        brand_form: document.getElementById("brand-form"),
        brand_id: document.getElementById("brand-id"),
        brand_name: document.getElementById("brand-name"),
        brand_modal_title: document.getElementById("brand-modal-title"),
        save_brand_btn: document.getElementById("save-brand-btn"),
        delete_brand_id: document.getElementById("delete-brand-id"),
        confirm_delete_btn: document.getElementById("confirm-delete-btn")
    };

    // Search handler
    elements.search_form.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(elements.search_form);
        elements.page_input.value = 1;
        searchBrands(formData);
    });

    // Prevent search form submission when modal is open
    elements.brand_form.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
        }
    });

    // Search on input clear
    elements.search_form.querySelector('input[type="search"]').addEventListener("input", function (e) {
        if (e.target.value === "") {
            elements.page_input.value = 1;
            const formData = new FormData(elements.search_form);
            searchBrands(formData);
        }
    });


    elements.search_form.querySelector('input[type="search"]').addEventListener("change", function (e) {
        elements.page_input.value = 1;
        const formData = new FormData(elements.search_form);
        searchBrands(formData);
    });

    // Add brand button handler
    elements.add_brand_btn.addEventListener("click", function () {
        elements.brand_form.reset();
        elements.brand_id.value = "";
        elements.brand_modal_title.textContent = "Add Brand";
        brandModal.show();
    });

    // Edit button handler (delegated)
    elements.brand_list.addEventListener("click", function (e) {
        const editBtn = e.target.closest(".edit-btn");
        if (editBtn) {
            const card = editBtn.closest(".brand-item");
            const brandId = card.dataset.brandId;
            openEditModal(brandId);
        }
    });

    // Delete button handler (delegated)
    elements.brand_list.addEventListener("click", function (e) {
        const deleteBtn = e.target.closest(".delete-btn");
        if (deleteBtn) {
            const card = deleteBtn.closest(".brand-item");
            const brandId = card.dataset.brandId;
            openDeleteModal(brandId);
        }
    });

    // Open delete modal
    function openDeleteModal(brandId) {
        elements.delete_brand_id.value = brandId;
        deleteModal.show();
    }

    // Confirm delete handler
    elements.confirm_delete_btn.addEventListener("click", function () {
        const brandId = elements.delete_brand_id.value;

        fetch(`/api/inventory/brands/delete/${brandId}`, {
            method: "DELETE",
        })
            .then(res => res.json())
            .then(data => {
                deleteModal.hide();
                refreshCurrentPage();
                console.log(data)
                if (data.success) {
                    showSuccessToast(data.message || "Brand deleted successfully");
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

    // Open edit modal and fetch brand data
    function openEditModal(brandId) {
        fetch(`/api/inventory/brands/${brandId}`)
            .then(res => res.json())
            .then(data => {
                elements.brand_id.value = data.brand_id;
                elements.brand_name.value = data.brand_name;
                elements.brand_modal_title.textContent = "Edit Brand";
                brandModal.show();
            })
            .catch(err => {
                if (typeof showErrorToast === "function") {
                    showErrorToast(err);
                } else {
                    console.error(err);
                }
            });
    }

    // Save brand handler
    elements.save_brand_btn.addEventListener("click", function () {
        if (!elements.brand_form.checkValidity()) {
            elements.brand_form.reportValidity();
            return;
        }

        const formData = new FormData();
        formData.append("brand_name", elements.brand_name.value);

        const isEdit = !!elements.brand_id.value;
        const url = isEdit ? "/api/inventory/brands/update" : "/api/inventory/brands/add";
        if (isEdit) {
            formData.append("brand_id", elements.brand_id.value);
        }

        fetch(url, {
            method: "POST",
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    brandModal.hide();
                    refreshCurrentPage();
                    if (typeof showSuccessToast === "function") {
                        showSuccessToast(data.message || "Brand saved successfully");
                    }
                } else {
                    throw new Error(data.message || "Failed to save brand");
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

    // Fetch and display brands
    function searchBrands(formData) {
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
                    elements.brand_list.replaceChildren();

                    if (count === 0) {
                        elements.brand_list.innerHTML = '<div class="text-center py-4 text-muted">No items found</div>';
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

    // Add single brand item to list
    function addItemToList(item) {
        const elem = elements.template.content.cloneNode(true);
        const card = elem.querySelector(".brand-item");
        const idEl = elem.querySelector(".brand-id");
        const nameEl = elem.querySelector(".brand-name");

        card.dataset.brandId = item.brand_id;
        idEl.textContent = `ID: ${item.brand_id}`;
        nameEl.textContent = item.brand_name;

        elements.brand_list.appendChild(elem);
    }

    // Render pagination
    function renderPagination(totalPages) {
        elements.pagination.innerHTML = "";
        const currentPage = parseInt(elements.page_input.value) || 1;

        if (totalPages <= 1) return;

        // Previous button
        const prevBtn = document.createElement("button");
        prevBtn.className = `btn btn-sm ${currentPage === 1 ? "btn-secondary" : "btn-outline-primary"}`;
        prevBtn.textContent = "Prev";
        prevBtn.disabled = currentPage === 1;
        prevBtn.addEventListener("click", () => goToPage(currentPage - 1));
        elements.pagination.appendChild(prevBtn);

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            const pageBtn = document.createElement("button");
            pageBtn.className = `btn btn-sm ${i === currentPage ? "btn-primary" : "btn-outline-primary"}`;
            pageBtn.textContent = i;
            pageBtn.addEventListener("click", () => goToPage(i));
            elements.pagination.appendChild(pageBtn);
        }

        // Next button
        const nextBtn = document.createElement("button");
        nextBtn.className = `btn btn-sm ${currentPage === totalPages ? "btn-secondary" : "btn-outline-primary"}`;
        nextBtn.textContent = "Next";
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.addEventListener("click", () => goToPage(currentPage + 1));
        elements.pagination.appendChild(nextBtn);
    }

    // Go to specific page
    function goToPage(page) {
        elements.page_input.value = page;
        const formData = new FormData(elements.search_form);
        searchBrands(formData);
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    // Refresh current page
    function refreshCurrentPage() {
        const formData = new FormData(elements.search_form);
        searchBrands(formData);
    }

    // Initialize on load
    window.addEventListener("DOMContentLoaded", () => {
        searchBrands();
    });
})();
