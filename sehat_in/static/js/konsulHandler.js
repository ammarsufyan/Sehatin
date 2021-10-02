// The variable that is passed are only for the api to works
// The backend process is handled in views.js

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
    console.log(title.replaceAll(' ', '-').replaceAll('?', ''));
    $.ajax({
        url: '/tanya-jawab/' + postid + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/delete',
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
                window.location.href = '/tanya-jawab';
            } else {
                alert("Error! Fail to delete post!" + dataJson.message);
            }
        }
    });
}

function deleteComment(logged_in, postid, title, commentId, csrf_token, mode) {
    /* delete comment, change comment counter and delete the comment on success, alert onfail */
    if (logged_in == "False") {
        alert('You must be logged in to delete a comment');
        return;
    }

    let isExecuted = confirm("Are you sure you want to delete this comment?");
    if (!isExecuted) {
        return;
    }

    // if mode admin ask for reason
    if (mode == 'admin') {
        let reason = prompt("Please enter the reason for deleting this comment");
        if (reason == null) { // cancel button pressed
            return;
        }
        if (reason == "") {
            alert("Please enter a valid reason!");
            return;
        } else
        if (reason.trim().length < 4) {
            alert("Reason too short! Min input length: 4 characters.");
            return;
        } else {
            $.ajax({
                url: '/tanya-jawab/' + postid + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/comment/' + commentId + '/delete',
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': csrf_token,
                    'mode': mode,
                    'reason': reason
                },
                success: function (data) {
                    dataJson = JSON.parse(data);
                    if (dataJson.status != 'error') {
                        $('#comments-' + commentId).remove();
                        $('#comment-counter').html(dataJson.message);
                    } else {
                        alert("Error! Fail to delete comment!" + dataJson.message);
                    }
                }
            });
        }
    } else {
        // Second confirmation
        isExecuted = confirm("Are you really sure you want to delete this comment?");
        if (!isExecuted) {
            return;
        }

        $.ajax({
            url: '/tanya-jawab/' + postid + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/comment/' + commentId + '/delete',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'mode': mode
            },
            success: function (data) {
                dataJson = JSON.parse(data);
                if (dataJson.status != 'error') {
                    $('#comments-' + commentId).remove();
                    $('#comment-counter').html(dataJson.message);
                } else {
                    alert("Error! Fail to delete comment!" + dataJson.message);
                }
            }
        });
    }
}
// global var to control the comment edit form
isOpen = false;

function editComment(logged_in, id, title, comment_id, csrf_token) {
    /* edit comment, on success comment will be updated on database, and client side page. On fail show alert popup -> shouldn't have failed in the first place but just in case */
    if (logged_in == "False") {
        alert('You must be logged in to edit a comment');
        return;
    }

    if(isOpen == true) {
        alert("You can only edit one comment at a time!");
        return;
    }

    // Make isOpen true
    isOpen = true;

    // Get values
    const valueDiv = document.getElementById('comment-' + comment_id);
    const value = valueDiv.innerHTML
    const toFillAfter = document.getElementById('fill-' + comment_id);
    
    // activate quill
    let quillEdit = new Quill('#comment-' + comment_id, {
        theme: 'snow',
        placeholder: 'Edit your comment...',
        modules: {
            toolbar: {
                container: myToolbar,
                handlers: {
                    image: imageHandler
                }
            }
        },
    });
    quillEdit.root.innerHTML = value.trim();

    // Function to deactiave quill and fill the div again
    function reset(div) {
        // Remove toolbar first
        $('.ql-toolbar').remove();

        // Remove the quill editor
        quillEdit.container.parentNode.removeChild(quillEdit.container)
        quillEdit.enable = false;
        quillEdit = null;

        // fill the div again
        toFillAfter.appendChild(div);

        isOpen = false;
    }

    // Appen a save button and cancel edit button
    const saveButton = document.createElement('button');
    saveButton.innerHTML = 'Save';
    saveButton.className = 'btn btn-save';
    saveButton.name = 'save';
    saveButton.onclick = function () {
        const newValue = quillEdit.root.innerHTML.trim();
        // check value
        if (newValue == '') {
            alert('Comment cannot be empty');
            return;
        }
        // check length
        if (newValue.length > 10000) {
            alert('Comment to long! Max character allowed including formatting are 10000 characters long');
        } else 
        if (newValue.length < 20) {
            alert('Comment too short! Min character allowed including formatting are 20 characters long');
        }

        $.ajax({
            url: '/tanya-jawab/' + id + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/comment/' + comment_id + '/edit',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'comment': newValue
            },
            success: function (data) {
                if (data == 'success') {
                    // Create the div again and append the value
                    var div = document.createElement('div');
                    div.innerHTML = newValue;
                    div.style = 'max-width: 800px;';
                    div.id = 'comment-' + comment_id;
                    reset(div);
                } else {
                    alert('Something went wrong, please try again');
                }
            }
        });
    }
    const cancelButton = document.createElement('button');
    cancelButton.innerHTML = 'Cancel';
    cancelButton.className = 'btn btn-cancel';
    cancelButton.name = 'cancel';
    cancelButton.onclick = function () {
        // Create the div again and append the value
        var div = document.createElement('div');
        div.innerHTML = value;
        div.style = 'max-width: 800px;';
        div.id = 'comment-' + comment_id;
        reset(div);
    }
    // Append the buttons to quill
    // button can also be styled -> for future reference
    valueDiv.appendChild(saveButton);
    valueDiv.appendChild(cancelButton);
}

function comment(logged_in, id, title, csrf_token) {
    /* comment, if success refresh page, if fail alert fail */
    if (logged_in == "False") {
        alert('You must be logged in to comment on a post');
        return;
    }

    // get the comment
    var myEditor = document.querySelector('#editor')
    var theComment = myEditor.children[0].innerHTML.trim();

    if (theComment.length < 20) {
        alert('Comment too short! Min character allowed including formatting are 20 characters long');
    } else
    if (theComment.length > 10000) {
        alert('Comment to long! Max character allowed including formatting are 10000 characters long');
    } else {
        $.ajax({
            url: '/tanya-jawab/' + id + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/comment',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'comment': theComment
            },
            success: function (data) {
                if (data == 'success') {
                    // Refresh the page
                    window.location.href = '/tanya-jawab/' + id + '/' + title.replaceAll(' ', '-').replaceAll('?', '');
                } else
                if (data == 'limit') {
                    alert('Character length invalid!')
                } else {
                    alert('There was an error posting your comment, try to refresh the page');
                }
            }
        });
    }
}