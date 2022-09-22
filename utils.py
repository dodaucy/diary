######################################
#                                    #
#               diary                #
#                                    #
#                MIT                 #
#     Copyright (C) 2022 dodaucy     #
#  https://github.com/dodaucy/diary  #
#                                    #
######################################


from typing import Dict

from config import config


def get_style() -> Dict[str, str]:
    return {
        "font_color": str(config.style.font_color),
        "background_color": str(config.style.background_color),
        "font_family": str(config.style.font_family)
    }
