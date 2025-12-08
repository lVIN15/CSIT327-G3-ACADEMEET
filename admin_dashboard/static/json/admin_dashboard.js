document.addEventListener('DOMContentLoaded', function() {
    // Select all filter buttons and all user rows
    const filterButtons = document.querySelectorAll('.filter-tabs .tab');
    const userRows = document.querySelectorAll('.user-row');

    function filterUsers(filterStatus) {
        userRows.forEach(row => {
            // Check if the row's class contains the specific filter status
            const matchesFilter = row.classList.contains(filterStatus + '-account');

            if (filterStatus === 'all') {
                row.style.display = ''; // Show all rows
            } else if (matchesFilter) {
                row.style.display = ''; // Show matching rows
            } else {
                row.style.display = 'none'; // Hide non-matching rows
            }
        });
    }

    // Attach click listeners to the filter buttons
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the status from the button's data attribute (e.g., 'active', 'deactivated')
            const filterStatus = this.getAttribute('data-filter');

            // Update button styling: remove 'active' from all, add to the clicked one
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            // Run the filtering logic
            filterUsers(filterStatus);
        });
    });

    // Run the filter on page load to ensure 'All' is selected and visible
    filterUsers('all');
});