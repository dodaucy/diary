var save_popup_shown = false;
var front_end_disabled = false;

var save_popup_reset_click = function() {
    console.log("Save popup reset click not registered");
}
var save_popup_save_click = function() {
    console.log("Save popup save click not registered");
}

var x_down = null;


function message_popup(title, message, error) {
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
        removing = true;
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
    title_element.innerText = title;

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
        popup.style.backgroundColor = "var(--light-red)";
        progress_bar_background.className += " message-popup-progress-bar-background-red";
    } else {
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
        var success = await on_save();
        disable(false);
        if (success) {
            reset_original_data();
            show_save_popup(false);
        } else {
            document.getElementById("save-popup-save").innerText = "Save Changes";
        }
    }
    // Warn user if they try to leave the page without saving
    window.onbeforeunload = function() {
        if (save_popup_shown && !front_end_disabled) {
            return "You have unsaved changes. Are you sure you want to leave?";
        }
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


function show_reload_popup(show, text) {
    var popup = document.getElementById("reload-popup")
    var save_popup_save = document.getElementById("save-popup-save")
    if (show) {
        popup.style.display = "flex";
        document.getElementById("reload-popup-text").innerText = text;
        front_end_disabled = true;
        if (save_popup_save) {
            save_popup_save.innerText = "Save Changes";
        }
    } else {
        popup.style.display = "none";
    }
    document.getElementById("content").style.filter = show ? "blur(2px)" : "none";
    if (save_popup_save) {
        document.getElementById("save-popup").style.filter = show ? "blur(2px)" : "none";
    }
    document.getElementById("hamburger-menu").style.filter = show ? "blur(2px)" : "none";
    document.getElementById("hamburger-menu-nav").style.filter = show ? "blur(2px)" : "none";
}


function show_hamburger_menu(show) {
    // Prevent from double clicking
    if (document.getElementById("hamburger-menu").style.display == "flex" && show) {
        return;
    }
    // Show or hide background
    document.getElementById("hamburger-menu-background").style.display = show ? "block" : "none";
    // Show or hide hamburger menu with animation
    var popup = document.getElementById("hamburger-menu");
    var position = 0;
    var timer = setInterval(function() {
        popup.style.display = "flex";
        if (position < 80) {
            position += 10;
        } else {
            position += 3;
        }
        if (show) {
            popup.style.transform = `translate(${Math.min(0, -100 + position)}%, 0)`;
        } else {
            popup.style.transform = `translate(${Math.max(-100, -position)}%, 0)`;
        }
        if (position >= 100) {
            if (!show) {
                popup.style.display = "none";
            }
            clearInterval(timer);
        }
    }, 20);
}


function handle_touch_start(event) {
    if (window.innerWidth <= 600 && document.getElementById("hamburger-menu") != null) {
        x_down = event.touches[0].clientX;
    }
}


function handle_touch_move(event) {
    if (!x_down) {
        return;
    }
    var x_up = event.touches[0].clientX;
    var x_diff = x_down - x_up;
    if (x_diff > 0) {
        show_hamburger_menu(false);
    } else {
        show_hamburger_menu(true);
    }
    x_down = null;
}


function request(method, url, success_callback, error_callback, data) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, `/api/${url}`, true);
    xhr.onerror = function() {
        message_popup("Request Failed", "Network Error", true);
        show_reload_popup(true, "Network Error");
    }
    xhr.onload = function() {
        if (xhr.status == 200) {
            success_callback(JSON.parse(xhr.responseText));
        } else if (xhr.status == 204) {
            success_callback();
        } else {
            try {
                var response = JSON.parse(xhr.responseText);
                if (typeof response.detail !== "string") {
                    throw new Error();
                }
                if (xhr.status == 401 && response.detail == "Not logged in") {
                    location.href = "/";
                    return;
                }
                var msg = response.detail;
            } catch (e) {
                var msg = `Status Code ${xhr.status}`;
            }
            message_popup("Request Failed", msg, true);
            if (xhr.status >= 400 && xhr.status < 500) {
                error_callback(msg);
            } else {
                show_reload_popup(true, msg);
            }
        }
    }
    if (data === undefined) {
        xhr.send();
    } else {
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify(data));
    }
}


function async_request(method, url, throw_error, data) {
    return new Promise(function(resolve, reject) {
        request(
            method,
            url,
            function(response) {
                resolve(response);
            },
            function(error_message) {
                if (throw_error) {
                    reject(`Request Failed: ${error_message}`);
                } else {
                    show_reload_popup(true, error_message);
                }
            },
            data
        );
    });
}


function disable(disable_elements) {
    var elements = document.getElementsByClassName("can-be-disabled");
    for (var i = 0; i < elements.length; i++) {
        elements[i].disabled = disable_elements;
        if (elements[i].className.includes("color-input")) {
            elements[i].style.cursor = disable_elements ? "not-allowed" : "pointer";
        }
    }
}


function confirm(element) {
    if (!element.className.includes("confirm-button")) {
        element.className = element.className.replace("red-button", "confirm-button");
        element.innerText += "???";
        return false
    }
    return true;
}


function reset_confirmations() {
    var elements = Array.from(document.getElementsByClassName("confirm-button"));
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        element.className = element.className.replace("confirm-button", "red-button");
        element.innerText = element.innerText.replace("???", "");
    }
}


function color_update(element) {
    element.parentElement.getElementsByClassName("color-input")[0].style.backgroundColor = element.value;
    element.setAttribute("value", element.value);
}


function generate_color() {
    return `#${Math.floor(Math.random() * 0xFFFFFF).toString(16)}`;
}


function update_select_input(select_input) {
    for (var i = 0; i < select_input.children.length; i++) {
        var option = select_input.children[i];
        if (option.value == select_input.value) {
            option.setAttribute("selected", "selected");
        } else {
            option.removeAttribute("selected");
        }
    }
}


function init_utils(){
    // Catch all errors
    window.onerror = function(message, source, lineno, colno, error) {
        message_popup("JavaScript Error", message, true);
        console.error(error);
        return true;
    }
    // Update HTML on value change
    var text_inputs = document.querySelectorAll("input[type=text]");
    for (var i = 0; i < text_inputs.length; i++) {
        var text_input = text_inputs[i];
        text_input.setAttribute("oninput", "this.setAttribute('value', this.value);");
    }
    var select_inputs = document.querySelectorAll("select");
    for (var i = 0; i < select_inputs.length; i++) {
        var select_input = select_inputs[i];
        select_input.setAttribute("onchange", "update_select_input(this);");
    }
    // Add touch events
    document.addEventListener("touchstart", handle_touch_start, false);
    document.addEventListener("touchmove", handle_touch_move, false);
}
