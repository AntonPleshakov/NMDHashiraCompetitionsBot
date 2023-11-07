from typing import List

from config.config import getconf
from nmd_exceptions import UsernameAlreadyExistsError
from tournament.player import Player
from .gapi.gsheets_manager import GSheetsManager
from .gapi.worksheet_manager import WorksheetManager


class RatingsDB:
    def __init__(self):
        ss_name = getconf("RATING_LIST_GTABLE_KEY")
        ws_name = getconf("RATING_LIST_PAGE_NAME")

        self._manager: WorksheetManager = (
            GSheetsManager().open(ss_name).get_worksheet(ws_name)
        )

    def add_user_rating(self, user: Player):
        if any(user.tg_username == row[0] for row in self._manager.get_all_values()):
            raise UsernameAlreadyExistsError

        self._manager.add_row(user.to_list())
        self._manager.sort_table(2)

    def update_all_user_ratings(self, ratings: List[Player]):
        rows = []
        for player in ratings:
            rows.append(player.to_list())
        self._manager.update_values(rows)
        self._manager.sort_table(2)

    def get_ratings(self) -> List[Player]:
        rows = self._manager.get_all_values()[1:]
        ratings = []
        for row in rows:
            ratings.append(Player.from_list(row))
        return ratings

    def delete_rating(self, tg_username: str):
        new_ratings = [
            player for player in self.get_ratings() if player.tg_username != tg_username
        ]
        self.update_all_user_ratings(new_ratings)

    def fetch_ratings(self):
        self._manager.fetch()


ratings_db = RatingsDB()
