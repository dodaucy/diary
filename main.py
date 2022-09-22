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
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

import utils
from config import config
from globals import db


app = FastAPI(openapi_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "style": utils.get_style()
        },
        exc.status_code
    )


@app.on_event("startup")
async def startup():
    await db.connect()


@app.get("/")
async def index(request: Request, token: str = Cookie("")):
    login_response = templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "style": utils.get_style()
        }
    )
    if token:
        fetched_token = await db.fetch_one(
            "SELECT * FROM sessions WHERE token = :token",
            {
                "token": token
            }
        )
        if fetched_token:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "style": utils.get_style()
                }
            )
        login_response.delete_cookie(
            key="token",
            httponly=True
        )
    return login_response


@app.post("/")
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
    # Return the session token and login
    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "style": utils.get_style()
        }
    )
    response.set_cookie(
        key="token",
        value=token,
        httponly=True
    )
    return response
