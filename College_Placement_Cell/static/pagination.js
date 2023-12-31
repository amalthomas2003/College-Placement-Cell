// Initialize page number
var nextPageNumber = 2;  // Start with page 2 as the first page is already loaded

// Function to fetch and append more questions when scrolling to the bottom
$(window).scroll(function () {
    if ($(window).scrollTop() + $(window).height() >= $(document).height() - 100) {
        console.log('Reached bottom of the page. Fetching more questions...');
        // Fetch the next set of questions
        fetchNextQuestions();
    }
});

// Function to fetch the next set of questions from the server
function fetchNextQuestions() {
    console.log('Fetching questions for page:', nextPageNumber);
    // Implement logic to fetch and append more questions
    $.ajax({
        type: 'GET',
        url: '/student_dashboard/view_questions',
        data: { page: nextPageNumber },  // Pass the current page number to the server
        success: function (response) {
            console.log('Received response from the server:', response);
            // Append the new questions to the questions container
            $('#questions-container').append(response);
            nextPageNumber++;  // Increment the page number for the next request
        },
        error: function (error) {
            console.error('Error fetching questions:', error);
        }
    });
}
