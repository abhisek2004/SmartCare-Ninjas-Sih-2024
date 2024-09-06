document.querySelectorAll('.bed').forEach(bed => {
    bed.addEventListener('click', function () {
        // Remove the 'selected' class from any previously selected bed
        document.querySelectorAll('.bed').forEach(b => b.classList.remove('selected'));
        // Add the 'selected' class to the clicked bed
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