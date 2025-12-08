class Calendar {
    constructor() {
        this.date = new Date();
        this.holidays = {};
        this.tooltipElement = document.getElementById('holidayTooltip');
        this.init();
    }

    async init() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupEventListeners();
                this.loadHolidays().then(() => this.render());
            });
        } else {
            this.setupEventListeners();
            await this.loadHolidays();
            this.render();
        }
    }

    setupEventListeners() {
        const prevButton = document.getElementById('prevMonth');
        const nextButton = document.getElementById('nextMonth');

        if (prevButton && nextButton) {
            prevButton.addEventListener('click', () => {
                this.date.setMonth(this.date.getMonth() - 1);
                this.loadHolidays().then(() => this.render());
            });

            nextButton.addEventListener('click', () => {
                this.date.setMonth(this.date.getMonth() + 1);
                this.loadHolidays().then(() => this.render());
            });
        }

        // Handle tooltip positioning
        document.addEventListener('mousemove', (e) => {
            const target = e.target;
            if (target && target.classList && target.classList.contains('holiday')) {
                const rect = target.getBoundingClientRect();
                const holidayObj = this.holidays[target.dataset.date];
                if (holidayObj) {
                    // Pass an object with date and name so showTooltip can format
                    this.showTooltip({ date: target.dataset.date, name: holidayObj.name }, rect);
                }
            } else {
                this.hideTooltip();
            }
        });
    }

    async loadHolidays() {
        const year = this.date.getFullYear();
        const month = this.date.getMonth() + 1;
        try {
            const response = await fetch(`/api/holidays/${year}/${month}/`);
            const data = await response.json();
            // Normalize holiday objects so we can show date + name in tooltip
            this.holidays = data.reduce((acc, holiday) => {
                const name = holiday.holiday_name || holiday.name || holiday.holiday || holiday.title || '';
                acc[holiday.date] = { name, raw: holiday };
                return acc;
            }, {});
        } catch (error) {
            console.error('Error loading holidays:', error);
            this.holidays = {};
        }
    }

    showTooltip(text, targetRect) {
        // allow passing either string or object { date, name }
        const textToShow = typeof text === 'string' ? text : (text.name ? `${text.date} — ${text.name}` : JSON.stringify(text));
        this.tooltipElement.textContent = textToShow;
        this.tooltipElement.classList.add('visible');

        // Position the tooltip above the date
        const tooltipRect = this.tooltipElement.getBoundingClientRect();
        const top = targetRect.top - tooltipRect.height - 10;
        const left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);

        this.tooltipElement.style.top = `${top}px`;
        this.tooltipElement.style.left = `${left}px`;
    }

    hideTooltip() {
        this.tooltipElement.classList.remove('visible');
    }

    render() {
        // Update month/year display
        const monthYearText = this.date.toLocaleString('default', { 
            month: 'long', 
            year: 'numeric' 
        });
        document.getElementById('monthYear').textContent = monthYearText;

        const tbody = document.getElementById('calendarBody');
        tbody.innerHTML = '';

        // Get first day of month and total days
        const firstDay = new Date(this.date.getFullYear(), this.date.getMonth(), 1);
        const lastDay = new Date(this.date.getFullYear(), this.date.getMonth() + 1, 0);
        
        let currentDay = 1;
        const today = new Date();

        // Create calendar grid
        for (let i = 0; i < 6; i++) {
            const row = document.createElement('tr');
            
            for (let j = 0; j < 7; j++) {
                const cell = document.createElement('td');
                
                if (i === 0 && j < firstDay.getDay()) {
                    cell.textContent = '';
                } else if (currentDay > lastDay.getDate()) {
                    cell.textContent = '';
                } else {
                    cell.textContent = currentDay;
                    
                    // Format date string for holiday lookup
                    const dateStr = `${this.date.getFullYear()}-${String(this.date.getMonth() + 1).padStart(2, '0')}-${String(currentDay).padStart(2, '0')}`;
                    
                    // Check if current date is a holiday
                    if (this.holidays[dateStr]) {
                        cell.classList.add('holiday');
                        cell.dataset.date = dateStr;
                    }
                    
                    // Highlight current day
                    if (this.date.getFullYear() === today.getFullYear() &&
                        this.date.getMonth() === today.getMonth() &&
                        currentDay === today.getDate()) {
                        cell.classList.add('current-day');
                    }
                    
                    currentDay++;
                }
                
                row.appendChild(cell);
            }
            
            tbody.appendChild(row);
            if (currentDay > lastDay.getDate()) break;
        }
    }
};

// Initialize calendar when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Calendar();
});