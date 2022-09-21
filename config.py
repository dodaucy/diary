
######################################
#                                    #
#               diary                #
#                                    #
#                MIT                 #
#     Copyright (C) 2022 dodaucy     #
#  https://github.com/dodaucy/diary  #
#                                    #
######################################


import yaml
from munch import munchify


with open("config.yml", "r") as f:
    config = munchify(yaml.safe_load(f))
