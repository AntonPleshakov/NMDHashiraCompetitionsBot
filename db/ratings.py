from datetime import date
from typing import List, Optional

from common.nmd_datetime import nmd_parse_datetime, nmd_now
from config.config import getconf
from logger.NMDLogger import nmd_logger
from nmd_exceptions import UsernameAlreadyExistsError, NewPlayerError
from parameters import Parameters
from parameters.int_param import IntParam
from parameters.str_param import StrParam
from .gapi.gsheets_manager import GSheetsManager
from .gapi.worksheet_manager import WorksheetManager


class Rating(Parameters):
    DATE_FORMAT = "%d.%m.%Y"

    def __init__(self):
        self.tg_username: StrParam = StrParam("ТГ Username")
        self.tg_id: IntParam = IntParam("ТГ ID")
        self.nmd_username: StrParam = StrParam("NMD Username")
        self.rating: IntParam = IntParam("Рейтинг")
        self.deviation: IntParam = IntParam("Отклонение")
        self.last_date: StrParam = StrParam("Дата последнего турнира")

    @classmethod
    def default(cls, tg_id: int):
        rating = cls()
        rating.tg_id.value = tg_id
        rating.rating.value = getconf("20K_RATING")
        rating.deviation.value = getconf("DEFAULT_DEVIATION")
        rating.last_date.value = ""
        return rating

    def update_date(self):
        self.last_date.value = date.today().strftime(self.DATE_FORMAT)

    def get_weeks(self):
        if not self.last_date.value:
            raise NewPlayerError
        last_date = nmd_parse_datetime(self.last_date.value, self.DATE_FORMAT)
        date_diff = nmd_now() - last_date
        return date_diff.days // 7


class RatingsDB:
    def __init__(self):
        ss_name = getconf("RATING_LIST_GTABLE_KEY")
        ws_name = getconf("RATING_LIST_PAGE_NAME")

        ss = GSheetsManager().open(ss_name)
        self._manager: WorksheetManager = ss.get_worksheet(ws_name)
        self._url = ss.get_url()

    def get_url(self):
        return self._url

    def add_user_rating(self, user: Rating):
        nmd_logger.info(f"DB: add user rating for {user.tg_username}")
        rows = self._manager.get_all_values()
        if any(user.tg_id.value == row[user.tg_id.index] for row in rows):
            raise UsernameAlreadyExistsError

        self._manager.add_row(user.to_row())
        self._manager.sort_table(user.rating.index)

    def update_all_user_ratings(self, ratings: List[Rating]):
        nmd_logger.info("DB: update all ratings")
        rows = [r.to_row() for r in ratings]
        self._manager.update_values(rows)
        self._manager.sort_table(Rating().rating.index)

    def update_user_rating(self, tg_id: int, rating: Rating):
        nmd_logger.info(
            f"DB: update user {rating.tg_username} info to: {', '.join(rating.to_row())}"
        )
        rows = self._manager.get_all_values()
        for i, row in enumerate(rows):
            if row[rating.tg_id.index] == str(tg_id):
                rows[i] = rating.to_row()
        self._manager.update_values(rows)
        self._manager.sort_table(rating.rating.index)

    def get_ratings(self) -> List[Rating]:
        rows = self._manager.get_all_values()
        ratings = []
        for row in rows:
            ratings.append(Rating.from_row(row))
        return ratings

    def get_rating(self, tg_id: int) -> Optional[Rating]:
        ratings = self.get_ratings()
        for rating in ratings:
            if rating.tg_id.value == tg_id:
                return rating
        return None

    def delete_rating(self, tg_id: int):
        new_ratings = [
            rating for rating in self.get_ratings() if rating.tg_id.value != tg_id
        ]
        self.update_all_user_ratings(new_ratings)

    def fetch_ratings(self):
        nmd_logger.info("DB: fetch ratings")
        self._manager.fetch()


ratings_db = RatingsDB()
