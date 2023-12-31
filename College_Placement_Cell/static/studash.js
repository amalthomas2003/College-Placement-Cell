function logout() {
    alert("Logout clicked!");  
    window.location.href = '/student_dashboard/logout';
}

function redirectToEligibleCompanies() {
    // Perform form submission or other actions if needed

    // Redirect to the desired page
    window.location.href = '/student_dashboard/eligible_companies';
}

function redirectToPostInterviewQuestions() {
    // Perform form submission or other actions if needed

    // Redirect to the desired page
    window.location.href = '/student_dashboard/post_questions';
}

function redirectToViewInterviewQuestions() {
    // Perform form submission or other actions if needed

    // Redirect to the desired page
    window.location.href = '/student_dashboard/view_questions';
}

function redirectToViewResults(){
    window.location.href = '/student_dashboard/view_result'
}

function redirectToViewMyQuestions(){
    window.location.href = '/student_dashboard/view_my_questions'
}

// Ripple btn
const rippleButtons = document.querySelectorAll(".btn1--ripple");

rippleButtons.forEach(button => {
    button.addEventListener("mouseover", function (e) {
        let x = e.clientX - e.target.offsetLeft;
        let y = e.clientY - e.target.offsetTop;
        let ripples = document.createElement("span");
        ripples.style.left = x + "px";
        ripples.style.top = y + "px";
        this.appendChild(ripples);

        setTimeout(() => {
            ripples.remove();
        }, 1000);
    });
});
