function getStatusText(status) {
    if (status === 2) {
        return "Pending";
    } else if (status === 1) {
        return "Accepted";
    } else {
        return "Rejected";
    }
}

function changeStatus(questionId, newStatus) {
    // You can implement the logic to update the status on the server here
    console.log(`Changed status of question ${questionId} to ${getStatusText(newStatus)}`);
}
