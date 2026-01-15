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
        number: /\d/.test(password)
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
        showErrorToast('New passwords do not match');
        return;
    }

    try {
        const formData = new FormData(document.getElementById('password-form'));

        const response = await fetch('/api/users/updatePassword', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showSuccessToast('Password changed successfully!');
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
            showErrorToast('Error: ' + result.message);
        }
    } catch (error) {
        showErrorToast('Network error occurred');
    }
});



// Password visibility toggle
document.querySelectorAll('.toggle-password').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('data-target');
        const input = document.getElementById(targetId);
        const icon = this.children[0];

        if (input.type === 'password') {
            input.type = 'text';
            icon.setAttribute("data-icon", 'eye-slash');
        } else {
            input.type = 'password';
            icon.setAttribute("data-icon", 'eye');
        }
    });
});
