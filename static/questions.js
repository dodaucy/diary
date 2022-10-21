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


function removeQuestion(element) {
    var questions = document.getElementById("questions");
    questions.removeChild(element);
}

function addQuestions() {
    var questions = document.getElementById("questions");
    var uuid = crypto.randomUUID();

    var question = document.createElement("div");
    question.className = "one-line";

    var input_field = document.createElement("input");
    input_field.type = "text";
    input_field.name = `new_name_${uuid}`;
    input_field.placeholder = "Question";
    input_field.required = true;
    question.appendChild(input_field);

    var color_field = document.createElement("input");
    color_field.type = "color";
    color_field.name = `new_color_${uuid}`;
    color_field.value = `#${Math.floor(Math.random() * 0xFFFFFF).toString(16)}`;
    color_field.required = true;
    question.appendChild(color_field);

    var button = document.createElement("button");
    button.type = "button";
    button.innerText = "Delete";
    button.addEventListener("click", function() {
        questions.removeChild(question);
    });
    question.appendChild(button);

    questions.appendChild(question);
}
