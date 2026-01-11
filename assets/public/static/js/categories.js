(function () {
    // Get Bootstrap modal instances
    const categoryModal = new bootstrap.Modal(document.getElementById("category-modal"));
    const deleteModal = new bootstrap.Modal(document.getElementById("delete-modal"));
    const elements = {
        template: document.getElementById("category-item-template"),
        category_list: document.getElementById("category-list"),
        search_form: document.getElementById("search-form"),
        page_input: document.getElementById("page-input"),
        pagination: document.getElementById("pagination"),
        add_category_btn: document.getElementById("add-category-btn"),
        category_form: document.getElementById("category-form"),
        category_id: document.getElementById("category-id"),
        category_name: document.getElementById("category-name"),
        category_modal_title: document.getElementById("category-modal-title"),
        save_category_btn: document.getElementById("save-category-btn"),
        delete_category_id: document.getElementById("delete-category-id"),
        confirm_delete_btn: document.getElementById("confirm-delete-btn")
    };

    // Search handler
    elements.search_form.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(elements.search_form);
        elements.page_input.value = 1;
        searchCategories(formData);
    });

    // Prevent search form submission when modal is open
    elements.category_form.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
        }
    });

    // Search on input clear
    elements.search_form.querySelector('input[type="search"]').addEventListener("input", function (e) {
        if (e.target.value === "") {
            elements.page_input.value = 1;
            const formData = new FormData(elements.search_form);
            searchCategories(formData);
        }
    });


    elements.search_form.querySelector('input[type="search"]').addEventListener("change", function (e) {
        elements.page_input.value = 1;
        const formData = new FormData(elements.search_form);
        searchCategories(formData);
    });

    // Add category button handler
    elements.add_category_btn.addEventListener("click", function () {
        elements.category_form.reset();
        elements.category_id.value = "";
        elements.category_modal_title.textContent = "Add Category";
        categoryModal.show();
    });

    // Edit button handler (delegated)
    elements.category_list.addEventListener("click", function (e) {
        const editBtn = e.target.closest(".edit-btn");
        if (editBtn) {
            const card = editBtn.closest(".category-item");
            const categoryId = card.dataset.categoryId;
            openEditModal(categoryId);
        }
    });

    // Delete button handler (delegated)
    elements.category_list.addEventListener("click", function (e) {
        const deleteBtn = e.target.closest(".delete-btn");
        if (deleteBtn) {
            const card = deleteBtn.closest(".category-item");
            const categoryId = card.dataset.categoryId;
            openDeleteModal(categoryId);
        }
    });

    // Open delete modal
    function openDeleteModal(categoryId) {
        elements.delete_category_id.value = categoryId;
        deleteModal.show();
    }

    // Confirm delete handler
    elements.confirm_delete_btn.addEventListener("click", function () {
        const categoryId = elements.delete_category_id.value;

        fetch(`/api/inventory/categories/delete/${categoryId}`, {
            method: "DELETE",
        })
            .then(res => res.json())
            .then(data => {
                deleteModal.hide();
                refreshCurrentPage();
                console.log(data)
                if (data.success) {
                    showSuccessToast(data.message || "Category deleted successfully");
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

    // Open edit modal and fetch category data
    function openEditModal(categoryId) {
        fetch(`/api/inventory/categories/${categoryId}`)
            .then(res => res.json())
            .then(data => {
                elements.category_id.value = data.category_id;
                elements.category_name.value = data.category_name;
                elements.category_modal_title.textContent = "Edit Category";
                categoryModal.show();
            })
            .catch(err => {
                if (typeof showErrorToast === "function") {
                    showErrorToast(err);
                } else {
                    console.error(err);
                }
            });
    }

    // Save category handler
    elements.save_category_btn.addEventListener("click", function () {
        if (!elements.category_form.checkValidity()) {
            elements.category_form.reportValidity();
            return;
        }

        const formData = new FormData();
        formData.append("category_name", elements.category_name.value);

        const isEdit = !!elements.category_id.value;
        const url = isEdit ? "/api/inventory/categories/update" : "/api/inventory/categories/add";
        if (isEdit) {
            formData.append("category_id", elements.category_id.value);
        }

        fetch(url, {
            method: "POST",
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    categoryModal.hide();
                    refreshCurrentPage();
                    if (typeof showSuccessToast === "function") {
                        showSuccessToast(data.message || "Category saved successfully");
                    }
                } else {
                    throw new Error(data.message || "Failed to save category");
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

    // Fetch and display categories
    function searchCategories(formData) {
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
                    elements.category_list.replaceChildren();

                    if (count === 0) {
                        elements.category_list.innerHTML = '<div class="text-center py-4 text-muted">No items found</div>';
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

    // Add single category item to list
    function addItemToList(item) {
        const elem = elements.template.content.cloneNode(true);
        const card = elem.querySelector(".category-item");
        const idEl = elem.querySelector(".category-id");
        const nameEl = elem.querySelector(".category-name");

        card.dataset.categoryId = item.category_id;
        idEl.textContent = `ID: ${item.category_id}`;
        nameEl.textContent = item.category_name;

        elements.category_list.appendChild(elem);
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
        searchCategories(formData);
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    // Refresh current page
    function refreshCurrentPage() {
        const formData = new FormData(elements.search_form);
        searchCategories(formData);
    }

    // Initialize on load
    window.addEventListener("DOMContentLoaded", () => {
        searchCategories();
    });
})();
