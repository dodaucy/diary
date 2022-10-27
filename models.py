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


class NewQuestion(BaseModel):
    enabled: bool
    name: str
    color: str


class UpdateQuestion(BaseModel):
    question_id: int
    enabled: bool
    name: str
    color: str


class DeleteQuestion(BaseModel):
    question_id: int
