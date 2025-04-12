// Function to calculate and display the patient's age based on their date of birth
function calculateAge() {
    const dobElement = document.getElementById('patient-dob');
    const ageElement = document.getElementById('patient-age');

    if (dobElement && ageElement) {
        const dob = new Date(dobElement.textContent);
        const diff = Date.now() - dob.getTime();
        const ageDate = new Date(diff);
        const calculatedAge = Math.abs(ageDate.getUTCFullYear() - 1970);

        ageElement.textContent = calculatedAge + ' years';
    }
}

// Function to toggle the navigation links on smaller screens
function toggleNav() {
    const navLinks = document.getElementById('nav-links');
    navLinks.classList.toggle('active');
}

// Event listener to calculate the patient's age when the page loads
document.addEventListener('DOMContentLoaded', () => {
    calculateAge();
});

// Example of form submission handling (for future development)
document.getElementById('patient-form')?.addEventListener('submit', function (e) {
    e.preventDefault();
    // Handle form submission here (e.g., sending data to a server)
    alert('Patient information submitted successfully!');
});

