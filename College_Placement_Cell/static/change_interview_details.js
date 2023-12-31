document.addEventListener("DOMContentLoaded", function () {
    tinymce.init({
        selector: '#editor',
        plugins: 'image link lists',
        menubar: 'edit view insert format table tools',
        toolbar: 'undo redo | styleselect | bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | numlist bullist outdent indent | link image | forecolor backcolor | removeformat',
        content_style: 'body { font-size: 16px; }',
    });

    const saveButton = document.getElementById('save-button');
    const contentInput = document.getElementById('content-input');

    saveButton.addEventListener('click', function (e) {
        const content = tinymce.get('editor').getContent();
        contentInput.value = content; // Update the hidden input field with the content

        // Create a FormData object to send the form data
        const formData = new FormData();
        formData.append('content', content);

        // Send the form data to the server
        fetch('/hr_dashboard/change_interview_details', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            // Handle the response from the server
            if (data.message === "Save Success") {
                // Show a "Save Success" popup
                alert("Save Success");

                // Automatically redirect to the company_hr_dashboard page
                window.location.href = '/company_hr_dashboard';
            }
        })
        .catch(error => {
            // Handle any errors that occur during the fetch request
            console.error('Error:', error);
        });
    });
});
