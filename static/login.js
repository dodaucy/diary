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


function login() {
    try {
        var password = document.getElementById("password").value.trim();
        if (password == "") {
            message_popup("Error", "Please enter a password", true);
            return;
        }
        disable(true);
        request(
            "POST",
            "login",
            function() {
                window.location.reload();
            },
            {
                password: password
            }
        );;
    } catch (error) {
        message_popup("JavaScript Error", error.toString(), true);
        console.error(error);
    }
}
