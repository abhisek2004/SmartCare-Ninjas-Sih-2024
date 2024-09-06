// Toggle the upper navbar on mobile view
function toggleNav() {
    const navLinks = document.getElementById('nav-links');
    navLinks.classList.toggle('active');
}

// Optional: Close the upper navbar when a link is clicked (for a better user experience on mobile)
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        const navLinks = document.getElementById('nav-links');
        navLinks.classList.remove('active');
    });
});

// Form submission handlers for donor registration and login
document.getElementById('donor-form').addEventListener('submit', function(e) {
    e.preventDefault();
    // Handle donor registration here
    alert('Donor registered successfully!');
});

document.getElementById('login-form').addEventListener('submit', function(e) {
    e.preventDefault();
    // Handle donor login here
    alert('Logged in successfully!');
});
function toggleNav() {
    const navLinks = document.getElementById('nav-links');
    navLinks.classList.toggle('active');
}

function openPopup(popupId) {
    document.getElementById(popupId).style.display = 'flex';
}

function closePopup(popupId) {
    document.getElementById(popupId).style.display = 'none';
}

