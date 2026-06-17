/**
 * API request helper functions
 */

const API = {
    /**
     * Make a GET request
     */
    get: async (url) => {
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    },
    
    /**
     * Make a POST request
     */
    post: async (url, data) => {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    },
    
    /**
     * Make a PUT request
     */
    put: async (url, data) => {
        try {
            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('API PUT Error:', error);
            throw error;
        }
    },
    
    /**
     * Make a DELETE request
     */
    delete: async (url) => {
        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            return await response.json();
        } catch (error) {
            console.error('API DELETE Error:', error);
            throw error;
        }
    }
};

/**
 * Loading state helper
 */
function setLoading(element, isLoading = true) {
    if (isLoading) {
        element.disabled = true;
        element.innerHTML = `<span class="spinner"></span> Loading...`;
    } else {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText || 'Submit';
    }
}

/**
 * Handle API responses
 */
function handleResponse(response) {
    if (response.status === 'success') {
        showNotification(response.message || 'Operation successful', 'success');
        return response.data;
    } else {
        showNotification(response.message || 'Operation failed', 'error');
        throw new Error(response.message);
    }
}

/**
 * Debounce function for search and filter operations
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Initialize common event handlers
 */
document.addEventListener('DOMContentLoaded', () => {
    // Store original button text for loading state
    document.querySelectorAll('button[type="submit"]').forEach(btn => {
        btn.dataset.originalText = btn.innerHTML;
    });
    
    // Check session on page load
    checkSession();
});

/**
 * Check if user is logged in
 */
async function checkSession() {
    try {
        const response = await API.get('/auth/check-session');
        if (response.status === 'error') {
            // Redirect to login if not authenticated
            if (window.location.pathname !== '/auth/login' && window.location.pathname !== '/auth/register') {
                window.location.href = '/auth/login';
            }
        }
    } catch (error) {
        console.log('Session check failed');
    }
}
