// Wait for DOM to fully load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Student Dashboard JS loaded');

    // Dropdown buttons and menus
    const departmentDropdownButton = document.getElementById('departmentDropdownButton');
    const departmentDropdownMenu = document.getElementById('departmentDropdownMenu');
    const selectedDepartment = document.getElementById('selectedDepartment');

    const timeDropdownButton = document.getElementById('timeDropdownButton');
    const timeDropdownMenu = document.getElementById('timeDropdownMenu');
    const selectedTime = document.getElementById('selectedTime');

    const daysDropdownButton = document.getElementById('daysDropdownButton');
    const daysDropdownMenu = document.getElementById('daysDropdownMenu');
    const selectedDays = document.getElementById('selectedDays');

    const tableRows = document.querySelectorAll('#scheduleTableBody tr[data-department]');
    const searchInput = document.getElementById('searchInput');

    console.log('Found table rows:', tableRows.length);

    // State for filters
    let selectedTimes = [];
    let selectedDaysList = [];
    // NEW: store selected department code (e.g. "CCS", "CMBA", "All")
    let selectedDeptCode = 'All';

    // Toggle dropdowns
    departmentDropdownButton.addEventListener('click', (e) => {
        e.stopPropagation();
        departmentDropdownMenu.classList.toggle('show');
        timeDropdownMenu.classList.remove('show');
        daysDropdownMenu.classList.remove('show');
    });

    timeDropdownButton.addEventListener('click', (e) => {
        e.stopPropagation();
        timeDropdownMenu.classList.toggle('show');
        departmentDropdownMenu.classList.remove('show');
        daysDropdownMenu.classList.remove('show');
    });

    daysDropdownButton.addEventListener('click', (e) => {
        e.stopPropagation();
        daysDropdownMenu.classList.toggle('show');
        departmentDropdownMenu.classList.remove('show');
        timeDropdownMenu.classList.remove('show');
    });

    // Department filter: use data-department (code) for comparisons
    departmentDropdownMenu.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            // Each button should have data-department attribute (e.g. "CCS" or "All")
            const deptCode = btn.dataset.department || btn.getAttribute('data-department') || 'All';
            selectedDeptCode = deptCode;
            // Display the friendly text on the button (uses visible label)
            selectedDepartment.textContent = btn.textContent.trim();
            departmentDropdownMenu.classList.remove('show');
            // Slight delay to allow UI update
            setTimeout(filterTable, 50);
        });
    });

    // Time filter with multi-select
    const timeCheckboxes = document.querySelectorAll('.time-checkbox');
    const allTimesCheckbox = document.getElementById('allTimesCheckbox');

    timeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            if (checkbox.dataset.time === 'all') {
                if (checkbox.checked) {
                    timeCheckboxes.forEach(cb => {
                        if (cb !== checkbox) cb.checked = false;
                    });
                    selectedTimes = [];
                }
            } else {
                if (checkbox.checked) {
                    allTimesCheckbox.checked = false;
                }
            }

            // Update selected times
            selectedTimes = Array.from(timeCheckboxes)
                .filter(cb => cb.checked && cb.dataset.time !== 'all')
                .map(cb => cb.dataset.time);

            // Update button text
            if (selectedTimes.length === 0) {
                selectedTime.textContent = 'All Times';
                allTimesCheckbox.checked = true;
            } else if (selectedTimes.length === 1) {
                const hour = selectedTimes[0];
                selectedTime.textContent = formatTimeRange(hour);
            } else {
                selectedTime.textContent = `${selectedTimes.length} times selected`;
            }

            filterTable();
        });
    });

    // Days filter
    const dayCheckboxes = document.querySelectorAll('.day-checkbox');
    const allDaysCheckbox = document.getElementById('allDaysCheckbox');

    dayCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            if (checkbox.dataset.day === 'all') {
                if (checkbox.checked) {
                    dayCheckboxes.forEach(cb => {
                        if (cb !== checkbox) cb.checked = false;
                    });
                    selectedDaysList = [];
                }
            } else {
                if (checkbox.checked) {
                    allDaysCheckbox.checked = false;
                }
            }

            selectedDaysList = Array.from(dayCheckboxes)
                .filter(cb => cb.checked && cb.dataset.day !== 'all')
                .map(cb => cb.dataset.day);

            if (selectedDaysList.length === 0) {
                selectedDays.textContent = 'All Days';
                allDaysCheckbox.checked = true;
            } else if (selectedDaysList.length === 1) {
                selectedDays.textContent = selectedDaysList[0];
            } else {
                selectedDays.textContent = `${selectedDaysList.length} days selected`;
            }

            filterTable();
        });
    });

    // Helper function to format time range
    function formatTimeRange(hour) {
        const hourInt = parseInt(hour);
        const nextHour = hourInt + 1;
        const formatHour = (h) => {
            const period = h >= 12 ? 'PM' : 'AM';
            const displayHour = h > 12 ? h - 12 : (h === 0 ? 12 : h);
            return `${displayHour.toString().padStart(2, '0')}:00 ${period}`;
        };
        return `${formatHour(hourInt)} - ${formatHour(nextHour)}`;
    }

    // Converts "HH:MM" → minutes since midnight
    function timeToMinutes(timeStr) {
        const [hours, minutes] = timeStr.split(':').map(Number);
        return hours * 60 + minutes;
    }

    // Search filter
    searchInput.addEventListener('keyup', filterTable);

    // Combined filter function
    function filterTable() {
        const searchQuery = searchInput.value.toLowerCase();

        tableRows.forEach(row => {
            const dept = row.getAttribute('data-department'); // department code stored in the row (e.g. CCS)
            const day = row.getAttribute('data-day');
            const searchData = row.getAttribute('data-search') || '';

            // Department match (compare codes)
            const deptMatch = (selectedDeptCode === 'All' || !selectedDeptCode) ? true : (dept === selectedDeptCode);

            // Search match
            const searchMatch = searchData.includes(searchQuery);

            // Time match (overlapping logic)
            let timeMatch = true;
            if (selectedTimes.length > 0) {
                const startText = row.querySelector('td:nth-child(3)').textContent.trim();
                const [startStr, endStr] = startText.split(' - ').map(t => t.trim());
                const rowStart = convertToMinutes(startStr);
                const rowEnd = convertToMinutes(endStr);

                timeMatch = selectedTimes.some(selectedHour => {
                    const selectedStart = parseInt(selectedHour);
                    const selectedEnd = selectedStart + 1;
                    const selStartMin = selectedStart * 60;
                    const selEndMin = selectedEnd * 60;
                    // overlap check
                    return (selStartMin < rowEnd && selEndMin > rowStart);
                });
            }

            // Day match
            let dayMatch = true;
            if (selectedDaysList.length > 0) {
                dayMatch = selectedDaysList.includes(day);
            }

            // Show row only if all filters match
            row.style.display = (deptMatch && searchMatch && timeMatch && dayMatch) ? '' : 'none';
        });
    }

    // Converts "10:30 AM" or "01:00 PM" to minutes
    function convertToMinutes(timeStr) {
        const [time, modifier] = timeStr.split(' ');
        let [hours, minutes] = time.split(':').map(Number);
        if (modifier === 'PM' && hours !== 12) hours += 12;
        if (modifier === 'AM' && hours === 12) hours = 0;
        return hours * 60 + minutes;
    }

    // Close dropdowns when clicking outside
    window.addEventListener('click', (e) => {
        if (!departmentDropdownButton.contains(e.target) && !departmentDropdownMenu.contains(e.target)) {
            departmentDropdownMenu.classList.remove('show');
        }
        if (!timeDropdownButton.contains(e.target) && !timeDropdownMenu.contains(e.target)) {
            timeDropdownMenu.classList.remove('show');
        }
        if (!daysDropdownButton.contains(e.target) && !daysDropdownMenu.contains(e.target)) {
            daysDropdownMenu.classList.remove('show');
        }
    });

    // Click handler for rows to view professor schedule
    document.querySelectorAll('.schedule-row').forEach(row => {
        row.addEventListener('click', () => {
            const professorId = row.getAttribute('data-professor-id');
            console.log('Clicked professor ID:', professorId);
            window.location.href = `/professor/${professorId}/schedule/`;
        });
    });

    // Initialize "All Times" and "All Days" as checked
    allTimesCheckbox.checked = true;
    allDaysCheckbox.checked = true;

    // Initialize department display
    selectedDepartment.textContent = 'All Departments';
    selectedDeptCode = 'All';

    console.log('All event listeners attached successfully');
});
