from typing import Dict, Optional

from pydantic import BaseModel


class Login(BaseModel):
    password: str


class DiaryEntry(BaseModel):
    date: str
    notes: str
    answers: Dict[int, int]


class NewQuestion(BaseModel):
    question_id: Optional[int]
    name: str
    color: str


class UpdateQuestion(BaseModel):
    question_id: int
    name: str
    color: str


class DeleteQuestion(BaseModel):
    question_id: int


class Settings(BaseModel):
    font_color: str
    button_font_color: str
    primary_background_color: str
    secondary_background_color: str
    nav_selected_item_color: str
    font_family: str
