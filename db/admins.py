from typing import List

from py_singleton import singleton

from config.config import getconf
from db.gapi.gsheets_managers import GSheetsManager
from db.gapi.worksheet_manager import WorksheetManager


@singleton
class Admins:
    def __init__(self):
        ss_name = getconf("ADMINS_GTABLE_NAME")
        ws_name = getconf("ADMINS_PAGE_NAME")

        self._manager: WorksheetManager = (
            GSheetsManager().open(ss_name).get_worksheet(ws_name)
        )

    def add_admin(self, user_name: str, user_id: str):
        self._manager.add_row([user_name, user_id])

    def get_admins(self) -> List[List[str]]:
        return self._manager.get_all_values()
