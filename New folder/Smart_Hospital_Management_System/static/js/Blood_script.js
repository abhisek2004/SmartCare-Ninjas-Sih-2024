// Toggle the upper navbar on mobile view
function toggleNav() {
    const navLinks = document.getElementById('nav-links');
    navLinks.classList.toggle('active');
}

// Toggle the sidebar on smaller screens
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

// Optional: Close the sidebar when a link is clicked (for a better user experience on mobile)
document.querySelectorAll('.sidebar ul li a').forEach(link => {
    link.addEventListener('click', () => {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.remove('active');
    });
});

// Optional: Close the upper navbar when a link is clicked (for a better user experience on mobile)
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        const navLinks = document.getElementById('nav-links');
        navLinks.classList.remove('active');
    });
});
