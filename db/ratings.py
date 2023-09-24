from tournament_db.player import Player

from config.config import getconf
from db.gapi.gsheets_manager import GSheetsManager
from db.gapi.worksheet_manager import WorksheetManager, Matrix


class UsernameAlreadyExistsError(Exception):
    pass


class Rating:
    def __init__(self):
        ss_name = getconf("RATING_LIST_GTABLE_NAME")
        ws_name = getconf("RATING_LIST_PAGE_NAME")

        self._manager: WorksheetManager = (
            GSheetsManager().open(ss_name).get_worksheet(ws_name)
        )

    def add_user_rating(self, user: Player):
        if any(user.tg_username == row[0] for row in self._manager.get_all_values()):
            raise UsernameAlreadyExistsError

        new_row = [
            user.tg_username,
            user.nmd_username,
            user.rating,
            user.deviation,
            user.attack,
            user.arena_place,
        ]
        self._manager.add_row(new_row)
        self._manager.sort_table(2)

    def update_all_user_ratings(self, ratings: Matrix):
        self._manager.update_all_values(ratings)
        self._manager.sort_table(2)

    def get_ratings(self) -> Matrix:
        return self._manager.get_all_values()[1:]
