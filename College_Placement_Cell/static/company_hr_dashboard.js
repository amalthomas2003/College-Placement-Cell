function updateDateTime() {
    const datetimeElement = document.getElementById("datetime");
    const now = new Date();
    const formattedDate = formatDate(now); // Format the date

    datetimeElement.textContent = formattedDate;
}

function formatDate(date) {
    const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' };
    return date.toLocaleDateString('en-US', options);
}

updateDateTime(); // Update initially

setInterval(updateDateTime, 1000); // Update every second


function toggleDropdown() {
    const dropdown = document.getElementById('dropdownContent');
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
}

// Close dropdown when clicking outside
document.addEventListener('click', function (event) {
    const dropdown = document.getElementById('dropdownContent');
    const profileImage = document.querySelector('.profile-image');

    if (!profileImage.contains(event.target) && !dropdown.contains(event.target) && dropdown.style.display === 'block') {
        dropdown.style.display = 'none';
    }
});

// Close the user button menu if the user clicks outside of it
document.addEventListener('click', function (event) {
    const userButtonMenu = document.getElementById('userButtonMenu');
    const userProfile = document.querySelector('.user-profile');

    if (!userProfile.contains(event.target) && !event.target.matches('.user-button')) {
        userButtonMenu.style.display = 'none';
    }
});

function updateDateTime() {
    const datetimeElement = document.getElementById("datetime");
    const now = new Date();
    datetimeElement.textContent = formatDate(now); // Formatting date
}

function openPopup() {
    const popup = document.getElementById("popup");
    popup.style.display = "block";
}

function closePopup() {
    const popup = document.getElementById("popup");
    popup.style.display = "none";
}

function saveRequirements() {
    const cgpaInput = document.getElementById("cgpa");
    const cgpaError = document.getElementById("cgpaError");
    const cgpa = parseFloat(cgpaInput.value);

    if (isNaN(cgpa) || cgpa < 0 || cgpa > 10) {
        cgpaError.textContent = "CGPA must be between 0 and 10";
        return; // Prevent saving if the CGPA is out of range
    }

    // If the CGPA is within the valid range, proceed with saving
    cgpaError.textContent = ""; // Clear the error message
    console.log("Minimum CGPA requirement set to: " + cgpa);
    closePopup();
}

function viewRequirements() {
    const cgpa = /* Retrieve the CGPA requirement from your data/source */
    alert("Minimum CGPA Requirement: " + cgpa);
}

function toggleUserMenu() {
    const userButtonMenu = document.getElementById("userButtonMenu");
    userButtonMenu.style.display = (userButtonMenu.style.display === "block") ? "none" : "block";
}

// Close the user button menu if the user clicks outside of it
document.addEventListener('click', function (event) {
    const userButtonMenu = document.getElementById("userButtonMenu");
    const userProfile = document.querySelector('.user-profile');

    if (!userProfile.contains(event.target) && !event.target.matches(".user-button")) {
        userButtonMenu.style.display = "none";
    }
});

// For demo purposes, you can set user details when the page loads
window.onload = function () {
    const dropdownName = document.getElementById("userName");
    const dropdownEmail = document.getElementById("userEmail");
    dropdownName.textContent = "Company Name";
    dropdownEmail.textContent = "company@example.com";
}



const currentDescription = "This is a sample company description.";

// Function to open the edit description popup
function openEditDescriptionPopup() {
    const popup = document.getElementById("editDescriptionPopup");
    const descriptionInput = document.getElementById("companyDescription");
    
    // Populate the textarea with the current description
    descriptionInput.value = currentDescription;

    popup.style.display = "block";
}

// Function to close the edit description popup
function closeEditDescriptionPopup() {
    const popup = document.getElementById("editDescriptionPopup");
    popup.style.display = "none";
}

// Function to save the edited description
function saveDescription() {
    const descriptionInput = document.getElementById("companyDescription");
    const description = descriptionInput.value;

    // Save the description - Example: You might save it to a database here

    // For now, let's display the saved description in console
    console.log("Description saved:", description);

    // Close the popup after saving
    closeEditDescriptionPopup();
}


function navigateToApplied() {
    window.location.href = "/hr_dashboard/applied_candidates";
}

function navigateToEligible() {
    window.location.href = "/hr_dashboard/eligible_students";
}

function openEditCompanyDescription(){
    window.location.href = "/hr_dashboard/change_company_details";

}

function openEditInterviewDetails(){
    window.location.href = "/hr_dashboard/change_interview_details";

}

function TogglePower()
{
    window.location.href = "/hr_dashboard/toggle_power"
    
}

function navigateToScrutiny() {
    window.location.href = "/hr_dashboard/application_scrutiny";
}