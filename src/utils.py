import datetime
import string

from fastapi import Cookie, HTTPException, status

from . import config
from .globals import db


async def is_logged_in(token: str) -> bool:
    """Check if the user is logged in"""
    if token == "":
        return False
    return await db.fetch_one(
        """
        SELECT
            token
        FROM
            sessions
        WHERE
            token = :token
            AND
            (
                created_at > UNIX_TIMESTAMP() - :token_expiration
                OR (
                    created_at > UNIX_TIMESTAMP() - :token_expiration - :extend_token_expiration_max_when_active
                    AND last_request > UNIX_TIMESTAMP() - :extend_token_expiration_buffer
                )
            )
            AND last_request > UNIX_TIMESTAMP() - :token_expiration_without_requests
        """,
        {
            "token": token,
            "token_expiration": config.auth.TOKEN_EXPIRATION,
            "extend_token_expiration_max_when_active": config.auth.EXTEND_TOKEN_EXPIRATION_MAX_WHEN_ACTIVE,
            "extend_token_expiration_buffer": config.auth.EXTEND_TOKEN_EXPIRATION_BUFFER,
            "token_expiration_without_requests": config.auth.TOKEN_EXPIRATION_WITHOUT_REQUESTS
        }
    ) is not None


async def login_check(token: str = Cookie("")) -> None:
    """Raise an exception if the user is not logged in"""
    if not await is_logged_in(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in"
        )


def get_days(date: str) -> int:
    """
    Count the number of days since 1st January 1970

    Format: `YYYY-MM-DD`
    """
    date_split = date.split("-")
    if len(date_split) == 3:
        for split in date_split:
            if not split.isdigit():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date"
                )
        if date_split[0].isdigit():
            if 6000 >= int(date_split[0]) >= 1970:
                try:
                    return (datetime.date(int(date_split[0]), int(date_split[1]), int(date_split[2])) - datetime.date(1970, 1, 1)).days
                except ValueError:
                    pass
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid date"
    )


def get_date(days: int) -> str:
    """
    Get the date from the number of days since 1st January 1970

    Format: `YYYY-MM-DD`
    """
    return (datetime.date(1970, 1, 1) + datetime.timedelta(days=days)).strftime("%Y-%m-%d")


def verify_color(color: str) -> None:
    if color.startswith("#") and len(color) == 7:
        for char in color[1:]:
            if char not in string.hexdigits:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid color"
                )
        return
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid color"
    )
