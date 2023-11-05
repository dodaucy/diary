from typing import Dict

from databases import Database

from . import constants
from . import models


class Settings():
    def __init__(self, database: Database):
        self.db = database
        self._data = {}

    async def load(self) -> None:
        """Load settings from database"""
        fetched_settings = await self.db.fetch_one("SELECT * FROM settings")
        if fetched_settings:
            # Load settings from database
            self._data = dict(fetched_settings)
        else:
            # Load default settings
            self._data = constants.DEFAULT_SETTINGS
            await self.db.execute(
                f"INSERT INTO settings ({', '.join(constants.DEFAULT_SETTINGS.keys())}) VALUES ({', '.join(':' + key for key in constants.DEFAULT_SETTINGS.keys())})",
                self._data
            )

    async def set_default(self) -> None:
        """Set default settings"""
        self._data = constants.DEFAULT_SETTINGS
        await self.db.execute(
            f"UPDATE settings SET {', '.join(key + ' = :' + key for key in constants.DEFAULT_SETTINGS.keys())}",
            self._data
        )

    async def update(self, settings: models.Settings) -> None:
        """Update settings in database"""
        self._data = settings.dict()
        await self.db.execute(
            f"UPDATE settings SET {', '.join(key + ' = :' + key for key in constants.DEFAULT_SETTINGS.keys())}",
            self._data
        )

    def items(self) -> Dict[str, str]:
        """Return settings as dict"""
        output = {}
        for key, value in self._data.items():
            output[key.replace("_", "-")] = value
        return output.items()

    def __getitem__(self, key: str) -> str:
        """Return setting value"""
        return self._data[key]
