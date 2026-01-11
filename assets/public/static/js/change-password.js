const passwordInput = document.getElementById('new-password');
const confirmPasswordInput = document.getElementById('confirm-password');
const changePasswordBtn = document.getElementById('change-password-btn');
const passwordMatchText = document.getElementById('password-match-text');

// Password validation requirements
const requirements = {
    length: { element: document.getElementById('req-length'), icon: document.getElementById('icon-length') },
    uppercase: { element: document.getElementById('req-uppercase'), icon: document.getElementById('icon-uppercase') },
    lowercase: { element: document.getElementById('req-lowercase'), icon: document.getElementById('icon-lowercase') },
    number: { element: document.getElementById('req-number'), icon: document.getElementById('icon-number') },
    special: { element: document.getElementById('req-special'), icon: document.getElementById('icon-special') }
};

function validatePassword(password) {
    const checks = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /\d/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    let allValid = true;

    for (const [key, check] of Object.entries(checks)) {
        if (check) {
            requirements[key].element.classList.add('valid');
            requirements[key].icon.className = 'fa-solid fa-check-circle';
        } else {
            requirements[key].element.classList.remove('valid');
            requirements[key].icon.className = 'fa-solid fa-circle';
            allValid = false;
        }
    }

    return allValid;
}

function checkPasswordsMatch() {
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    if (confirmPassword === '') {
        passwordMatchText.textContent = '';
        passwordMatchText.className = 'form-text';
        return false;
    }

    if (password === confirmPassword) {
        passwordMatchText.textContent = 'Passwords match!';
        passwordMatchText.className = 'form-text text-success';
        return true;
    } else {
        passwordMatchText.textContent = 'Passwords do not match!';
        passwordMatchText.className = 'form-text text-danger';
        return false;
    }
}

passwordInput.addEventListener('input', function () {
    const isValid = validatePassword(passwordInput.value);
    const passwordsMatch = checkPasswordsMatch();

    changePasswordBtn.disabled = !(isValid && passwordsMatch);
});

confirmPasswordInput.addEventListener('input', function () {
    const isValid = validatePassword(passwordInput.value);
    const passwordsMatch = checkPasswordsMatch();

    changePasswordBtn.disabled = !(isValid && passwordsMatch);
});

// Form Submission
document.getElementById('password-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (newPassword !== confirmPassword) {
        showToast('New passwords do not match', 'danger');
        return;
    }

    try {
        const response = await fetch('/api/users/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });

        if (response.ok) {
            showToast('Password changed successfully!', 'success');
            // Clear form
            document.getElementById('password-form').reset();
            // Reset validation states
            for (const req of Object.values(requirements)) {
                req.element.classList.remove('valid');
                req.icon.className = 'fa-solid fa-circle';
            }
            passwordMatchText.textContent = '';
            passwordMatchText.className = 'form-text';
            changePasswordBtn.disabled = true;
        } else {
            const error = await response.json();
            showToast('Error: ' + error.message, 'danger');
        }
    } catch (error) {
        showToast('Network error occurred', 'danger');
    }
});

function showToast(message, type = 'success') {
    const toastEl = document.getElementById('password-toast');
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
