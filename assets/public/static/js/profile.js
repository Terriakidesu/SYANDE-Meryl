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
        formData.append('file', fileInput.files[0]);
    }

    // Add form data
    formData.append("user_id", parseInt(document.getElementById("user_id").value))
    formData.append('username', document.getElementById('username').value);
    formData.append('first_name', document.getElementById('first-name').value);
    formData.append('last_name', document.getElementById('last-name').value);
    formData.append('email', document.getElementById('email').value);

    try {
        const response = await fetch('/api/users/update', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            showSuccessToast('Profile updated successfully!');
        } else {
            const error = await response.json();
            showErrorToast('Error: ' + error.message);
        }
    } catch (error) {

        if (error) showErrorToast('Network error occurred');
    }
});
