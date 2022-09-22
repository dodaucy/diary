######################################
#                                    #
#               diary                #
#                                    #
#                MIT                 #
#     Copyright (C) 2022 dodaucy     #
#  https://github.com/dodaucy/diary  #
#                                    #
######################################


import os

import bcrypt
from fastapi import Cookie, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

import utils
from config import config
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
        # Check if token is valid
        fetched_token = await db.fetch_one(
            "SELECT * FROM sessions WHERE token = :token",
            {
                "token": token
            }
        )
        if fetched_token:
            # Return diary page
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "settings": s.settings
                }
            )
        # If the token is invalid, delete it
        login_response.delete_cookie(
            key="token",
            httponly=True
        )
    # Return the login page
    return login_response


@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    # Check if the password is correct
    if not bcrypt.checkpw(password.strip().encode(), config.password_hash.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
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


@app.get("/settings")
async def settings(request: Request, token: str = Cookie("")):
    await utils.login_check(token)
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "settings": s.settings
        }
    )


@app.post("/set_settings")
async def set_settings(token: str = Cookie(""), font_color: str = Form(...), background_color: str = Form(...), font_family: str = Form(...)):
    await utils.login_check(token)
    # Check data
    for color in [font_color, background_color]:
        if color.startswith("#"):
            color = color[1:]
        if 3 > len(color) > 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid color"
            )
        for char in color:
            if char not in "0123456789abcdefABCDEF":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid color"
                )
    if len(font_family) > 32:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Font family too long"
        )
    # Set settings
    await s.update(
        font_color=f"#{font_color}",
        background_color=f"#{background_color}",
        font_family=font_family
    )
    return RedirectResponse(
        url="/settings",
        status_code=status.HTTP_303_SEE_OTHER
    )
