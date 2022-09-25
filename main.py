######################################
#                                    #
#               diary                #
#                                    #
#                MIT                 #
#     Copyright (C) 2022 dodaucy     #
#  https://github.com/dodaucy/diary  #
#                                    #
######################################

# Load environment variables from config.env file
from dotenv import load_dotenv
load_dotenv("config.env")

import mimetypes
import os

import bcrypt
from fastapi import (Cookie, Depends, FastAPI, Form, HTTPException, Request,
                     status)
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

import utils
from globals import db
from settings import Settings

app = FastAPI(openapi_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

s = Settings()


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "settings": s.settings
        },
        exc.status_code
    )


@app.on_event("startup")
async def startup():
    mimetypes.init()
    mimetypes.add_type("image/webp", ".webp")
    await db.connect()
    await s.load()


@app.get("/")
async def index(request: Request, token: str = Cookie("")):
    # Create login page response
    login_response = templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "settings": s.settings
        }
    )
    if token:
        if await utils.is_logged_in(token):
            # Return diary page
            return templates.TemplateResponse(
                "diary.html",
                {
                    "request": request,
                    "settings": s.settings,
                    "questions": await db.fetch_all("SELECT id, name FROM questions WHERE enabled = 1")
                }
            )
        # Delete session cookie
        login_response.delete_cookie(
            key="token",
            httponly=True
        )
    # Return the login page
    return login_response


@app.get("/diary", dependencies=[Depends(utils.login_check)])
async def get_diary(date: str):
    days = utils.get_days(date)
    # Fetch notes
    notes = await db.fetch_val(
        "SELECT notes FROM notes WHERE days = :days",
        {
            "days": days
        }
    )
    # Fetch answers
    fetched_answers = await db.fetch_all(
        "SELECT question_id, value FROM answers WHERE days = :days",
        {
            "days": days
        }
    )
    # Format answers
    answers = {}
    for answer in fetched_answers:
        answers[str(answer["question_id"])] = str(answer["value"])
    # Return diary data
    return {
        "notes": notes or "",
        "answers": answers
    }


@app.post("/login")
async def login(password: str = Form(...)):
    # Verify password
    if not bcrypt.checkpw(password.strip().encode(), os.getenv("PASSWORD_HASH").encode()):
        return RedirectResponse(
            url="/",
            status_code=status.HTTP_303_SEE_OTHER
        )
    # Create a session
    token = os.urandom(32).hex()
    await db.execute(
        "INSERT INTO sessions (token) VALUES (:token)",
        {
            "token": token
        }
    )
    # Redirect to the index page
    response = RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER
    )
    response.set_cookie(
        key="token",
        value=token,
        httponly=True
    )
    return response


@app.post("/logout")
async def logout(token: str = Cookie("")):
    # Delete the session
    if token:
        await db.execute(
            "DELETE FROM sessions WHERE token = :token",
            {
                "token": token
            }
        )
    # Redirect to the login page
    response = RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER
    )
    response.delete_cookie(
        key="token",
        httponly=True
    )
    return response


@app.get("/settings", dependencies=[Depends(utils.login_check)])
async def settings(request: Request):
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "settings": s.settings
        }
    )


@app.post("/update_settings", dependencies=[Depends(utils.login_check)])
async def set_settings(font_color: str = Form(...), background_color: str = Form(...), font_family: str = Form(...)):
    # Verify data
    for color in [font_color, background_color]:
        if not color.startswith("#"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid color"
            )
        if 4 > len(color) > 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid color"
            )
        for char in color[1:]:
            if char not in "0123456789abcdefABCDEF":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid color"
                )
    if len(font_family.strip()) > 32:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Font family too long"
        )
    # Set settings
    await s.update(
        font_color=font_color,
        background_color=background_color,
        font_family=font_family.strip()
    )
    return RedirectResponse(
        url="/settings",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/questions", dependencies=[Depends(utils.login_check)])
async def questions(request: Request):
    return templates.TemplateResponse(
        "questions.html",
        {
            "request": request,
            "settings": s.settings,
            "questions": await db.fetch_all("SELECT id, name FROM questions WHERE enabled = 1")
        }
    )


@app.post("/update_questions", dependencies=[Depends(utils.login_check)])
async def update_questions(request: Request):
    # Verify data
    form_data = (await request.form()).multi_items()
    for question in form_data:
        if question[0] != "new" and not question[0].isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid question ID"
            )
        if len(question[1]) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question too long"
            )
    # Update questions
    question_ids = []
    new_questions = []
    for question in form_data:
        if question[0] == "new":
            new_questions.append(question[1])
        else:
            # Update question
            question_ids.append(int(question[0]))
            await db.execute(
                "UPDATE questions SET name = :name WHERE id = :id",
                {
                    "name": question[1].strip(),
                    "id": int(question[0])
                }
            )
    # Disable questions
    if question_ids:
        await db.execute(
            "UPDATE questions SET enabled = 0 WHERE id NOT IN :ids",
            {
                "ids": set(question_ids)
            }
        )
    else:
        await db.execute("UPDATE questions SET enabled = 0")
    # Add new questions
    for question in new_questions:
        await db.execute(
            "INSERT INTO questions (name, enabled) VALUES (:name, 1)",
            {
                "name": question.strip()
            }
        )
    # Redirect to the questions page
    return RedirectResponse(
        url="/questions",
        status_code=status.HTTP_303_SEE_OTHER
    )
