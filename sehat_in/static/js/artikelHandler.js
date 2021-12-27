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
        alert("Anda harus masuk untuk mengubah post!");
        return;
    }
    window.location.href = '/artikel/' + id + '/' + title.replaceAll(' ', '-').replaceAll('?', '') + '/edit';
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
    let confirmTitle = prompt("Tolong masukkan judul postnya untuk konfirmasi penghapusan:");
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
                alert("Sukses menghapus artikel!");
                window.location.href = '/artikel';
            } else {
                alert("Error! Gagal menghapus post!" + dataJson.message);
            }
        }
    });
}