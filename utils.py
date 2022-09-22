######################################
#                                    #
#               diary                #
#                                    #
#                MIT                 #
#     Copyright (C) 2022 dodaucy     #
#  https://github.com/dodaucy/diary  #
#                                    #
######################################


from typing import Dict

from fastapi import HTTPException, status

from config import config
from globals import db


def get_style() -> Dict[str, str]:
    return {
        "font_color": str(config.style.font_color),
        "background_color": str(config.style.background_color),
        "font_family": str(config.style.font_family)
    }


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
