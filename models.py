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

from pydantic import BaseModel


class DiaryEntry(BaseModel):
    date: str
    notes: str
    answers: Dict[int, int]
