/**
 * Form validation functions
 */

const validationRules = {
    email: (value) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(value);
    },
    phone: (value) => {
        return value.length >= 10;
    },
    password: (value) => {
        return value.length >= 6;
    },
    amount: (value) => {
        return parseFloat(value) > 0;
    },
    required: (value) => {
        return value.trim().length > 0;
    },
    date: (value) => {
        const date = new Date(value);
        const today = new Date();
        const age = today.getFullYear() - date.getFullYear();
        return age >= 18;
    }
};

/**
 * Validate form
 */
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        if (input.required && !validationRules.required(input.value)) {
            markInvalid(input, 'This field is required');
            isValid = false;
        } else if (input.type === 'email' && input.value && !validationRules.email(input.value)) {
            markInvalid(input, 'Invalid email format');
            isValid = false;
        } else if (input.type === 'tel' && input.value && !validationRules.phone(input.value)) {
            markInvalid(input, 'Phone number must be at least 10 digits');
            isValid = false;
        } else if (input.type === 'number' && input.value && !validationRules.amount(input.value)) {
            markInvalid(input, 'Amount must be greater than 0');
            isValid = false;
        } else if (input.type === 'date' && input.value && !validationRules.date(input.value)) {
            markInvalid(input, 'You must be at least 18 years old');
            isValid = false;
        } else {
            markValid(input);
        }
    });
    
    return isValid;
}

/**
 * Mark input as invalid
 */
function markInvalid(input, message) {
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    
    let errorEl = input.nextElementSibling;
    if (!errorEl || !errorEl.classList.contains('error-message')) {
        errorEl = document.createElement('div');
        errorEl.className = 'error-message';
        input.parentNode.insertBefore(errorEl, input.nextSibling);
    }
    errorEl.textContent = message;
}

/**
 * Mark input as valid
 */
function markValid(input) {
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    
    const errorEl = input.nextElementSibling;
    if (errorEl && errorEl.classList.contains('error-message')) {
        errorEl.remove();
    }
}

/**
 * Add inline validation
 */
document.addEventListener('input', (e) => {
    if (e.target.matches('input, textarea')) {
        const input = e.target;
        if (input.required) {
            if (validationRules.required(input.value)) {
                markValid(input);
            }
        }
    }
});

/**
 * Validate on blur
 */
document.addEventListener('blur', (e) => {
    if (e.target.matches('input[type="email"]')) {
        if (e.target.value && !validationRules.email(e.target.value)) {
            markInvalid(e.target, 'Invalid email format');
        } else {
            markValid(e.target);
        }
    }
}, true);

/**
 * Custom styles for validation
 */
const style = document.createElement('style');
style.textContent = `
    .is-invalid {
        border-color: #f5576c !important;
        background-color: rgba(245, 87, 108, 0.05) !important;
    }
    
    .is-valid {
        border-color: #43e97b !important;
        background-color: rgba(67, 233, 123, 0.05) !important;
    }
    
    .error-message {
        color: #f5576c;
        font-size: 0.85rem;
        margin-top: 0.3rem;
        display: block;
    }
`;
document.head.appendChild(style);
