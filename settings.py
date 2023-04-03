#############################################
#                                           #
#                   diary                   #
#                                           #
#                    MIT                    #
#     Copyright (C) 2022 - 2023 dodaucy     #
#     https://github.com/dodaucy/diary      #
#                                           #
#############################################


from typing import Dict

from databases import Database

import constants
import models


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
                "INSERT INTO settings (font_color, primary_background_color, secondary_background_color, font_family) VALUES (:font_color, :primary_background_color, :secondary_background_color, :font_family)",
                self._data
            )

    async def update(self, *, settings: models.Settings) -> None:
        """Update settings in database"""
        self._data = settings.dict()
        await self.db.execute(
            "UPDATE settings SET font_color = :font_color, primary_background_color = :primary_background_color, secondary_background_color = :secondary_background_color, font_family = :font_family",
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
