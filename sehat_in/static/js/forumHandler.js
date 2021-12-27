// The variable that is passed are only for the api to works
// The backend process is handled in views.js
// Quill
var myToolbar = [
    ['bold', 'italic', 'underline', 'strike'],       
    ['blockquote'],

    [{ 'color': [] }, { 'background': [] }],         
    [{ 'font': [] }],
    [{ 'align': [] }],

    ['clean'],                                        
    ['image']
];

function imageHandler() {
    var range = this.quill.getSelection();
    var value = prompt('Salin tautan gambar di sini!');
    if (value == "") { // If empty value
        return;
    }

    // verify the url, must be an image and a https image
    if (value.startsWith('https://') && (value.endsWith('.png') || value.endsWith('.jpg') || value.endsWith('.jpeg'))) {
        this.quill.insertEmbed(range.index, 'image', value, Quill.sources.USER);
    } else {
        // Check if img is http
        if (value.startsWith('http://')) {
            alert('Gambar yang ditautkan harus aman (HTTPS)!');
        } else {
            alert('Format tautan gambar invalid! Gambar harus berupa png, jpg, atau jpeg!');
        }
    }
}

function editPost(logged_in, id, title) {
    /* edit post, move page to edit page */
    if (logged_in == "False") {
        alert("Anda harus masuk untuk mengedit post!");
        return;
    }
    window.location.href = '/forum/' + id + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/edit';
}

var disableLikePost = false;
function likePost(logged_in, id, title, csrf_token) {
    /* like post, if success edit likes and liker, if fail alert fail */
    if (logged_in == "False") {
        alert('Anda harus masuk untuk menyukai post!');
        return;
    }
    // prevent user from spamming the button
    if (disableLikePost == true) {
        return;
    }
    disableLikePost = true;

    $.ajax({
        url: '/forum/' + id + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/like',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token
        },
        success: function (data) {
            dataJson = JSON.parse(data);
            $('#post-like-count').html(dataJson.likes);
        }
    });
    disableLikePost = false;
}

function deletePost(logged_in, postid, title, csrf_token, mode) {
    /* delete post, alert post has been deleted successfully and redirect to post lists on success, alert fail otherwise */
    if (logged_in == "False") {
        alert('Anda harus masuk untuk menghapus post!');
        return;
    }

    let isExecuted = confirm("Apakah anda yakin ingin menghapus post ini?");
    if (!isExecuted) {
        return;
    }

    let reason = "";
    // Admin prompt for reason
    if (mode == 'admin') {
        // prompt for reason
        reason = prompt("Tolong masukkan alasan penghapusan post:");
        if (reason == null) { // cancel button pressed
            return;
        }
        if (reason == "") {
            alert("Harap masukkan alasan yang valid!");
            return;
        }
        if (reason.length < 4 || reason.length > 200) {
            alert("Panjang alasan tidak valid! Harus sepanjang 4-200 karakter!");
            return;
        }
    }

    // prompt for the title
    let confirmTitle = prompt("Please enter the title of the post to confirm deletion:");
    if (confirmTitle == null) { // cancel button pressed
        return;
    }
    if (confirmTitle == "") {
        alert("Harap masukkan judul yang valid!");
        return;
    }
    if (confirmTitle.trim() != title) {
        alert("Judul yang anda masukkan tidak sesuai dengan judul postnya!");
        return;
    }

    $.ajax({
        url: '/forum/' + postid + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/delete',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token,
            'mode': mode,
            'reason': reason.trim()
        },
        success: function (data) {
            dataJson = JSON.parse(data);
            if (dataJson.status == 'success') {
                alert("Post berhasil dihapus!");
                window.location.href = '/forum';
            } else {
                alert("Error! Gagal menghapus post!" + dataJson.message);
            }
        }
    });
}

function reportPost(logged_in, postid, title, csrf_token) {
    /* report post, alert success on success, alert fail on failure */
    if (logged_in == "False") {
        alert('Anda harus masuk untuk melaporkan post!');
        return;
    }

    // Ask for confirmation
    if (!confirm("Apakah anda yakin ingin melaporan post ini?")) {
        return;
    }

    // Ask for reasons
    var reason = prompt("Tolong masukkan alasan untuk melaporkan post ini:");
    if (reason == null) { // cancel button pressed
        return;
    }
    if (reason == "") {
        alert("Anda harus memasukkan alasan pelaporan post ini.");
        return;
    }
    if (reason < 4 || reason > 200) {
        alert("Panjang alasan tidak valid! Harus sepanjang 4-200 karakter!");
        return;
    }

    $.ajax({
        url: '/forum/' + postid + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/report',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token,
            'reason': reason
        },
        success: function (data) {
            dataJson = JSON.parse(data);
            if (dataJson.status == 'success') {
                alert("Post berhasil dilaporkan! Terimakasih atas kontribusinya!");
            } else {
                alert("Error! Gagal untuk melaporkan post! " + dataJson.message);
            }
        }
    });
}

function reportComment(logged_in, postid, title, commentId, csrf_token) {
    /* report comment, alert success on success, alert fail on failure */
    if (logged_in == "False") {
        alert('Anda harus masuk untuk melaporkan komentar!');
        return;
    }

    // Ask for confirmation
    if (!confirm("Apakah anda yakin ingin melaporan komentar ini?")) {
        return;
    }

    // Ask for reasons
    var reason = prompt("Tolong masukkan alasan untuk melaporkan komentar ini:");
    if (reason == null) { // cancel button pressed
        return;
    }
    if (reason == "") {
        alert("Anda harus memasukkan alasan pelaporan komentar ini.");
        return;
    }
    if (reason < 4 || reason > 200) {
        alert("Panjang alasan tidak valid! Harus sepanjang 4-200 karakter!");
        return;
    }

    $.ajax({
        url: '/forum/' + postid + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/comment/' + commentId + '/report',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token,
            'reason': reason,
        },
        success: function (data) {
            dataJson = JSON.parse(data);
            if (dataJson.status == 'success') {
                alert("Komentar berhasil dilaporkan! Terimakasih atas kontribusinya!");
            } else {
                alert("Error! Gagal melaporkan komentar! " + dataJson.message);
            }
        }
    });
}

function deleteComment(logged_in, postid, title, commentId, csrf_token, mode) {
    /* delete comment, change comment counter and delete the comment on success, alert onfail */
    if (logged_in == "False") {
        alert('Anda harus masuk untuk menghapus komentar!');
        return;
    }

    let isExecuted = confirm("Apakah anda yakin ingin menghapus komentar ini?");
    if (!isExecuted) {
        return;
    }

    // if mode admin ask for reason
    if (mode == 'admin') {
        var reason = prompt("Tolong masukkan alasan penghapusan komentar ini:");
        if (reason == null) { // cancel button pressed
            return;
        }
        if (reason == "") {
            alert("Tolong masukkan alasan yang valid!");
            return;
        } else
        if (reason.trim().length < 4) {
            alert("Panjang alasan terlalu pendek! Panjang minimal: 4 karakter.");
            return;
        } else {
            $.ajax({
                url: '/forum/' + postid + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/comment/' + commentId + '/delete',
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
                        alert("Error! Gagal menghapus komentar!" + dataJson.message);
                    }
                }
            });
        }
    } else {
        // Second confirmation
        isExecuted = confirm("Apakah anda benar-benar yakin ingin menghapus komentar ini?");
        if (!isExecuted) {
            return;
        }

        $.ajax({
            url: '/forum/' + postid + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/comment/' + commentId + '/delete',
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
                    alert("Error! Gagal menghapus komentar!" + dataJson.message);
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
        alert('Anda harus masuk untuk mengubah komentar!');
        return;
    }

    if(isOpen == true) {
        alert('Anda hanya dapat mengubah satu komentar dalam satu waktu!');
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
        placeholder: 'Ubah komentar anda...',
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
            alert('Komentar terlalu panjang! Panjang maksimum termasuk pemformatan adalah 10000 karakter!');
        } else 
        if (newValue.length < 20) {
            alert('Komentar terlalu pendek! Panjang minimum termasuk pemformatan adalah 20 karakter!');
        }

        $.ajax({
            url: '/forum/' + id + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/comment/' + comment_id + '/edit',
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
                    div.className = "isi_forum";
                    reset(div);
                } else {
                    alert('Terjadi masalah, harap coba lagi.');
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
        div.className = "isi_forum";
        reset(div);
    }
    // Append the buttons to quill
    // button can also be styled -> for future reference
    valueDiv.appendChild(saveButton);
    valueDiv.appendChild(cancelButton);
}

var disableLikeComment = false;
function likeComment(logged_in, post_id, title, comment_id, csrf_token) {
    /* like comment, if success edit likes count, if fail alert fail */
    if (logged_in == "False") {
        alert('Anda harus masuk untuk menyukai komentar!');
        return;
    }
    // prevent user from spamming the button
    if (disableLikeComment == true) {
        return;
    }
    disableLikeComment = true;

    $.ajax({
        url: '/forum/' + post_id + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/comment/' + comment_id + '/like',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': csrf_token
        },
        success: function (data) {
            dataJson = JSON.parse(data);
            $('#comment-like-count-' + comment_id).html(dataJson.likes);
        }
    });
    disableLikeComment = false;
}

function comment(logged_in, id, title, csrf_token) {
    /* comment, if success refresh page, if fail alert fail */
    if (logged_in == "False") {
        alert('Anda harus masuk untuk meninggalkan komentar!');
        return;
    }

    // get the comment
    var myEditor = document.querySelector('#editor')
    var theComment = myEditor.children[0].innerHTML.trim();

    if (theComment.length < 20) {
        alert('Komentar terlalu pendek! Panjang minimum termasuk pemformatan adalah 20 karakter!');
    } else
    if (theComment.length > 10000) {
        alert('Komentar terlalu panjang! Panjang maksimum termasuk pemformatan adalah 10000 karakter!');
    } else {
        $.ajax({
            url: '/forum/' + id + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/comment',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrf_token,
                'comment': theComment
            },
            success: function (data) {
                if (data == 'success') {
                    // Refresh the page
                    window.location.href = '/forum/' + id + '/' + title.replaceAll(' ', '-').replaceAll('?', '');
                } else
                if (data == 'limit') {
                    alert('Panjang karakter tidak valid!')
                } else {
                    alert('Terjadi error saat memposting komentar anda, coba muat ulang halaman.');
                }
            }
        });
    }
}