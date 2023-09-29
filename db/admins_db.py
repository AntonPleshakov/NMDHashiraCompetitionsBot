from config.config import getconf
from db.gapi.gsheets_manager import GSheetsManager
from db.gapi.worksheet_manager import WorksheetManager, Matrix


class AdminsDB:
    def __init__(self):
        ss_name = getconf("ADMINS_GTABLE_NAME")
        ws_name = getconf("ADMINS_PAGE_NAME")

        self._manager: WorksheetManager = (
            GSheetsManager().open(ss_name).get_worksheet(ws_name)
        )

    def add_admin(self, user_name: str, user_id: str):
        self._manager.add_row([user_name, user_id])

    def get_admins(self) -> Matrix:
        return self._manager.get_all_values()[1:]

    def del_admin(self, user_id: str):
        admins = self.get_admins()
        new_admins = [row for row in admins if row[1] != user_id]
        self._manager.update_values(new_admins)
