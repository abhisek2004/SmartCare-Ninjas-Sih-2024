// script.js

document.querySelectorAll('.bed').forEach(bed => {
    bed.addEventListener('click', function () {
        document.querySelectorAll('.bed').forEach(b => b.classList.remove('selected'));
        this.classList.add('selected');
    });
});

document.getElementById('book-btn').addEventListener('click', function () {
    const selectedBed = document.querySelector('.bed.selected');
    
    if (selectedBed) {
        const bedNumber = selectedBed.getAttribute('data-bed');
        
        // Redirect to the success page with the bed number in the URL
        window.location.href = `success.html?bed=${bedNumber}`;
    } else {
        alert('Please select a bed to book.');
    }
});

