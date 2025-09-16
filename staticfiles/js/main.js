// BookingMVP Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initBackToTop();
    initLoadingOverlay();
    initFormValidation();
    initSearchFunctionality();
    initFilters();
    initDatePickers();
    initTooltips();
    initAnimations();
    
    console.log('BookingMVP: JavaScript initialized');
});

// Back to Top Button
function initBackToTop() {
    const backToTopBtn = document.getElementById('back-to-top');
    if (!backToTopBtn) return;
    
    function toggleBackToTop() {
        if (window.pageYOffset > 100) {
            backToTopBtn.classList.remove('d-none');
        } else {
            backToTopBtn.classList.add('d-none');
        }
    }
    
    window.addEventListener('scroll', toggleBackToTop);
    
    backToTopBtn.addEventListener('click', function(e) {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Loading Overlay
function initLoadingOverlay() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (!loadingOverlay) return;
    
    // Show loading on form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            showLoading();
        });
    });
    
    // Show loading on AJAX requests
    if (typeof fetch !== 'undefined') {
        const originalFetch = fetch;
        fetch = function(...args) {
            showLoading();
            return originalFetch.apply(this, args)
                .finally(() => hideLoading());
        };
    }
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('d-none');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('d-none');
    }
}

// Form Validation
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time validation
    document.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });
}

function validateField(field) {
    const isValid = field.checkValidity();
    field.classList.remove('is-valid', 'is-invalid');
    field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    
    // Custom validation messages
    const feedback = field.parentNode.querySelector('.invalid-feedback');
    if (feedback && !isValid) {
        feedback.textContent = getValidationMessage(field);
    }
}

function getValidationMessage(field) {
    if (field.validity.valueMissing) {
        return `${field.labels[0]?.textContent || 'This field'} is required.`;
    }
    if (field.validity.typeMismatch) {
        return `Please enter a valid ${field.type}.`;
    }
    if (field.validity.patternMismatch) {
        return field.dataset.patternMessage || 'Please match the requested format.';
    }
    if (field.validity.tooShort) {
        return `Minimum length is ${field.minLength} characters.`;
    }
    if (field.validity.tooLong) {
        return `Maximum length is ${field.maxLength} characters.`;
    }
    return field.validationMessage;
}

// Search Functionality
function initSearchFunctionality() {
    const searchForm = document.getElementById('search-form');
    if (!searchForm) return;
    
    // Auto-complete for location search
    const locationInput = document.getElementById('location');
    if (locationInput) {
        let debounceTimer;
        locationInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                searchLocations(this.value);
            }, 300);
        });
    }
    
    // Date validation
    const checkInDate = document.getElementById('check_in');
    const checkOutDate = document.getElementById('check_out');
    
    if (checkInDate && checkOutDate) {
        checkInDate.addEventListener('change', function() {
            const checkInValue = new Date(this.value);
            const tomorrow = new Date(checkInValue);
            tomorrow.setDate(tomorrow.getDate() + 1);
            
            checkOutDate.min = tomorrow.toISOString().split('T')[0];
            if (checkOutDate.value && new Date(checkOutDate.value) <= checkInValue) {
                checkOutDate.value = tomorrow.toISOString().split('T')[0];
            }
        });
    }
}

function searchLocations(query) {
    if (query.length < 2) return;
    
    // This would typically make an API call
    // For now, we'll just show a simple example
    console.log('Searching for:', query);
}

// Filters
function initFilters() {
    const filterForm = document.getElementById('filters-form');
    if (!filterForm) return;
    
    // Price range slider
    const priceRange = document.getElementById('price-range');
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    
    if (priceRange && minPriceInput && maxPriceInput) {
        // Update inputs when range changes
        priceRange.addEventListener('input', function() {
            const values = this.value.split(',');
            minPriceInput.value = values[0];
            maxPriceInput.value = values[1];
            updatePriceDisplay();
        });
        
        // Update range when inputs change
        [minPriceInput, maxPriceInput].forEach(input => {
            input.addEventListener('input', function() {
                priceRange.value = `${minPriceInput.value},${maxPriceInput.value}`;
                updatePriceDisplay();
            });
        });
    }
    
    // Auto-submit filters with debounce
    let filterDebounce;
    filterForm.addEventListener('change', function() {
        clearTimeout(filterDebounce);
        filterDebounce = setTimeout(() => {
            applyFilters();
        }, 500);
    });
    
    // Clear filters
    const clearFiltersBtn = document.getElementById('clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            filterForm.reset();
            applyFilters();
        });
    }
}

function updatePriceDisplay() {
    const minPrice = document.getElementById('min-price')?.value || 0;
    const maxPrice = document.getElementById('max-price')?.value || 1000;
    const display = document.getElementById('price-display');
    
    if (display) {
        display.textContent = `$${minPrice} - $${maxPrice}`;
    }
}

function applyFilters() {
    const filterForm = document.getElementById('filters-form');
    if (!filterForm) return;
    
    const formData = new FormData(filterForm);
    const params = new URLSearchParams();
    
    for (let [key, value] of formData.entries()) {
        if (value) {
            params.append(key, value);
        }
    }
    
    // Update URL and reload results
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', newUrl);
    
    // Here you would typically fetch new results via AJAX
    // For now, we'll just reload the page
    if (params.toString()) {
        window.location.reload();
    }
}

// Date Pickers
function initDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        if (!input.hasAttribute('min')) {
            input.min = today;
        }
        
        // Add calendar icon
        if (!input.parentNode.querySelector('.date-icon')) {
            const icon = document.createElement('i');
            icon.className = 'fas fa-calendar-alt date-icon';
            icon.style.cssText = 'position: absolute; right: 10px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6c757d;';
            
            input.parentNode.style.position = 'relative';
            input.parentNode.appendChild(icon);
        }
    });
}

// Tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
}

// Animations
function initAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements with animation classes
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
    
    // Stagger animation for cards
    const cards = document.querySelectorAll('.hotel-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('slide-up');
    });
}

// Utility Functions
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

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// API Helper Functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        showLoading();
        const response = await fetch(url, finalOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        showNotification('An error occurred. Please try again.', 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Notification System
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

// Hotel Card Interactions
document.addEventListener('click', function(e) {
    if (e.target.closest('.hotel-card')) {
        const card = e.target.closest('.hotel-card');
        const hotelId = card.dataset.hotelId;
        
        if (hotelId && !e.target.closest('a, button')) {
            // Navigate to hotel detail page
            window.location.href = `/hotels/${hotelId}/`;
        }
    }
});

// Wishlist functionality
function toggleWishlist(hotelId) {
    apiRequest(`/api/wishlist/toggle/${hotelId}/`, {
        method: 'POST'
    })
    .then(data => {
        const button = document.querySelector(`[data-hotel-id="${hotelId}"] .wishlist-btn`);
        if (button) {
            const icon = button.querySelector('i');
            if (data.added) {
                icon.className = 'fas fa-heart text-danger';
                showNotification('Added to wishlist', 'success');
            } else {
                icon.className = 'far fa-heart';
                showNotification('Removed from wishlist', 'info');
            }
        }
    })
    .catch(error => {
        console.error('Wishlist toggle failed:', error);
    });
}

// Export functions for global use
window.BookingMVP = {
    showLoading,
    hideLoading,
    showNotification,
    apiRequest,
    toggleWishlist
};