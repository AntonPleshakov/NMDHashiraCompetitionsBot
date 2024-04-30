from typing import List, Optional

from config.config import getconf
from nmd_exceptions import UsernameAlreadyExistsError
from parameters import Parameters
from parameters.int_param import IntParam
from parameters.str_param import StrParam
from .gapi.gsheets_manager import GSheetsManager
from .gapi.worksheet_manager import WorksheetManager


class Rating(Parameters):
    def __init__(self):
        self.tg_username: StrParam = StrParam("ТГ Username")
        self.tg_id: IntParam = IntParam("ТГ ID")
        self.nmd_username: StrParam = StrParam("NMD Username")
        self.rating: IntParam = IntParam("Рейтинг")
        self.deviation: IntParam = IntParam("Отклонение")


class RatingsDB:
    def __init__(self):
        ss_name = getconf("RATING_LIST_GTABLE_KEY")
        ws_name = getconf("RATING_LIST_PAGE_NAME")

        self._manager: WorksheetManager = (
            GSheetsManager().open(ss_name).get_worksheet(ws_name)
        )

    def add_user_rating(self, user: Rating):
        rows = self._manager.get_all_values()
        if any(str(user.tg_username) == row[user.tg_username.index] for row in rows):
            raise UsernameAlreadyExistsError

        self._manager.add_row(user.to_row())
        self._manager.sort_table(user.rating.index)

    def update_all_user_ratings(self, ratings: List[Rating]):
        rows = []
        for rating in ratings:
            rows.append(rating.to_row())
        self._manager.update_values(rows)
        self._manager.sort_table(Rating().rating.index)

    def update_user_rating(self, tg_username: str, rating: Rating):
        rows = self._manager.get_all_values()
        for i, row in enumerate(rows):
            if row[rating.tg_username.index] == tg_username:
                rows[i] = rating.to_row()
        self._manager.update_values(rows)
        self._manager.sort_table(rating.rating.index)

    def get_ratings(self) -> List[Rating]:
        rows = self._manager.get_all_values()
        ratings = []
        for row in rows:
            ratings.append(Rating.from_row(row))
        return ratings

    def get_rating(self, tg_username: str) -> Optional[Rating]:
        ratings = self.get_ratings()
        for rating in ratings:
            if rating.tg_username.value == tg_username:
                return rating
        return None

    def delete_rating(self, tg_username: str):
        new_ratings = [
            rating
            for rating in self.get_ratings()
            if rating.tg_username.value != tg_username
        ]
        self.update_all_user_ratings(new_ratings)

    def fetch_ratings(self):
        self._manager.fetch()


ratings_db = RatingsDB()
