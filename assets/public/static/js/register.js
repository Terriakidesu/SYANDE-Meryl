/**
 * Registration Form Handler
 *
 * This script manages the multi-step registration process including:
 * - Password visibility toggle
 * - Email verification and OTP request
 * - OTP verification
 * - User registration
 * - Form navigation
 * - OTP resend functionality with timer
 * - Progress indicator updates
 */

// Global state
let resendInterval = undefined;
const DEFAULT_RESEND_TIMEOUT = 30000; // 30 seconds in milliseconds

// Password validation constants
const PASSWORD_MIN_LENGTH = 8;
const ALLOWED_SPECIAL_CHARS = '!@#$%^&*';
const PASSWORD_REGEX = new RegExp(`^[a-zA-Z0-9${ALLOWED_SPECIAL_CHARS.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}]+$`);

/**
 * DOM Element Cache
 * Centralized element references for better maintainability
 */
const elements = {
    // Forms
    emailForm: document.querySelector('form#email-form'),
    otpForm: document.querySelector('form#otp-form'),
    registerForm: document.querySelector('form#register-form'),

    // Buttons
    togglePassword: document.getElementById('togglePassword'),
    otpBackButton: document.querySelector('button#otp-back-button'),
    registerBackButton: document.querySelector('button#register-back-button'),
    resendCodeButton: document.querySelector('button#resend_code'),

    // Progress indicator
    progressContainer: document.querySelector('div#progress-container'),

    // OTP display elements
    otpEmailSpan: () => document.querySelector('#email-span'),
    resendTimerSpan: () => elements.resendCodeButton.querySelector('span'),

    // Password elements
    passwordInput: () => document.getElementById('password'),
    passwordRequirements: {
        length: () => document.getElementById('req-length'),
        uppercase: () => document.getElementById('req-uppercase'),
        lowercase: () => document.getElementById('req-lowercase'),
        number: () => document.getElementById('req-number'),
        special: () => document.getElementById('req-special'),
        validChars: () => document.getElementById('req-valid-chars')
    }
};

/**
 * Toggle password visibility with eye icon
 */
function setupPasswordToggle() {
    if (!elements.togglePassword) return;

    elements.togglePassword.addEventListener('click', function () {
        const passwordInput = document.getElementById('password');
        const icon = this.children[0];

        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            passwordInput.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    });
}

/**
 * Handle email form submission
 * Verifies email and requests OTP
 */
function setupEmailForm() {
    if (!elements.emailForm) return;

    elements.emailForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        try {
            const formData = new FormData(this);
            const email = formData.get('email');

            // Verify email
            const verifyResponse = await fetch('/api/auth/verify_email', {
                method: 'POST',
                body: formData
            });

            const verifyData = await verifyResponse.json();

            if (!verifyData.success) {
                throw new Error('Email verification failed');
            }

            // Request OTP
            const otpResponse = await fetch('/api/auth/request_otp', {
                method: 'POST',
                body: formData
            });

            const otpData = await otpResponse.json();

            if (otpData.success) {
                startResendTimer();
                updateProgressTabs('OTP');

                // Update OTP form with email and transition
                elements.otpEmailSpan().textContent = email;

                await animateFormTransition(elements.emailForm, elements.otpForm);
            } else {
                throw new Error('OTP request failed');
            }

        } catch (error) {
            console.error('Email form submission error:', error);
        }
    });
}

/**
 * Handle OTP form submission
 */
function setupOtpForm() {
    if (!elements.otpForm) return;

    elements.otpForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        try {
            const formData = new FormData(this);

            const otp = formData.get('otp');

            if (otp.length < 6) {
                this.querySelector("input[name=otp]").setCustomValidity("OTP must be 6 digits");
                return;
            }

            const response = await fetch('/api/auth/verify_otp', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {

                const detailForm = new FormData(elements.emailForm);
                elements.registerForm.querySelector("input[name=username]").value = detailForm.get("first_name").toLowerCase();
                updateProgressTabs("Account");
                await animateFormTransition(elements.otpForm, elements.registerForm);
            } else {
                throw new Error('OTP verification failed');
            }

        } catch (error) {
            console.error('OTP form submission error:', error);
        }
    });
}

/**
 * Handle registration form submission
 */
function setupRegisterForm() {
    if (!elements.registerForm) return;

    elements.registerForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        try {
            const formData = new FormData(this);
            const emailFormData = new FormData(elements.emailForm);

            // Merge email form data into registration form data
            for (const [name, value] of emailFormData.entries()) {
                formData.append(name, value);
            }

            const response = await fetch('/api/auth/register', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                console.log('Registration successful:', data);
                // TODO: Handle successful registration (redirect, etc.)
            } else {
                throw new Error('Registration failed');
            }

        } catch (error) {
            console.error('Registration form submission error:', error);
        }
    });
}

/**
 * Handle back button navigation between forms
 */
function setupNavigation() {
    // OTP form back to email form
    if (elements.otpBackButton) {
        elements.otpBackButton.addEventListener('click', async () => {
            updateProgressTabs('Details');
            elements.otpEmailSpan().textContent = 'johndoe@email.com';
            await animateFormTransition(elements.otpForm, elements.emailForm, true);
        });
    }

    // Registration form back to OTP form
    if (elements.registerBackButton) {
        elements.registerBackButton.addEventListener('click', async () => {
            updateProgressTabs('OTP');
            await animateFormTransition(elements.registerForm, elements.otpForm, true);
        });
    }
}

/**
 * Handle OTP resend functionality
 */
function setupResendCode() {
    if (!elements.resendCodeButton) return;

    elements.resendCodeButton.addEventListener('click', async function (event) {
        event.preventDefault();

        // Prevent multiple clicks during countdown
        if (resendInterval !== undefined) {
            return;
        }

        try {
            const formData = new FormData(elements.emailForm);
            formData.append('request_new', true);

            const response = await fetch('/api/auth/request_otp', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                startResendTimer();
            } else {
                throw new Error('Failed to resend OTP');
            }

        } catch (error) {
            console.error('Resend OTP error:', error);
        }
    });
}

/**
 * Start the resend timer countdown
 */
function startResendTimer() {
    const timerSpan = elements.resendTimerSpan();
    timerSpan.textContent = '00:30';

    const startTime = new Date().getTime();

    // Clear any existing interval
    if (resendInterval !== undefined) {
        clearInterval(resendInterval);
    }

    resendInterval = setInterval(() => {
        const now = new Date().getTime();
        const elapsedTime = now - startTime;
        const remainingSeconds = 30 - Math.floor(elapsedTime / 1000);

        // Format as MM:SS
        const displayTime = remainingSeconds.toString().padStart(2, '0');
        timerSpan.textContent = `00:${displayTime}`;

        // Reset when timer completes
        if (elapsedTime > DEFAULT_RESEND_TIMEOUT) {
            clearInterval(resendInterval);
            resendInterval = undefined;
            timerSpan.textContent = 'Resend Code';
        }
    }, 1000);
}

/**
 * Update progress indicator tabs
 * @param {string} activeTab - Name of the tab to activate ('Details', 'OTP', 'Done')
 */
function updateProgressTabs(activeTab) {
    if (!elements.progressContainer) return;

    const tabs = elements.progressContainer.querySelectorAll('div.progress-label');
    let activeIndex = 0;

    // Determine active tab index
    switch (activeTab) {
        case 'Details': activeIndex = 0; break;
        case 'OTP': activeIndex = 1; break;
        case 'Account': activeIndex = 2; break;
        default: return;
    }

    // Update tab states
    tabs.forEach((tab, index) => {
        tab.classList.remove('progress-label-done', 'progress-label-active');

        if (index <= activeIndex) {
            tab.classList.add('progress-label-done');
        }

        if (index === activeIndex) {
            tab.classList.add('progress-label-active');
        }
    });
}

/**
 * Animate form transition with fade effect
 * @param {HTMLElement} fromForm - Form to hide
 * @param {HTMLElement} toForm - Form to show
 * @param {boolean} isBackNavigation - Whether this is a back navigation
 */
async function animateFormTransition(fromForm, toForm, isBackNavigation = false) {
    return new Promise((resolve) => {
        fromForm.animate(
            [
                { opacity: 1 },
                { opacity: 0 }
            ],
            {
                easing: 'ease-out',
                duration: 300
            }
        ).addEventListener('finish', function () {
            fromForm.style.display = 'none';
            toForm.style.display = 'block';

            // Reset animation for next time
            fromForm.style.opacity = '1';
            toForm.style.opacity = '1';

            resolve();
        });
    });
}

/**
 * Validate password requirements
 * @param {string} password - Password to validate
 * @returns {Object} Validation results for each requirement
 */
function validatePassword(password) {
    if (!password) {
        return {
            length: false,
            uppercase: false,
            lowercase: false,
            number: false,
            special: false,
            validChars: true
        };
    }

    return {
        length: password.length >= PASSWORD_MIN_LENGTH,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        special: new RegExp(`[${ALLOWED_SPECIAL_CHARS.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}]`).test(password),
        validChars: PASSWORD_REGEX.test(password)
    };
}

/**
 * Update password requirement indicators based on validation
 * @param {Object} validation - Validation results from validatePassword
 */
function updatePasswordRequirements(validation) {
    const requirements = elements.passwordRequirements;

    // Update each requirement indicator
    Object.entries(validation).forEach(([requirement, isValid]) => {
        const element = requirements[requirement]();
        if (element) {
            element.classList.remove('valid', 'invalid');

            if (isValid) {
                element.classList.add('valid');
            } else if (requirement !== 'validChars' || !isValid) {
                element.classList.add('invalid');
            }
        }
    });
}

/**
 * Setup realtime password validation
 */
function setupPasswordValidation() {
    const passwordInput = elements.passwordInput();
    if (!passwordInput) return;

    // Add input event listener for realtime validation
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const validation = validatePassword(password);
        updatePasswordRequirements(validation);
    });

    // Add blur event listener to validate when field loses focus
    passwordInput.addEventListener('blur', function() {
        const password = this.value;
        const validation = validatePassword(password);

        // Only show invalid state if field has been touched
        if (password.length > 0) {
            updatePasswordRequirements(validation);

            // Validate overall password strength
            const isPasswordValid = Object.values(validation).every(Boolean);
            if (!isPasswordValid) {
                this.setCustomValidity('Password does not meet requirements');
            } else {
                this.setCustomValidity('');
            }
        }
    });
}

/**
 * Initialize all event listeners and functionality
 */
function initializeRegistration() {
    setupPasswordToggle();
    setupEmailForm();
    setupOtpForm();
    setupRegisterForm();
    setupNavigation();
    setupResendCode();
    setupPasswordValidation();
}

// Start the registration process when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeRegistration);
