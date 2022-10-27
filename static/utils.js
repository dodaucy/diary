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


function show_save_popup(show) {
    var popup = document.getElementById("save-popup");
    var counter = 0;
    var position = 0;
    var timer = setInterval(function() {
        counter += 1;
        if (show) {
            popup.style.display = "flex";
            if (counter <= 10) {
                position -= (11 - counter) * 3;
            } else if (counter <= 20) {
                position += counter - 10;
            } else {
                clearInterval(timer);
                return;
            }
            popup.style.transform = `translate(-50%, ${position + 110}px)`;
        } else {
            if (counter <= 10) {
                position -= 11 - counter
            } else if (counter <= 20) {
                position += (counter - 10) * 3;
            } else {
                popup.style.display = "none";
                clearInterval(timer);
                return;
            }
            popup.style.transform = `translate(-50%, ${position}px)`;
        }
    }, 20);
}


function disable(disable_elements) {
    var elements = document.getElementsByClassName("can-be-disabled");
    for (var i = 0; i < elements.length; i++) {
        elements[i].disabled = disable_elements;
    }
}
