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
