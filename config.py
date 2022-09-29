import os

from dotenv import load_dotenv


# Load environment variables from config.env file
load_dotenv("config.env")


# Create ENV required variables
DATABASE: str = os.environ["DATABASE"]
PASSWORD_HASH: str = os.environ["PASSWORD_HASH"]


class Config:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)
            if key in os.environ:
                self.__setattr__(key, type(value)(os.environ[key]))
