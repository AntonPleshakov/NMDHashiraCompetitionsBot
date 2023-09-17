from typing import List

from py_singleton import singleton

from config.config import getconf
from db.gapi.gsheets_managers import GSheetsManager
from db.gapi.worksheet_manager import WorksheetManager


class UsernameAlreadyExistsError(Exception):
    pass


@singleton
class Rating:
    def __init__(self):
        ss_name = getconf("RATING_LIST_GTABLE_NAME")
        ws_name = getconf("RATING_LIST_PAGE_NAME")

        self._manager: WorksheetManager = (
            GSheetsManager().open(ss_name).get_worksheet(ws_name)
        )

    def add_user_rating(
        self,
        tg_username: str,
        nmd_username: str = "",
        rating: int = 100,
        deviation: int = 200,
        attack: int = 0,
        arena_place: int = 0,
    ):
        if any(tg_username == row[0] for row in self._manager.get_all_values()):
            raise UsernameAlreadyExistsError

        new_row = [tg_username, nmd_username, rating, deviation, attack, arena_place]
        self._manager.add_row(new_row)
        self._manager.sort_table(2)

    def update_all_user_ratings(self, ratings: List[List[str]]):
        self._manager.update_all_values(ratings)
        self._manager.sort_table(2)

    def get_ratings(self) -> List[List[str]]:
        return self._manager.get_all_values()[1:]
