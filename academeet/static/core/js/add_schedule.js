// Counter for schedule entries
let scheduleCount = 1;

// Add a new schedule entry
function addScheduleEntry() {
    scheduleCount++;
    
    const scheduleEntries = document.getElementById('scheduleEntries');
    
    const newEntry = document.createElement('div');
    newEntry.className = 'schedule-entry';
    newEntry.innerHTML = `
        <div class="entry-header">
            <h3>Schedule Entry ${scheduleCount}</h3>
            <button type="button" class="remove-btn" onclick="removeSchedule(this)">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
        </div>

        <div class="form-row">
            <div class="form-group">
                <label for="department">Department</label>
                <select name="department[]" required>
                    <option value="">Select Department</option>
                    <option value="CCS">College of Computer Studies</option>
                    <option value="CMBA">College of Management, Business, and Accountancy</option>
                    <option value="CCJ">College of Criminal Justice</option>
                    <option value="CNAHS">College of Nursing and Allied Health Sciences</option>
                    <option value="CEA">College of Engineering and Architecture</option>
                    <option value="CASE">College of Arts, Sciences and Education</option>
                </select>
            </div>
        </div>

        <div class="form-row">
            <div class="form-group">
                <label for="subject_code">Subject Code</label>
                <input type="text" name="subject_code[]" placeholder="e.g. CSIT104" required>
            </div>
            <div class="form-group">
                <label for="subject_name">Subject Name</label>
                <input type="text" name="subject_name[]" placeholder="e.g. Programming Fundamentals" required>
            </div>
        </div>

        <div class="form-row">
            <div class="form-group">
                <label for="section">Section</label>
                <input type="text" name="section[]" placeholder="e.g. G7-AP4" required>
            </div>
            <div class="form-group">
                <label for="room">Room</label>
                <input type="text" name="room[]" placeholder="e.g. RTL223" required>
            </div>
            <div class="form-group">
                <label for="year_level">Year Level</label>
                <select name="year_level[]" required>
                    <option value="">Select Year Level</option>
                    <option value="1st">1st Year</option>
                    <option value="2nd">2nd Year</option>
                    <option value="3rd">3rd Year</option>
                    <option value="4th">4th Year</option>
                    <option value="5th">5th Year</option>
                </select>
            </div>
        </div>

        <div class="form-row">
            <div class="form-group">
                <label for="day">Day</label>
                <select name="day[]" required>
                    <option value="">Select Day</option>
                    <option value="Monday">Monday</option>
                    <option value="Tuesday">Tuesday</option>
                    <option value="Wednesday">Wednesday</option>
                    <option value="Thursday">Thursday</option>
                    <option value="Friday">Friday</option>
                    <option value="Saturday">Saturday</option>
                    <option value="Sunday">Sunday</option>
                </select>
            </div>
            <div class="form-group">
                <label>Time Slot</label>
                <div class="time-slot-group">
                    <input type="time" name="time_from[]" required>
                    <span class="time-separator">to</span>
                    <input type="time" name="time_to[]" required>
                </div>
            </div>
            <div class="form-group">
                <label for="status">Status</label>
                <select name="status[]" required>
                    <option value="">Select Status</option>
                    <option value="Class">Class</option>
                    <option value="Out of work">Out of work</option>
                    <option value="Available">Available</option>
                </select>
            </div>
        </div>
    `;
    
    scheduleEntries.appendChild(newEntry);
    
    // Smooth scroll to the new entry
    setTimeout(() => {
        newEntry.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
}

// Remove a schedule entry
function removeSchedule(button) {
    const entries = document.querySelectorAll('.schedule-entry');
    
    // Don't remove if it's the only entry
    if (entries.length <= 1) {
        alert('You must have at least one schedule entry.');
        return;
    }
    
    const entry = button.closest('.schedule-entry');
    entry.style.animation = 'fadeOut 0.3s ease-out';
    
    setTimeout(() => {
        entry.remove();
        updateEntryNumbers();
    }, 300);
}

// Update entry numbers after removal
function updateEntryNumbers() {
    const entries = document.querySelectorAll('.schedule-entry');
    entries.forEach((entry, index) => {
        const header = entry.querySelector('.entry-header h3');
        if (index === 0) {
            header.textContent = 'Schedule Entry';
        } else {
            header.textContent = `Schedule Entry ${index + 1}`;
        }
    });
    scheduleCount = entries.length;
}

// Add fadeOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(-10px); }
    }
`;
document.head.appendChild(style);

// Form validation
document.getElementById('scheduleForm').addEventListener('submit', function(e) {
    const entries = document.querySelectorAll('.schedule-entry');
    
    if (entries.length === 0) {
        e.preventDefault();
        alert('Please add at least one schedule entry.');
        return;
    }
    
    // Validate time slots
    let isValid = true;
    entries.forEach((entry, index) => {
        const timeFrom = entry.querySelector('input[name="time_from[]"]').value;
        const timeTo = entry.querySelector('input[name="time_to[]"]').value;
        
        if (timeFrom && timeTo && timeFrom >= timeTo) {
            isValid = false;
            alert(`Schedule Entry ${index + 1}: End time must be after start time.`);
        }
    });
    
    if (!isValid) {
        e.preventDefault();
    }
});