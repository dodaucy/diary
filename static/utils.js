/*
#############################################
#                                           #
#                   diary                   #
#                                           #
#                    MIT                    #
#     Copyright (C) 2022 - 2023 dodaucy     #
#     https://github.com/dodaucy/diary      #
#                                           #
#############################################
*/


var save_popup_shown = false;
var save_popup_reset_click = function() {
    console.log("Save popup reset click not registered");
}
var save_popup_save_click = function() {
    console.log("Save popup save click not registered");
}


function message_popup(message, error) {
    /* Create popup */
    var popup = document.createElement("div");
    popup.className = "message-popup";
    popup.style.opacity = 0;

    /* Prepare remove function */
    var removing = false;
    var remove = function() {
        if (removing) {
            return;
        }
        var count = 0;
        var interval = setInterval(function() {
            count += 0.1;
            popup.style.opacity = 1 - count;
            if (count >= 1) {
                clearInterval(interval);
                popup.remove();
            }
        }, 50);
    }

    /* Create title element */
    var title_element = document.createElement("div");
    title_element.className = "message-popup-title";

    /* Set message */
    var message_element = document.createElement("p");
    message_element.innerText = message;

    /* Create progress bar */
    var progress_bar_background = document.createElement("div");
    progress_bar_background.className = "message-popup-progress-bar-background";
    var progress_bar = document.createElement("div");
    progress_bar.className = "message-popup-progress-bar";

    /* Set title and color depending on if it's an error or not */
    if (error) {
        title_element.innerText = "An error has occured";
        popup.style.backgroundColor = "var(--light-red)";
        progress_bar_background.className += " message-popup-progress-bar-background-red";
    } else {
        title_element.innerText = "Success";
        popup.style.backgroundColor = "var(--light-green)";
        progress_bar_background.className += " message-popup-progress-bar-background-green";
    }

    /* Delete popup after clicking on it */
    popup.onclick = remove;

    /* Append elements to popup */
    popup.appendChild(title_element);
    popup.appendChild(message_element);
    popup.appendChild(progress_bar_background);
    popup.appendChild(progress_bar);

    /* Add popup to message container */
    document.getElementById("message-container").appendChild(popup);

    /* Show slow */
    var counter = 0;
    var timer = setInterval(function() {
        counter += 0.1;
        popup.style.opacity = counter;
        if (counter >= 1) {
            clearInterval(timer);
        }
    }, 50);

    /* Remove after a few seconds */
    var cooldown = 0;
    var cooldown_interval = setInterval(function() {
        cooldown += 1;
        progress_bar.style.width = `${100 - cooldown / 20 * 100}%`;
        if (cooldown >= 20) {
            clearInterval(cooldown_interval);
            remove();
        }
    }, 250);
}


function save_popup_register_events(on_reset, on_save) {
    save_popup_reset_click = function() {
        on_reset();
        show_save_popup(false);
    }
    save_popup_save_click = async function() {
        document.getElementById("save-popup-save").innerText = "Saving...";
        disable(true);
        await on_save();
        disable(false);
        reset_original_data();
        show_save_popup(false);
    }
}


function show_save_popup(show) {
    if (show == save_popup_shown) {
        return;
    }
    save_popup_shown = show;

    var reset = document.getElementById("save-popup-reset");
    reset.onclick = null;
    var save = document.getElementById("save-popup-save");
    save.onclick = null;
    if (show) {
        save.innerText = "Save Changes";
    }

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
                reset.onclick = save_popup_reset_click;
                save.onclick = save_popup_save_click;
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


function request(method, url, callback, data) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, `/api/${url}`, true);
    xhr.onerror = function() {
        message_popup("Network Error", true);
    }
    xhr.onload = function() {
        if (xhr.status == 200) {
            callback(JSON.parse(xhr.responseText));
        } else if (xhr.status == 204) {
            callback();
        } else {
            try {
                var response = JSON.parse(xhr.responseText);
                if (typeof response.detail !== "string") {
                    throw new Error();
                }
                message_popup(response.detail, true);
            } catch (e) {
                message_popup(`Unknown Error (Status Code ${xhr.status})`, true);
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


function sync_request(method, url, data) {
    return new Promise(function(resolve, reject) {
        request(method, url, function(response) {
            resolve(response);
        }, data);
    });
}


function disable(disable_elements) {
    var elements = document.getElementsByClassName("can-be-disabled");
    for (var i = 0; i < elements.length; i++) {
        elements[i].disabled = disable_elements;
    }
}


function color_update(element) {
    element.parentElement.getElementsByClassName("color-input")[0].style.backgroundColor = element.value;
}


// Catch all errors
window.onerror = function(message, source, lineno, colno, error) {
    message_popup(message, true);
    console.error(error);
    return true;
}
