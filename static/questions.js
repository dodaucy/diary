function removeQuestion(element) {
    var questions = document.getElementById("questions");
    questions.removeChild(element);
}

function addQuestions() {
    var questions = document.getElementById("questions");

    var question = document.createElement("div");
    question.className = "flex";

    var input_field = document.createElement("input");
    input_field.type = "text";
    input_field.name = "new";
    input_field.placeholder = "Question";
    input_field.required = true;
    question.appendChild(input_field);

    var button = document.createElement("button");
    button.type = "button";
    button.innerText = "Delete";
    button.addEventListener("click", function() {
        questions.removeChild(question);
    });
    question.appendChild(button);

    questions.appendChild(question);
}
