document.addEventListener('DOMContentLoaded', function() {
    loadHolidays();
});

async function loadHolidays() {
    const holidayList = document.getElementById('holidayList');
    
    try {
        const response = await fetch('/api/holidays/');
        const data = await response.json();
        
        if (data.length === 0) {
            holidayList.innerHTML = '<p>No upcoming holidays</p>';
            return;
        }

        const holidayHTML = data.map(holiday => {
            const date = new Date(holiday.date).toLocaleDateString('en-PH', {
                month: 'long',
                day: 'numeric',
                year: 'numeric'
            });
            
            return `
                <li class="holiday-item">
                    <span class="holiday-date">${date}</span>
                    <span class="holiday-desc">${holiday.description}</span>
                </li>
            `;
        }).join('');

        holidayList.innerHTML = `<ul class="holiday-items">${holidayHTML}</ul>`;
    } catch (error) {
        console.error('Error loading holidays:', error);
        holidayList.innerHTML = '<p class="error">Error loading holidays</p>';
    }
}