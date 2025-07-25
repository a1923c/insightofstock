// Main JavaScript functionality for Insight of Stock

// Global utility functions
const Utils = {
    formatNumber: function(num) {
        if (num === 0) return '0';
        
        if (num >= 100000000) {
            return (num / 100000000).toFixed(2) + '亿';
        } else if (num >= 10000) {
            return (num / 10000).toFixed(2) + '万';
        } else {
            return num.toLocaleString();
        }
    },

    formatDate: function(dateStr) {
        if (!dateStr || dateStr === 'nan') return 'N/A';
        
        try {
            const year = dateStr.substring(0, 4);
            const month = dateStr.substring(4, 6);
            const day = dateStr.substring(6, 8);
            return `${year}-${month}-${day}`;
        } catch (e) {
            return dateStr;
        }
    },

    formatDateTime: function(dateTimeStr) {
        if (!dateTimeStr) return 'Never';
        return new Date(dateTimeStr).toLocaleString();
    },

    showToast: function(message, type = 'info') {
        // Create toast element
        const toastContainer = document.createElement('div');
        toastContainer.className = 'position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1050';
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        document.body.appendChild(toastContainer);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Clean up after toast is hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toastContainer.remove();
        });
    },

    showError: function(message, containerId = null) {
        if (containerId) {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = `<div class="alert alert-danger">${message}</div>`;
            }
        } else {
            this.showToast(message, 'danger');
        }
    },

    showSuccess: function(message) {
        this.showToast(message, 'success');
    },

    showLoading: function(containerId, text = 'Loading...') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">${text}</span>
                    </div>
                    <p class="mt-2">${text}</p>
                </div>
            `;
        }
    },

    hideLoading: function(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
        }
    }
};

// API helper
const API = {
    baseURL: '',

    async request(endpoint, options = {}) {
        try {
            const response = await fetch(this.baseURL + endpoint, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    async getTickers() {
        return this.request('/api/tickers');
    },

    async getTickerHolders(tsCode) {
        return this.request(`/api/tickers/${tsCode}/holders`);
    },

    async updateData() {
        return this.request('/api/update-data', { method: 'POST' });
    }
};

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Global functions for inline usage
window.updateData = async function() {
    const modal = new bootstrap.Modal(document.getElementById('updateModal'));
    const statusDiv = document.getElementById('updateStatus');
    
    statusDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Updating data...</p></div>';
    modal.show();
    
    try {
        const result = await API.updateData();
        if (result.success) {
            statusDiv.innerHTML = '<div class="alert alert-success">' + result.message + '</div>';
            Utils.showSuccess('Data updated successfully');
            
            // Reload current page data after 2 seconds
            setTimeout(() => {
                modal.hide();
                if (typeof loadTickers === 'function') {
                    loadTickers();
                } else if (typeof loadTickerDetails === 'function') {
                    loadTickerDetails();
                }
            }, 2000);
        } else {
            throw new Error(result.error || 'Update failed');
        }
    } catch (error) {
        statusDiv.innerHTML = '<div class="alert alert-danger">Failed to update data: ' + error.message + '</div>';
        Utils.showError('Failed to update data: ' + error.message);
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Utils, API };
}