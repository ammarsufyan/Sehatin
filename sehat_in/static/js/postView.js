// The variable that is passed are only for the api to works
// The backend process is handled in views.js

function editPost(logged_in, id, title) {
    if (logged_in == "False") {
        alert("You must be logged in to edit a post");
        return;
    }
    window.location.href = '/post/' + id + '/' + title.replace(' ', '-')+ '/edit';
}

function likePost(logged_in, id, title, csrf_token) {
    if (logged_in == "False") {
        alert('You must be logged in to like a post');
        return;
    }
    
    $.ajax({
        url: '/post/' + id + '/' + title.replace(' ', '-') + '/like',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token
        },
        success: function (data) {
            dataJson = JSON.parse(data);
            if(dataJson.name != 'error') {
                $('#post-like-count').html(dataJson.likes);
                $('#post-liker').html(dataJson.names.join(', '));
            }
        }
    });
}

function deletePost(logged_in, id, title, csrf_token) {
    if (logged_in == "False") {
        alert('You must be logged in to delete a post');
        return;
    }
    
    $.ajax({
        url: '/post/' + id + '/' + title.replace(' ', '-') + '/delete',
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

function deleteComment(logged_in, postid, title, csrf_token, userid, mode) {
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
            url: '/post/' + postid + '/' + title.replace(' ', '-') + '/comment/' + userid + '/delete-adminmode',
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
            url: '/post/' + postid + '/' + title.replace(' ', '-') + '/comment/' + userid + '/delete',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_token
            },
            success: function (data) {
                // redirect from the backend, with message value of msg deleted or something
                // window.location.href = '/post/' + id + '/' + title.replace(' ', '-');
            }
        });
    }
}

function editComment(logged_in, id, title, csrf_token) {
    if (logged_in == "False") {
        alert('You must be logged in to edit a comment');
        return;
    }
    
    $.ajax({
        url: '/post/' + id + '/' + title.replace(' ', '-') + '/comment/' + id + '/edit',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token
        },
        success: function (data) {
            // edit comment
            // $('#comment-').html(data);
        }
    })
}

function likeComment(logged_in, id, title, csrf_token) {
    if (logged_in == "False") {
        alert('You must be logged in to like a comment');
        return;
    }

    $.ajax({
        url: '/post/' + id + '/' + title.replace(' ', '-') + '/comment/' + id + '/like',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token
        },
        success: function (data) {
            dataJson = JSON.parse(data);
            $('#comment-like-count-' + id).html(dataJson.likes);
            $('#comment-liker-' + id).html(dataJson.names.join(', '));
        }
    });
}

function comment(logged_in, id, title, csrf_token) {
    if (logged_in == "False") {
        alert('You must be logged in to comment on a post');
        return;
    }
    
    // get the comment
    var myEditor = document.querySelector('#editor')
    var theComment = myEditor.children[0].innerHTML

    if (theComment.length < 20 ) {
        alert('Your comment must be at least 20 characters long');
    } else {
        $.ajax({
            url: '/post/' + id + '/' + title.replace(' ', '-') + '/comment',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'comment': theComment
            },
            success: function (data) {
                if (data != 'error') {
                    // Refresh the page
                    window.location.href = '/post/' + id + '/' + title.replace(' ', '-');
                } else {
                    alert('There was an error posting your comment, try to refresh the page');
                }
            }
        });
    }
}