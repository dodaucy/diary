#############################################
#                                           #
#                   diary                   #
#                                           #
#                    MIT                    #
#     Copyright (C) 2022 - 2023 dodaucy     #
#     https://github.com/dodaucy/diary      #
#                                           #
#############################################


import asyncio
import calendar
import datetime
import os

import bcrypt
from fastapi import Depends, FastAPI, HTTPException, Response, status

import config
import models
import utils
from globals import db, login_rate_limit_handler, rate_limit_handler
from globals import settings as global_settings


app = FastAPI(openapi_url=None)

question_insert_lock = asyncio.Lock()


@app.post("/login", dependencies=[Depends(login_rate_limit_handler.trigger)])
async def login(login_model: models.Login):
    password = login_model.password
    # Verify password
    if not bcrypt.checkpw(password.strip().encode(), config.PASSWORD_HASH.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    # Create a session
    token = os.urandom(32).hex()
    await db.execute(
        "INSERT INTO sessions (token, last_request, created_at) VALUES (:token, UNIX_TIMESTAMP(), UNIX_TIMESTAMP())",
        {
            "token": token
        }
    )
    # Return response with token
    response = Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
    response.set_cookie(
        key="token",
        value=token,
        httponly=True
    )
    return response


@app.get("/diary", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def diary(date: str):
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


@app.post("/update_diary_entry", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def update_diary_entry(diary_entry: models.DiaryEntry):
    days = utils.get_days(diary_entry.date)
    # Verify data
    if len(diary_entry.notes) > 65535:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notes must be less than 65535 characters"
        )
    for key, value in diary_entry.answers.items():
        if key < 0 or key > 4294967295:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid key"
            )
        if value < 0 or value > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid answer value"
            )
    # Update notes
    await db.execute(
        "INSERT INTO notes (days, notes) VALUES (:days, :notes) ON DUPLICATE KEY UPDATE notes = :notes",
        {
            "days": days,
            "notes": diary_entry.notes
        }
    )
    # Update answers
    for key, value in diary_entry.answers.items():
        await db.execute(
            "INSERT INTO answers (days, question_id, value) VALUES (:days, :question_id, :value) ON DUPLICATE KEY UPDATE value = :value",
            {
                "days": days,
                "question_id": key,
                "value": value
            }
        )
    # Return 204
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@app.get("/stats", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def stats(year: int):
    # Verify data
    if year < 1970 or year > 6000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid year"
        )
    # Fetch data
    answers = await db.fetch_all(
        "SELECT days, question_id, value FROM answers WHERE days >= :year AND days < :next_year ORDER BY days ASC",
        {
            "year": (datetime.date(year, 1, 1) - datetime.date(1970, 1, 1)).days,
            "next_year": (datetime.date(year + 1, 1, 1) - datetime.date(1970, 1, 1)).days
        }
    )
    # Format data
    final_answers = []
    for month in range(12):
        month += 1
        day_list = []
        for day in range(calendar.monthrange(year, month)[1]):
            day += 1
            day_dict = {}
            for answer in answers:
                if datetime.date(year, month, day) == datetime.date(1970, 1, 1) + datetime.timedelta(days=answer["days"]):
                    if answer['value']:
                        day_dict[answer["question_id"]] = answer["value"]
            day_list.append(day_dict)
        final_answers.append(day_list)
    return final_answers


@app.post("/new_question", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def new_question(question: models.NewQuestion):
    # Verify data
    utils.verify_color(question.color)
    if len(question.name) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question name must be less or equal to 255 characters"
        )
    # Insert question
    async with question_insert_lock:
        await db.execute(
            "INSERT INTO questions (name, color, enabled) VALUES (:name, :color, :enabled)",
            {
                "name": question.name,
                "color": question.color,
                "enabled": question.enabled
            }
        )
        question_id = await db.fetch_val(
            "SELECT LAST_INSERT_ID()"
        )
    # Return question id
    return {
        "question_id": question_id
    }


@app.post("/update_question", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def update_question(question: models.UpdateQuestion):
    # Verify data
    utils.verify_color(question.color)
    if len(question.name) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question name must be less or equal to 255 characters"
        )
    if question.question_id < 0 or question.question_id > 4294967295:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question id"
        )
    # Update question
    await db.execute(
        "UPDATE questions SET name = :name, color = :color, enabled = :enabled WHERE id = :question_id",
        {
            "question_id": question.question_id,
            "name": question.name,
            "color": question.color,
            "enabled": question.enabled
        }
    )
    # Return 204
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@app.post("/delete_question", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def delete_question(question: models.DeleteQuestion):
    # Verify data
    if question.question_id < 0 or question.question_id > 4294967295:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question id"
        )
    # Delete question
    await db.execute(
        "DELETE FROM questions WHERE id = :question_id",
        {
            "question_id": question.question_id
        }
    )
    # Return 204
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@app.post("/update_settings", dependencies=[Depends(rate_limit_handler.trigger), Depends(utils.login_check)])
async def update_settings(settings: models.Settings):
    # Verify data
    data = settings.dict()
    if len(data.pop("font_family")) > 32:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Font family must be less or equal to 32 characters"
        )
    for color in data.values():
        utils.verify_color(color)
    # Update settings
    await global_settings.update(settings)
    # Return 204
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
