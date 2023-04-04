#############################################
#                                           #
#                   diary                   #
#                                           #
#                    MIT                    #
#     Copyright (C) 2022 - 2023 dodaucy     #
#     https://github.com/dodaucy/diary      #
#                                           #
#############################################


import mimetypes
import os

import bcrypt
from fastapi import Cookie, Depends, FastAPI, Form, Request, status
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
templates.env.globals["settings"] = global_settings


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception(request: Request, exc: StarletteHTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url="/",
            status_code=status.HTTP_303_SEE_OTHER
        )
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
                    "questions": await db.fetch_all("SELECT id, name, color FROM questions WHERE enabled = 1"),
                    "selected_navbar_item": "diary"
                }
            )
        # Delete session cookie
        login_response.delete_cookie(
            key="token",
            httponly=True
        )
    # Return the login page
    return login_response


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


@app.get("/stats", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def stats(request: Request):
    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "questions": await db.fetch_all("SELECT id, name, color FROM questions WHERE enabled = 1"),
            "selected_navbar_item": "stats"
        }
    )


@app.get("/questions", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def questions(request: Request):
    return templates.TemplateResponse(
        "questions.html",
        {
            "request": request,
            "questions": await db.fetch_all("SELECT id, name, color FROM questions WHERE enabled = 1"),
            "selected_navbar_item": "questions"
        }
    )


@app.get("/settings", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def settings(request: Request):
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "selected_navbar_item": "settings"
        }
    )


@app.get("/test", dependencies=[Depends(rate_limit_handler.trigger)])
async def test(request: Request):
    return templates.TemplateResponse(
        "test.html",
        {
            "request": request
        }
    )


@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(
        url="/static/icons/32x32.png"
    )
