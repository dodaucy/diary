######################################
#                                    #
#               diary                #
#                                    #
#                MIT                 #
#     Copyright (C) 2022 dodaucy     #
#  https://github.com/dodaucy/diary  #
#                                    #
######################################


from databases import Database

import constants


class Settings:
    def __init__(self, database: Database):
        self.db = database
        self._data = {}

    async def load(self) -> None:
        """Load settings from database"""
        fetched_settings = await self.db.fetch_one("SELECT * FROM settings")
        if fetched_settings:
            # Load settings from database
            self._data = {
                "font_color": fetched_settings["font_color"],
                "background_color": fetched_settings["background_color"],
                "font_family": fetched_settings["font_family"]
            }
        else:
            # Load default settings
            self._data = {
                "font_color": constants.DEFAULT_FONT_COLOR,
                "background_color": constants.DEFAULT_BACKGROUND_COLOR,
                "font_family": constants.DEFAULT_FONT_FAMILY
            }
            await db.execute(
                "INSERT INTO settings (font_color, background_color, font_family) VALUES (:font_color, :background_color, :font_family)",
                self._data
            )

    async def update(self, *, font_color: str, background_color: str, font_family: str) -> None:
        """Update settings in database"""
        self._data = {
            "font_color": font_color,
            "background_color": background_color,
            "font_family": font_family
        }
        await self.db.execute(
            "UPDATE settings SET font_color = :font_color, background_color = :background_color, font_family = :font_family",
            self._data
        )

    def get(self, key: str) -> str:
        """Get a setting"""
        return self._data[key]
