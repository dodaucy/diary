import os

from dotenv import load_dotenv
from humanfriendly import parse_timespan


# Load environment variables from config.env file
load_dotenv("config.env")


# Create ENV required variables
DATABASE: str = os.environ["DATABASE"]
PASSWORD_HASH: str = os.environ["PASSWORD_HASH"]


class Time:
    def __init__(self, time_string: str):
        self.seconds = parse_timespan(time_string)


class Config:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, Time):
                self.__setattr__(key, value.seconds)
                if key in os.environ:
                    if os.environ[key].isdigit():
                        self.__setattr__(key, int(os.environ[key]))
                    else:
                        self.__setattr__(key, parse_timespan(os.environ[key]))
            else:
                self.__setattr__(key, value)
                if key in os.environ:
                    self.__setattr__(key, type(value)(os.environ[key]))
