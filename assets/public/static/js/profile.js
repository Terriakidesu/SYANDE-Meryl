// Profile Picture Preview
document.getElementById('profile-picture-input').addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById('current-profile-pic').src = e.target.result;
        }
        reader.readAsDataURL(file);
    }
});

// Form Submission
document.getElementById('profile-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData();
    const fileInput = document.getElementById('profile-picture-input');

    // Add profile picture if selected
    if (fileInput.files[0]) {
        formData.append('profile_picture', fileInput.files[0]);
    }

    // Add form data
    formData.append('first_name', document.getElementById('first-name').value);
    formData.append('last_name', document.getElementById('last-name').value);
    formData.append('email', document.getElementById('email').value);
    formData.append('phone', document.getElementById('phone').value);
    formData.append('address', document.getElementById('address').value);

    try {
        const response = await fetch('/api/users/profile', {
            method: 'PUT',
            body: formData
        });

        if (response.ok) {
            showToast('Profile updated successfully!');
        } else {
            const error = await response.json();
            showToast('Error: ' + error.message, 'danger');
        }
    } catch (error) {
        showToast('Network error occurred', 'danger');
    }
});

function showToast(message, type = 'success') {
    const toastEl = document.getElementById('profile-toast');
    const toastBody = document.getElementById('toast-message');
    const toastHeader = toastEl.querySelector('.toast-header strong');

    toastBody.textContent = message;
    toastHeader.textContent = type === 'success' ? 'Success' : 'Error';

    if (type === 'danger') {
        toastHeader.className = 'me-auto text-danger';
        toastEl.querySelector('.toast-header i').className = 'fa-solid fa-circle-exclamation text-danger me-2';
    } else {
        toastHeader.className = 'me-auto';
        toastEl.querySelector('.toast-header i').className = 'fa-solid fa-circle-check text-success me-2';
    }

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}
