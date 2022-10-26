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


function disable(disable_elements) {
    var elements = document.getElementsByClassName("can-be-disabled");
    for (var i = 0; i < elements.length; i++) {
        elements[i].disabled = disable_elements;
    }
}
