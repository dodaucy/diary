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


function request(method, url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.onerror = function() {
        alert("Network error");
    }
    xhr.onload = function() {
        if (xhr.status == 200) {
            callback(JSON.parse(xhr.responseText));
        } else {
            alert("Error: " + xhr.status);
        }
    }
    xhr.send();
}


function disable(disable_elements) {
    var elements = document.getElementsByClassName("can-be-disabled");
    for (var i = 0; i < elements.length; i++) {
        elements[i].disabled = disable_elements;
    }
}
