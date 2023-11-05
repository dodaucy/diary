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


var last_load;
var last_date;
var original_questions_list;
var original_notes;


function reset_original_data() {
    original_questions_list = document.getElementById("questions-list").cloneNode(true);
    original_notes = document.getElementById("notes").value;
}


function question_list_change_check() {
    var questions = document.getElementById("questions-list");
    if (document.getElementById("notes").value != original_notes) {
        changed = true;
    } else {
        var changed = false;
        for (var i = 0; i < questions.children.length; i++) {
            var question = questions.children[i];
            var original_question = original_questions_list.children[i];

            if (question.getElementsByTagName("select")[0].value != original_question.getElementsByTagName("select")[0].value) {
                changed = true;
                break;
            }
        }
    }
    document.getElementById("date").disabled = changed;
    show_save_popup(changed);
}


function load_diary() {
    var date = document.getElementById("date").value;

    // Spam protection
    if (date == last_date) {
        return;
    }
    disable(true);
    if (!!last_load) {
        if (Date.now() - last_load < 1000) {
            setTimeout(function(){
                load_diary();
            }, 500)
            return;
        }
    }
    last_load = Date.now();
    last_date = date

    // Verify date
    var year = date.split("-")[0];
    if (1970 > year || year > 6000) {
        message_popup("Invalid date", "Date out of range", true);
        document.getElementById("date").disabled = false;
        return;
    }

    // Load diary
    if (date) {
        request(
            "GET",
            `diary?date=${date}`,
            function(diary) {
                document.getElementById("notes").value = diary.notes;
                var children = document.getElementById("questions-list").children;
                for (var i = 0; i < children.length; i++) {
                    var select = children[i].getElementsByTagName("select")[0];
                    var id = select.id.split("-")[1];
                    if (id in diary.answers) {
                        select.value = diary.answers[id];
                    } else {
                        select.value = "0";
                    }
                    update_select_input(select);
                }
                disable(false);
                reset_original_data();
            },
            function() {}
        );
    }
}


function init() {
    save_popup_register_events(
        function() {
            document.getElementById("questions-list").innerHTML = original_questions_list.innerHTML;
            document.getElementById("notes").value = original_notes;
            document.getElementById("date").disabled = false;
        },
        async function() {
            var date = document.getElementById("date").value;
            var notes = document.getElementById("notes").value;
            var answers = {};
            var children = document.getElementById("questions-list").children;
            for (var i = 0; i < children.length; i++) {
                var select = children[i].getElementsByTagName("select")[0];
                answers[parseInt(select.id.split("-")[1])] = select.value;
            }
            await async_request(
                "POST",
                "update_diary_entry",
                false,
                {
                    "date": date,
                    "notes": notes,
                    "answers": answers
                }
            );
            return true;
        }
    )
    document.getElementById("date").value = (new Date()).toISOString().split("T")[0];
    load_diary();
}
