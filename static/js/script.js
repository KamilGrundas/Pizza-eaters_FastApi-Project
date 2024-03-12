document.getElementById('editCommentForm').addEventListener('submit', function(e) {
    e.preventDefault();

    var form = this;
    var commentText = document.getElementById('text').value;

    // Fetch API to send a PUT request
    fetch('/wizards/pictures/{{ context['comment'].picture_id }}/comments/{{ context['comment'].picture_comment_id }}', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            // Include other headers as required, like authorization tokens
        },
        body: JSON.stringify({
            text: commentText,
            // Include other properties of CommentBase as required
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        // Handle success, e.g., redirect or update the UI
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle errors, e.g., show a message to the user
    });
});