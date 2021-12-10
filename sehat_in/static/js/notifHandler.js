function markRead(notification_id, username, csrf_token) {
    $.ajax({
        url: "/profile/" + username + "/notification/read/" + notification_id,
        type: "POST",
        data: {csrfmiddlewaretoken: csrf_token},
        success: function(data) {
            dataJson = JSON.parse(data);
            if (dataJson.status != 'success') { 
                alert("Error saat membuka notifikasi!");
            }
        }
    });
}

function readAll(username, csrf_token) {
    // ask for confirmation

    if (confirm('Are you sure you want to mark all notifications as read?')) {
        $.ajax({
            url: "/profile/" + username + "/notification/readall",
            type: "POST",
            data: {csrfmiddlewaretoken: csrf_token},
            success: function(data) {
                dataJson = JSON.parse(data);
                if (dataJson.status != 'success') { 
                    alert("Error saat membuka notifikasi!");
                }
            }
        });
    }
}