function markRead(notification_id, username, csrf_token) {
    $.ajax({
        url: "/profile/" + username + "/notification/read/" + notification_id,
        type: "POST",
        data: {csrfmiddlewaretoken: csrf_token},
        success: function(data) {
            dataJson = JSON.parse(data);
            if (dataJson.status == 'success') { 
                $('#notif-' + notification_id).css('background-color', 'white');
                $('#btn-notif-' + notification_id).remove();
            } else {
                alert("Error, failed to mark notification as read: ");
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
                if (dataJson.status == 'success') {
                    $('li[name*=\'notif-id\']').css('background-color', 'white');
                    $('button[name*=\'btn-notif-id\']').remove();
                } else {
                    alert("Error, failed to mark all notifications as read: ");
                }
            }
        });
    }
}