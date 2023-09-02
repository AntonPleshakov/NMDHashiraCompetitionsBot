from py_singleton import singleton

from config.config import config, MODE
from gsheets_manager import GSheetsManager


class UsernameAlreadyExistsError(Exception):
    pass


@singleton
class Rating:
    def __init__(self):
        ss_name = config[MODE]["RATING_LIST_GTABLE_NAME"]
        ws_name = config[MODE]["RATING_LIST_PAGE_NAME"]

        self._manager = GSheetsManager(ss_name).get_worksheet(ws_name)

    def add_user_rating(
        self,
        tg_username,
        nmd_username="",
        rating=100,
        deviation=200,
        attack=0,
        arena_place=0,
    ):
        if any(tg_username == row[0] for row in self._manager.get_all_values()):
            raise UsernameAlreadyExistsError

        new_row = [tg_username, nmd_username, rating, deviation, attack, arena_place]
        self._manager.add_row(new_row)
        self._manager.sort_table(2)

    def update_all_user_ratings(self, ratings):
        self._manager.update_values(ratings)
        self._manager.sort_table(2)

    def get_ratings(self):
        return self._manager.get_all_values()[1:]
