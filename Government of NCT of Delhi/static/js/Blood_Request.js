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

// Handle action button clicks (approve or reject)
document.querySelectorAll('button.approve').forEach(button => {
    button.addEventListener('click', function() {
        const row = this.closest('tr');
        row.querySelector('td:nth-child(7)').textContent = 'Approved';
        this.disabled = true;
        row.querySelector('button.reject').disabled = true;
    });
});

document.querySelectorAll('button.reject').forEach(button => {
    button.addEventListener('click', function() {
        const row = this.closest('tr');
        row.querySelector('td:nth-child(7)').textContent = 'Rejected';
        this.disabled = true;
        row.querySelector('button.approve').disabled = true;
    });
});
