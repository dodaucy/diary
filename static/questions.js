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


var original_questions;


function reset_original_data() {
    original_questions = document.getElementById("questions").cloneNode(true);
}


function init() {
    reset_original_data();
    save_popup_register_events(
        function() {
            document.getElementById("questions").innerHTML = original_questions.innerHTML;
        },
        async function() {
            var questions = document.getElementById("questions");
            for (var i = 0; i < questions.children.length; i++) {
                var question = questions.children[i];
                var question_id = question.getElementsByClassName("i_id")[0].innerText;
                var text = question.getElementsByClassName("i_text")[0].value;
                var color = question.getElementsByClassName("i_color")[0].value;

                // Search for original question
                var found = false;
                var is_equal = false;
                for (var j = 0; j < original_questions.children.length; j++) {
                    var original_question = original_questions.children[j];
                    var original_question_id = original_question.getElementsByClassName("i_id")[0].innerText;

                    // If found
                    if (question_id == original_question_id) {
                        found = true;
                        // Check if equal
                        var original_text = original_question.getElementsByClassName("i_text")[0].value;
                        var original_color = original_question.getElementsByClassName("i_color")[0].value;
                        if (text == original_text && color == original_color) {
                            is_equal = true;
                        }
                        break;
                    }
                }

                if (!found) {
                    // Add new question
                    var new_id = await sync_request(
                        "POST",
                        "new_question",
                        {
                            "name": text,
                            "color": color,
                            "enabled": true
                        }
                    );
                    question.getElementsByClassName("i_id")[0].innerText = new_id.question_id;
                } else if (!is_equal) {
                    // Update question
                    await sync_request(
                        "POST",
                        "update_question",
                        {
                            "question_id": question_id,
                            "name": text,
                            "color": color,
                            "enabled": true
                        }
                    );
                }
            }

            // Check for deleted questions
            for (var i = 0; i < original_questions.children.length; i++) {
                var original_question = original_questions.children[i];
                var original_question_id = original_question.getElementsByClassName("i_id")[0].innerText;

                // Search for question
                var found = false;
                for (var j = 0; j < questions.children.length; j++) {
                    var question = questions.children[j];
                    var question_id = question.getElementsByClassName("i_id")[0].innerText;

                    // If found
                    if (question_id == original_question_id) {
                        found = true;
                        break;
                    }
                }

                if (!found) {
                    // Delete question
                    await sync_request(
                        "POST",
                        "delete_question",
                        {
                            "question_id": original_question_id
                        }
                    );
                }
            }
        }
    );
}


function question_change_check() {
    var questions = document.getElementById("questions");
    var changed = false;

    if (questions.children.length != original_questions.children.length) {
        changed = true;
    } else {
        for (var i = 0; i < questions.children.length; i++) {
            var question = questions.children[i];
            var original_question = original_questions.children[i];

            if (question.getElementsByClassName("i_text")[0].value != original_question.getElementsByClassName("i_text")[0].value) {
                changed = true;
                break;
            }

            if (question.getElementsByClassName("i_color")[0].value != original_question.getElementsByClassName("i_color")[0].value) {
                changed = true;
                break;
            }
        }
    }

    show_save_popup(changed);
}


function removeQuestion(element) {
    var questions = document.getElementById("questions");
    questions.removeChild(element);
    question_change_check();
}


function addQuestions() {
    var questions = document.getElementById("questions");

    var question = document.createElement("div");
    question.className = "modified-flex-container";

    var id = document.createElement("div");
    id.className = "i_id no-display";
    id.innerText = "new";
    question.appendChild(id);

    var text = document.createElement("input");
    text.type = "text";
    text.className = "i_text input-on-secondary-background flex-auto-scale can-be-disabled";
    text.placeholder = "Question";
    question.appendChild(text);

    var color = document.createElement("input");
    color.type = "color";
    color.className = "i_color input-on-secondary-background can-be-disabled";
    color.value = `#${Math.floor(Math.random() * 0xFFFFFF).toString(16)}`;
    question.appendChild(color);

    var button = document.createElement("button");
    button.type = "button";
    button.className = "button red-button can-be-disabled";
    button.innerText = "Delete";
    button.addEventListener("click", function() {
        removeQuestion(question);
    });
    question.appendChild(button);

    questions.appendChild(question);
}
