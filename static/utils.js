/*
######################################
#                                    #
#               diary                #
#                                    #
#                MIT                 #
#     Copyright (C) 2022 dodaucy     #
#  https://github.com/dodaucy/diary  #
#                                    #
######################################
*/


function request(method, url, callback, data) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, `/api/${url}`, true);
    xhr.onerror = function() {
        alert("Network error");
    }
    xhr.onload = function() {
        if (xhr.status == 200) {
            callback(JSON.parse(xhr.responseText));
        } else if (xhr.status == 204) {
            callback();
        } else {
            try {
                var response = JSON.parse(xhr.responseText);
                alert(response.detail);
            } catch (e) {
                alert(`Unknown Error (Status Code ${xhr.status})`);
            }
        }
    }
    if (data === undefined) {
        xhr.send();
    } else {
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(data));
    }
}


function disable(disable_elements) {
    var elements = document.getElementsByClassName("can-be-disabled");
    for (var i = 0; i < elements.length; i++) {
        elements[i].disabled = disable_elements;
    }
}
