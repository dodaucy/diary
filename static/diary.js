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


var last_load;
var last_date;


function disable(disable_elements) {
    var elements = document.getElementsByClassName("can-be-disabled");
    for (var i = 0; i < elements.length; i++) {
        elements[i].disabled = disable_elements;
    }
}


function loadDiary() {
    var date = document.getElementById("date").value;

    // Spam protection
    if (date == last_date) {
        return;
    }
    disable(true);
    if (!!last_load) {
        if (Date.now() - last_load < 1000) {
            setTimeout(function(){
                loadDiary();
            }, 500)
            return;
        }
    }
    last_load = Date.now();
    last_date = date

    // Verify date
    var year = date.split("-")[0];
    if (1970 > year || year > 6000) {
        return;
    }

    // Load diary
    if (date) {
        get("/diary?date=" + date, function(diary) {
            document.getElementById("notes").value = diary.notes;
            var children = document.getElementById("questions").children;
            for (var i = 0; i < children.length; i++) {
                var select = children[i].getElementsByTagName("select")[0];
                if (select.name in diary.answers) {
                    select.value = diary.answers[select.name];
                } else {
                    select.value = "0";
                }
            }
            disable(false);
        });
    }
}
