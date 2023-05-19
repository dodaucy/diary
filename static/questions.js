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
    reset_confirmations();
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
                var question_id = question.getElementsByClassName("i-id")[0].innerText;
                var text = question.getElementsByClassName("i-text")[0].value;
                var color = question.getElementsByClassName("i-color")[0].value;

                // Search for original question
                var found = false;
                var is_equal = false;
                for (var j = 0; j < original_questions.children.length; j++) {
                    var original_question = original_questions.children[j];
                    var original_question_id = original_question.getElementsByClassName("i-id")[0].innerText;

                    // If found
                    if (question_id == original_question_id) {
                        found = true;
                        // Check if equal
                        var original_text = original_question.getElementsByClassName("i-text")[0].value;
                        var original_color = original_question.getElementsByClassName("i-color")[0].value;
                        if (text == original_text && color == original_color) {
                            is_equal = true;
                        }
                        break;
                    }
                }

                if (!found) {
                    // Add new question
                    var new_id = await async_request(
                        "POST",
                        "new_question",
                        false,
                        {
                            "name": text,
                            "color": color
                        }
                    );
                    question.getElementsByClassName("i-id")[0].innerText = new_id.question_id;
                } else if (!is_equal) {
                    // Update question
                    await async_request(
                        "POST",
                        "update_question",
                        false,
                        {
                            "question_id": question_id,
                            "name": text,
                            "color": color
                        }
                    );
                }
            }

            // Check for deleted questions
            for (var i = 0; i < original_questions.children.length; i++) {
                var original_question = original_questions.children[i];
                var original_question_id = original_question.getElementsByClassName("i-id")[0].innerText;

                // Search for question
                var found = false;
                for (var j = 0; j < questions.children.length; j++) {
                    var question = questions.children[j];
                    var question_id = question.getElementsByClassName("i-id")[0].innerText;

                    // If found
                    if (question_id == original_question_id) {
                        found = true;
                        break;
                    }
                }

                if (!found) {
                    // Delete question
                    await async_request(
                        "POST",
                        "delete_question",
                        false,
                        {
                            "question_id": original_question_id
                        }
                    );
                }
            }

            return true;
        }
    );
}


function question_change_check() {
    reset_confirmations();

    // Check if questions have changed
    var questions = document.getElementById("questions");
    var changed = false;
    if (questions.children.length != original_questions.children.length) {
        changed = true;
    } else {
        for (var i = 0; i < questions.children.length; i++) {
            var question = questions.children[i];
            var original_question = original_questions.children[i];

            if (question.getElementsByClassName("i-text")[0].value != original_question.getElementsByClassName("i-text")[0].value) {
                changed = true;
                break;
            }

            if (question.getElementsByClassName("i-color")[0].value != original_question.getElementsByClassName("i-color")[0].value) {
                changed = true;
                break;
            }
        }
    }

    // Check if every question has a name
    var all_fields_filled = true;
    for (var i = 0; i < questions.children.length; i++) {
        var question = questions.children[i];
        if (question.getElementsByClassName("i-text")[0].value == "") {
            all_fields_filled = false;
            break;
        }
    }
    // Disable save button if not all fields are filled
    document.getElementById("save-popup-save").disabled = !all_fields_filled;

    show_save_popup(changed);
}


function remove_question(delete_button) {
    if (!confirm(delete_button)) {
        return;
    }
    var questions = document.getElementById("questions");
    questions.removeChild(delete_button.parentElement);
    question_change_check();
}


function add_questions() {
    var questions = document.getElementById("questions");

    var question = document.createElement("div");
    question.className = "full-line";

    var id = document.createElement("div");
    id.className = "i-id no-display";
    id.innerText = "new";
    question.appendChild(id);

    var text = document.createElement("input");
    text.type = "text";
    text.className = "i-text input-on-secondary-background flex-auto-scale can-be-disabled";
    text.maxLength = 255;
    text.placeholder = "Question";
    text.autocomplete = "off";
    question.appendChild(text);

    var generated_id = crypto.randomUUID();
    var generated_color = `#${Math.floor(Math.random() * 0xFFFFFF).toString(16)}`;

    var color_label = document.createElement("label");
    color_label.htmlFor = generated_id;
    color_label.className = "color-input";
    color_label.style.backgroundColor = generated_color;
    question.appendChild(color_label);

    var color = document.createElement("input");
    color.type = "color";
    color.id = generated_id;
    color.className = "i-color input-on-secondary-background can-be-disabled no-display";
    color.setAttribute("value", generated_color);
    color.setAttribute("oninput", "color_update(this);");
    color.autocomplete = "off";
    question.appendChild(color);

    var button = document.createElement("button");
    button.type = "button";
    button.className = "i-delete-button red-button can-be-disabled";
    button.innerText = "Delete";
    button.setAttribute("onclick", "remove_question(this);");
    question.appendChild(button);

    questions.appendChild(question);

    question_change_check();
}
