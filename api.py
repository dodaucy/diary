import calendar
import datetime

from fastapi import Depends, FastAPI, HTTPException, status

import utils
from globals import db, rate_limit_handler


app = FastAPI(openapi_url=None)


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
