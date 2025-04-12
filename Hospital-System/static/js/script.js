const navbar = document.querySelector('.sticky-navbar');

// Listen for the scroll event
window.addEventListener('scroll', () => {
  if (window.scrollY > 100) { // Adjust the pixel value to control when the navbar becomes sticky
    navbar.classList.add('sticky');
  } else {
    navbar.classList.remove('sticky');
  }
});


// appointment codition 

function selectDoctor() {
  const diseaseInput = document.getElementById("diseaseInput").value;
  let doctorResult = document.getElementById("doctorResult");

  if (diseaseInput === "diabetes" || diseaseInput === "cancer" || diseaseInput === "hypertension" || diseaseInput === "asthma" || diseaseInput === "alzheimer") {
    doctorResult.textContent = "Dr. Mohammed Hassan";
  } else if (diseaseInput === "influenza" || diseaseInput === "heart-disease" || diseaseInput === "malaria" || diseaseInput === "parkinson") {
    doctorResult.textContent = "Dr. Jamal Ahmed";
  } else if (diseaseInput === "hepatitis" || diseaseInput === "covid-19" || diseaseInput === "dementia") {
    doctorResult.textContent = "Dr. Amina Khan";
  } else if (diseaseInput === "stroke" || diseaseInput === "copd") {
    doctorResult.textContent = "Dr. Fatima Malik";
  } else {
    doctorResult.textContent = "No matching doctor found.";
  }
}
