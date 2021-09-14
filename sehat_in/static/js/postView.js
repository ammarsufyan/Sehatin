// The variable that is passed are only for the api to works
// The backend process is handled in views.js

function editPost(logged_in, id, title) {
    /* edit post, move page to edit page */
    if (logged_in == "False") {
        alert("You must be logged in to edit a post");
        return;
    }
    window.location.href = '/post/' + id + '/' + title.replaceAll(' ', '-')+ '/edit';
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
            if(dataJson.names != 'error') {
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

function deleteComment(logged_in, postid, title, csrf_token, userid, mode) {
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

function editComment(logged_in, id, title, csrf_token) {
    /* edit comment, ... */
    if (logged_in == "False") {
        alert('You must be logged in to edit a comment');
        return;
    }
    
    $.ajax({
        url: '/post/' + id + '/' + title.replaceAll(' ', '-') + '/comment/' + id + '/edit',
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
            if(dataJson.names != 'error') {
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
    var theComment = myEditor.children[0].innerHTML

    if (theComment.length < 20 ) {
        alert('Your comment must be at least 20 characters long');
    } else {
        $.ajax({
            url: '/post/' + id + '/' + title.replaceAll(' ', '-') + '/comment',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'comment': theComment
            },
            success: function (data) {
                if (data != 'error') {
                    // Refresh the page
                    window.location.href = '/post/' + id + '/' + title.replaceAll(' ', '-');
                } else {
                    alert('There was an error posting your comment, try to refresh the page');
                }
            }
        });
    }
}