// The variable that is passed are only for the api to works
// The backend process is handled in views.js
// Quill
var myToolbar = [
    ['bold', 'italic', 'underline', 'strike'],
    ['blockquote', 'code-block'],

    [{
        'color': []
    }, {
        'background': []
    }],
    [{
        'font': []
    }],
    [{
        'align': []
    }],

    ['clean'],
    ['image']
];

function imageHandler() {
    var range = this.quill.getSelection();
    var value = prompt('please copy paste the image url here.');
    if (value) {
        this.quill.insertEmbed(range.index, 'image', value, Quill.sources.USER);
    }
}

function editPost(logged_in, id, title) {
    /* edit post, move page to edit page */
    if (logged_in == "False") {
        alert("You must be logged in to edit a post");
        return;
    }
    window.location.href = '/post/' + id + '/' + title.replaceAll(' ', '-') + '/edit';
}

function likePost(logged_in, id, title, csrf_token) {
    /* like post, if sucess edit likes and liker, if fail alert fail */
    if (logged_in == "False") {
        alert('You must be logged in to like a post');
        return;
    }

    $.ajax({
        url: '/post/' + id + '/' + title.replaceAll(' ', '-') + '/like',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token
        },
        success: function (data) {
            dataJson = JSON.parse(data);
            if (dataJson.names != 'error') {
                $('#post-like-count').html(dataJson.likes);
                $('#post-liker').html(dataJson.names.join(', '));
            } else {
                alert("Error! Fail to like post!");
            }
        }
    });
}

function deletePost(logged_in, id, title, csrf_token) {
    /* delete post, .. */
    if (logged_in == "False") {
        alert('You must be logged in to delete a post');
        return;
    }

    $.ajax({
        url: '/post/' + id + '/' + title.replaceAll(' ', '-') + '/delete',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token
        },
        success: function (data) {
            // redirect from the backend, with message value of post deleted or something
            // window.location.href = '/post';
        }
    });
}

function reportPost(logged_in, id, csrf_token) {
    /* report post, ... */
    if (logged_in == "False") {
        alert('You must be logged in to report a post');
        return;
    }

    $.ajax({
        url: '/report/post/' + id,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token
        },
        success: function (data) {
            // redirect from the backend, with message value of post deleted or something

        }
    });
}

function reportComment(logged_in, id, csrf_token) {
    /* report comment, ... */
    if (logged_in == "False") {
        alert('You need to login to report a comment');
        return;
    }

    $.ajax({
        url: '/report/comment/' + id,
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token
        },
        success: function (data) {

        }
    });
}

function deleteComment(logged_in, postid, title, userid, csrf_token, mode) {
    /* delete comment, ... */
    if (logged_in == "False") {
        alert('You must be logged in to delete a comment');
        return;
    }

    let isExecuted = confirm("Are you sure you want to delete this comment?");
    if (!isExecuted) {
        return;
    }
    if (mode == 'admin') {
        $.ajax({
            url: '/post/' + postid + '/' + title.replaceAll(' ', '-') + '/comment/' + userid + '/delete-adminmode',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_token
            },
            success: function (data) {
                // redirect from the backend, with message value of post deleted or something

            }
        });
    } else {
        $.ajax({
            url: '/post/' + postid + '/' + title.replaceAll(' ', '-') + '/comment/' + userid + '/delete',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_token
            },
            success: function (data) {
                // redirect from the backend, with message value of msg deleted or something
                // window.location.href = '/post/' + id + '/' + title.replaceAll(' ', '-');
            }
        });
    }
}

function editComment(logged_in, id, title, comment_id, csrf_token) {
    /* edit comment, on sucess comment will be updated on database, and client side page. On fail show alert popup -> shouldn't have failed in the first place but just in case */
    if (logged_in == "False") {
        alert('You must be logged in to edit a comment');
        return;
    }

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
            url: '/post/' + id + '/' + title.replaceAll(' ', '-') + '/comment/' + comment_id + '/edit',
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
        div.id = 'comment-' + comment_id;
        reset(div);
    }
    // Append the buttons to quill
    // button can also be styled -> for future reference
    valueDiv.appendChild(saveButton);
    valueDiv.appendChild(cancelButton);
}


function likeComment(logged_in, post_id, title, comment_id, csrf_token) {
    /* like comment, if sucess edit likes count, if fail alert fail */
    if (logged_in == "False") {
        alert('You must be logged in to like a comment');
        return;
    }

    $.ajax({
        url: '/post/' + post_id + '/' + title.replaceAll(' ', '-') + '/comment/' + comment_id + '/like',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token
        },
        success: function (data) {
            dataJson = JSON.parse(data);
            if (dataJson.names != 'error') {
                $('#comment-like-count-' + comment_id).html(dataJson.likes);
            } else {
                alert("Error! Fail to like comment!");
            }
        }
    });
}

function comment(logged_in, id, title, csrf_token) {
    /* comment, if sucess refresh page, if fail alert fail */
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
            url: '/post/' + id + '/' + title.replaceAll(' ', '-') + '/comment',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'comment': theComment
            },
            success: function (data) {
                if (data == 'success') {
                    // Refresh the page
                    window.location.href = '/post/' + id + '/' + title.replaceAll(' ', '-');
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