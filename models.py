#############################################
#                                           #
#                   diary                   #
#                                           #
#                    MIT                    #
#     Copyright (C) 2022 - 2023 dodaucy     #
#     https://github.com/dodaucy/diary      #
#                                           #
#############################################


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


class Settings(BaseModel):
    font_color: str
    button_font_color: str
    primary_background_color: str
    secondary_background_color: str
    navbar_selected_item_color: str
    font_family: str
