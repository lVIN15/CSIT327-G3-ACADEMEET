// Status selector functionality
function toggleStatusDropdown() {
    const selector = document.getElementById('statusSelector');
    selector.classList.toggle('active');

    // Close dropdown when clicking outside
    document.addEventListener('click', function closeDropdown(e) {
        if (!selector.contains(e.target)) {
            selector.classList.remove('active');
            document.removeEventListener('click', closeDropdown);
        }
    });
}

function updateStatus(status) {
    const statusDot = document.querySelector('.current-status .status-dot');
    const statusText = document.querySelector('.current-status .status-text');
    const selector = document.getElementById('statusSelector');
    const toast = document.getElementById('statusToast');
    const toastMessage = document.querySelector('.toast-message');
    
    // Update status dot and text
    statusDot.className = 'status-dot status-' + status;
    statusText.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    
    // Close dropdown
    selector.classList.remove('active');
    
    // Show toast notification
    toastMessage.textContent = `Your status has been updated to ${status}`;
    toast.classList.add('show');
    
    // Hide toast after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);

    // Send status update to server
    fetch('/update_status/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ status: status })
    }).then(response => {
        if (!response.ok) {
            throw new Error('Failed to update status');
        }
    }).catch(error => {
        console.error('Error:', error);
        toastMessage.textContent = 'Failed to update status. Please try again.';
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    });
}

// Helper function to get CSRF token from cookies
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