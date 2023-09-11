#############################################
#                                           #
#                   diary                   #
#                                           #
#                    MIT                    #
#     Copyright (C) 2022 - 2023 dodaucy     #
#     https://github.com/dodaucy/diary      #
#                                           #
#############################################


import os

from dotenv import load_dotenv
from humanfriendly import parse_timespan


# Load environment variables from .env file
load_dotenv(".env")


# Create ENV required variables
assert "DATABASE" in os.environ, "DATABASE environment variable is required"
# Only allow mariadb and mysql
database_lower = os.environ["DATABASE"].lower()
assert database_lower.startswith("mariadb") or database_lower.startswith("mysql"), "Only mariadb and mysql are supported"
DATABASE: str = os.environ["DATABASE"]
assert "PASSWORD_HASH" in os.environ, "PASSWORD_HASH environment variable is required"
PASSWORD_HASH: str = os.environ["PASSWORD_HASH"]


class Time:
    def __init__(self, time_string: str):
        self.seconds = parse_timespan(time_string)


class Config:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # Set default values
            self.__setattr__(key, value)
            if isinstance(value, Time):
                self.__setattr__(key, value.seconds)
            # Set environment variables
            if key in os.environ:
                if isinstance(value, Time):
                    # Time
                    if os.environ[key].isdigit():
                        self.__setattr__(key, int(os.environ[key]))
                    else:
                        self.__setattr__(key, parse_timespan(os.environ[key]))
                elif isinstance(value, bool):
                    # Boolean
                    if os.environ[key].upper() in ("YES", "Y", "TRUE", "1"):
                        self.__setattr__(key, True)
                    elif os.environ[key].upper() in ("NO", "N", "FALSE", "0"):
                        self.__setattr__(key, False)
                    else:
                        raise ValueError(f"{repr(key)} is not a valid boolean")
                else:
                    # Other
                    self.__setattr__(key, type(value)(os.environ[key]))


style = Config(
    SHOW_LOGO_ON_LOGIN=True,
    SHOW_GITHUB_LINK_ON_LOGIN=True
)

auth = Config(
    TOKEN_EXPIRATION=Time("16 weeks"),
    EXTEND_TOKEN_EXPIRATION_MAX_WHEN_ACTIVE=Time("7 days"),
    EXTEND_TOKEN_EXPIRATION_BUFFER=Time("6 hours"),
    TOKEN_EXPIRATION_WITHOUT_REQUESTS=Time("3 weeks"),
    CHECK_FOR_EXPIRED_TOKENS_EVERY=Time("15 minutes")
)

rate_limit = Config(
    RATE_LIMIT_ALLOW_REQUESTS=60,
    RATE_LIMIT_TIME_WINDOW=Time("5 minutes"),
    LOGIN_RATE_LIMIT_ALLOW_REQUESTS=30,
    LOGIN_RATE_LIMIT_TIME_WINDOW=Time("1 hour")
)
