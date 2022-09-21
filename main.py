######################################
#                                    #
#               diary                #
#                                    #
#                MIT                 #
#     Copyright (C) 2022 dodaucy     #
#  https://github.com/dodaucy/diary  #
#                                    #
######################################


from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import config


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
            "detail": exc.detail
        },
        exc.status_code
    )


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request
        }
    )


@app.post("/")
def login(request: Request, password: str = Form(...)):
    if password.strip() != config.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )
