var original_settings;


function reset_original_data() {
    reset_confirmations();
    original_settings = document.getElementById("settings-box").cloneNode(true);
}


function init() {
    reset_original_data();
    save_popup_register_events(
        function() {
            document.getElementById("settings-box").innerHTML = original_settings.innerHTML;
            reset_confirmations();
        },
        async function() {
            // Read settings
            var settings = document.getElementById("settings-box");
            var data = {};
            for (var i = 0; i < settings.children.length; i++) {
                var setting = settings.children[i];
                data[setting.getElementsByTagName("label")[0].innerText.replace(/ /g, "_").toLowerCase()] = setting.getElementsByTagName("input")[0].value;
            }
            // Send request
            try {
                await async_request(
                    "POST",
                    "update_settings",
                    true,
                    data
                );
            } catch (error) {
                if (!error.toString().startsWith("Request Failed")) {
                    throw error;
                }
                return false;
            }
            // Load new settings
            var root = document.querySelector(":root");
            for (var key in data) {
                root.style.setProperty((`--${key}`).replace(/_/g, "-"), data[key]);
            }
            return true;
        }
    );
}


function reset_settings(element) {
    if (!confirm(element)) {
        return;
    }
    disable(true);
    request(
        "POST",
        "reset_settings",
        function() {
            location.reload();
        },
        function() {
            reset_confirmations();
            disable(false);
        }
    );
}


function logout(element) {
    if (!confirm(element)) {
        return;
    }
    disable(true);
    request(
        "POST",
        "logout",
        function() {
            location.href = "/";
        },
        function() {
            reset_confirmations();
            disable(false);
        }
    );
}


function settings_change_check() {
    reset_confirmations();
    var settings = document.getElementById("settings-box");

    // Loop through settings
    var changed = false;
    for (var i = 0; i < settings.children.length; i++) {
        var setting = settings.children[i];
        var original_setting = original_settings.children[i];

        // Check if value changed
        var original_value = original_setting.getElementsByTagName("input")[0].value;
        var value = setting.getElementsByTagName("input")[0].value;
        if (value != original_value) {
            changed = true;
            break;
        }
    }

    show_save_popup(changed);
}
