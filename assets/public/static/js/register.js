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
    resendTimerSpan: () => elements.resendCodeButton.querySelector('span')
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
 * Initialize all event listeners and functionality
 */
function initializeRegistration() {
    setupPasswordToggle();
    setupEmailForm();
    setupOtpForm();
    setupRegisterForm();
    setupNavigation();
    setupResendCode();
}

// Start the registration process when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeRegistration);
