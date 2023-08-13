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


function restore_question() {
    disable(true);
    var question_id = parseInt(document.getElementById("restore-question-id").value.trim());
    if (isNaN(question_id)) {
        message_popup("Error", "Please enter a valid question ID", true);
        disable(false);
        return;
    }
    request(
        "POST",
        "new_question",
        function() {
            message_popup("Success", "Question restored", false);
            document.getElementById("restore-question-id").value = "";
            disable(false);
        },
        function() {
            disable(false);
        },
        {
            question_id: question_id,
            name: "Restored Question",
            color: generate_color()
        }
    );
}


function logout_all_sessions(element) {
    if (!confirm(element)) {
        return;
    }
    disable(true);
    request(
        "POST",
        "logout_all",
        function() {
            location.href = "/";
        },
        function() {
            reset_confirmations();
            disable(false);
        }
    );
}
