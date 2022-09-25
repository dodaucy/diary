######################################
#                                    #
#               diary                #
#                                    #
#                MIT                 #
#     Copyright (C) 2022 dodaucy     #
#  https://github.com/dodaucy/diary  #
#                                    #
######################################


import datetime

from fastapi import HTTPException, status

from globals import db


async def login_check(token: str) -> None:
    """Check if the user is logged in"""
    if token:
        fetched_token = await db.fetch_one(
            "SELECT * FROM sessions WHERE token = :token",
            {
                "token": token
            }
        )
        if fetched_token:
            return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not logged in"
    )


def get_days(date: str) -> int:
    """Count the number of days since 1st January 1970"""
    date_split = date.split("-")
    if len(date_split) == 3:
        for split in date_split:
            if not split.isdigit():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date"
                )
        if date_split[0].isdigit():
            if 6000 > int(date_split[0]) > 1970:
                try:
                    return (datetime.date(int(date_split[0]), int(date_split[1]), int(date_split[2])) - datetime.date(1970, 1, 1)).days
                except ValueError:
                    pass
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid date"
    )
