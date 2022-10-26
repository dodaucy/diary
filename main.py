######################################
#                                    #
#               diary                #
#                                    #
#                MIT                 #
#     Copyright (C) 2022 dodaucy     #
#  https://github.com/dodaucy/diary  #
#                                    #
######################################


import mimetypes
import os

import bcrypt
from fastapi import (Cookie, Depends, FastAPI, Form, HTTPException, Request,
                     status)
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_utils.tasks import repeat_every
from starlette.exceptions import HTTPException as StarletteHTTPException

import api
import config
import utils
from globals import db, login_rate_limit_handler, rate_limit_handler
from globals import settings as global_settings


app = FastAPI(openapi_url=None)
app.mount("/api", api.app)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
templates.env.globals["len"] = len
templates.env.globals["settings"] = global_settings.get


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "detail": exc.detail
        },
        exc.status_code
    )


@repeat_every(seconds=config.auth.CHECK_FOR_EXPIRED_TOKENS_EVERY)
async def delete_expired_tokens():
    await db.execute(
        """
        DELETE FROM
            sessions
        WHERE
            created_at <= UNIX_TIMESTAMP() - :token_expiration - :extend_token_expiration_max_when_active
            OR (
                created_at <= UNIX_TIMESTAMP() - :token_expiration
                AND last_request <= UNIX_TIMESTAMP() - :extend_token_expiration_buffer
            )
            OR last_request <= UNIX_TIMESTAMP() - :token_expiration_without_requests
        """,
        {
            "token_expiration": config.auth.TOKEN_EXPIRATION,
            "extend_token_expiration_max_when_active": config.auth.EXTEND_TOKEN_EXPIRATION_MAX_WHEN_ACTIVE,
            "extend_token_expiration_buffer": config.auth.EXTEND_TOKEN_EXPIRATION_BUFFER,
            "token_expiration_without_requests": config.auth.TOKEN_EXPIRATION_WITHOUT_REQUESTS
        }
    )


@app.on_event("startup")
async def startup():
    mimetypes.init()
    mimetypes.add_type("image/webp", ".webp")
    await db.connect()
    await global_settings.load()
    await delete_expired_tokens()


@app.get("/", dependencies=[Depends(rate_limit_handler.trigger)])
async def index(request: Request, token: str = Cookie("")):
    # Create login page response
    login_response = templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "show_logo": config.style.SHOW_LOGO_ON_LOGIN,
            "show_github": config.style.SHOW_GITHUB_LINK_ON_LOGIN,
        }
    )
    if token:
        if await utils.is_logged_in(token):
            # Return diary page
            return templates.TemplateResponse(
                "diary.html",
                {
                    "request": request,
                    "questions": await db.fetch_all("SELECT id, name, color FROM questions WHERE enabled = 1")
                }
            )
        # Delete session cookie
        login_response.delete_cookie(
            key="token",
            httponly=True
        )
    # Return the login page
    return login_response


@app.post("/update_diary", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def post_diary(request: Request, date: str = Form(...), notes: str = Form("")):
    form_data = await request.form()
    days = utils.get_days(date)
    # Verify data
    if len(notes) > 65535:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notes must be less than 65535 characters"
        )
    for key, value in form_data.items():
        if key in ("date", "notes"):
            continue
        if not key.isdigit() or not value.isdigit() or 1 > int(value) > 5 or int(key) > 4294967295:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data"
            )
    # Update notes
    await db.execute(
        "INSERT INTO notes (days, notes) VALUES (:days, :notes) ON DUPLICATE KEY UPDATE notes = :notes",
        {
            "days": days,
            "notes": notes
        }
    )
    # Update answers
    for key, value in form_data.items():
        if key in ("date", "notes"):
            continue
        await db.execute(
            "INSERT INTO answers (days, question_id, value) VALUES (:days, :question_id, :value) ON DUPLICATE KEY UPDATE value = :value",
            {
                "days": days,
                "question_id": int(key),
                "value": int(value)
            }
        )
    # Rredirect to diary
    return RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.post("/login", dependencies=[Depends(login_rate_limit_handler.trigger)])
async def login(password: str = Form(...)):
    # Verify password
    if not bcrypt.checkpw(password.strip().encode(), config.PASSWORD_HASH.encode()):
        return RedirectResponse(
            url="/",
            status_code=status.HTTP_303_SEE_OTHER
        )
    # Create a session
    token = os.urandom(32).hex()
    await db.execute(
        "INSERT INTO sessions (token, last_request, created_at) VALUES (:token, UNIX_TIMESTAMP(), UNIX_TIMESTAMP())",
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


@app.post("/logout", dependencies=[Depends(rate_limit_handler.trigger)])
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


@app.get("/settings", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def settings(request: Request):
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request
        }
    )


@app.post("/update_settings", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
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
    await global_settings.update(
        font_color=font_color,
        background_color=background_color,
        font_family=font_family.strip()
    )
    return RedirectResponse(
        url="/settings",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/questions", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def questions(request: Request):
    return templates.TemplateResponse(
        "questions.html",
        {
            "request": request,
            "questions": await db.fetch_all("SELECT id, name, color FROM questions WHERE enabled = 1")
        }
    )


@app.post("/update_questions", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def update_questions(request: Request):
    new_questions = {}
    existing_questions = {}
    form_data = (await request.form()).items()
    for question in form_data:
        # Verify data
        key_splited = question[0].split("_")
        if not any((
            len(key_splited) == 2 and key_splited[0].isdigit() and key_splited[1] in ("name", "color"),  # Update existing question
            len(key_splited) == 3 and key_splited[0] == "new" and key_splited[1] in ("name", "color")  # Create new question
        )):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid key"
            )
        if len(question[1]) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question too long"
            )
        # Sort data
        if key_splited[0] == "new":
            if key_splited[2] not in new_questions:
                new_questions[key_splited[2]] = {}
            new_questions[key_splited[2]][key_splited[1]] = question[1]
        else:
            if key_splited[0] not in existing_questions:
                existing_questions[key_splited[0]] = {}
            existing_questions[key_splited[0]][key_splited[1]] = question[1]
    # Verify data
    for question in new_questions.values():
        if "name" not in question or "color" not in question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid question"
            )
    for question in existing_questions.values():
        if "name" not in question or "color" not in question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid question"
            )
    # Update questions
    for question_id, question in existing_questions.items():
        await db.execute(
            "UPDATE questions SET name = :name, color = :color WHERE id = :id",
            {
                "name": question["name"],
                "color": question["color"],
                "id": question_id
            }
        )
    # Disable questions
    if existing_questions:
        await db.execute(
            "UPDATE questions SET enabled = 0 WHERE id NOT IN :ids",
            {
                "ids": set(existing_questions.keys())
            }
        )
    else:
        await db.execute("UPDATE questions SET enabled = 0")
    # Create questions
    for question in new_questions.values():
        await db.execute(
            "INSERT INTO questions (name, color, enabled) VALUES (:name, :color, 1)",
            {
                "name": question["name"],
                "color": question["color"]
            }
        )
    return RedirectResponse(
        url="/questions",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/stats", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def stats(request: Request):
    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "questions": await db.fetch_all("SELECT id, name, color FROM questions WHERE enabled = 1")
        }
    )


@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(
        url="/static/icons/32x32.png"
    )
