// The variable that is passed are only for the api to works
// The backend process is handled in views.js
// Quill
var myToolbar = [
    ['bold', 'italic', 'underline', 'strike'],       
    ['blockquote', 'code-block'],

    [{ 'color': [] }, { 'background': [] }],         
    [{ 'font': [] }],
    [{ 'align': [] }],

    ['clean'],                                        
    ['image']
];

function imageHandler() {
    var range = this.quill.getSelection();
    var value = prompt('please copy paste the image url here.');
    if (value == "") { // If empty value
        return;
    }

    // verify the url, must be an image and a https image
    if (value.startsWith('https://') && (value.endsWith('.png') || value.endsWith('.jpg') || value.endsWith('.jpeg'))) {
        this.quill.insertEmbed(range.index, 'image', value, Quill.sources.USER);
    } else {
        // Check if img is http
        if (value.startsWith('http://')) {
            alert('Image linked needs to be secured (HTTPS)!');
        } else {
            alert('Invalid linked image! Image must be a png, jpg or jpeg!');
        }
    }
}

function editPost(logged_in, id, title) {
    /* edit post, move page to edit page */
    if (logged_in == "False") {
        alert("You must be logged in to edit a post");
        return;
    }
    window.location.href = '/artikel/' + id + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/edit';
}

function deletePost(logged_in, postid, title, csrf_token, mode) {
    /* delete post, alert post has been deleted successfully and redirect to post lists on success, alert fail otherwise */
    if (logged_in == "False") {
        alert('You must be logged in to delete a comment');
        return;
    }

    let isExecuted = confirm("Are you sure you want to delete this post?");
    if (!isExecuted) {
        return;
    }

    let reason = "";
    // Admin prompt for reason
    if (mode == 'admin') {
        // prompt for reason
        reason = prompt("Please enter a reason for deleting this post:");
        if (reason == null) { // cancel button pressed
            return;
        }
        if (reason == "") {
            alert("Please enter a reason for deleting this post!");
            return;
        }
        if (reason.length < 4) {
            alert("Invalid Reason Length! Must be between 4 and 200 characters!");
            return;
        }
    }

    // prompt for the title
    let confirmTitle = prompt("Please enter the title of the post to confirm deletion:");
    if (confirmTitle == null) { // cancel button pressed
        return;
    }
    if (confirmTitle == "") {
        alert("Please enter the title of the post to confirm deletion!");
        return;
    }
    if (confirmTitle.trim() != title) {
        alert("The title you entered does not match the title of the post!");
        return;
    }

    $.ajax({
        url: '/artikel/' + postid + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/delete',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token,
            'mode': mode,
            'reason': reason.trim()
        },
        success: function (data) {
            dataJson = JSON.parse(data);
            if (dataJson.status == 'success') {
                alert("Post has been deleted successfully!");
                window.location.href = '/artikel';
            } else {
                alert("Error! Fail to delete post!" + dataJson.message);
            }
        }
    });
}