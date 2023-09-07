from py_singleton import singleton

from config.config import config, MODE
from db.gapi.gsheets_managers import GSheetsManager


@singleton
class Admins:
    def __init__(self):
        ss_name = config[MODE]["ADMINS_GTABLE_NAME"]
        ws_name = config[MODE]["ADMINS_PAGE_NAME"]

        self._manager = GSheetsManager().open(ss_name).get_worksheet(ws_name)

    def add_admin(self, user_name, user_id):
        self._manager.add_row([user_name, user_id])

    def get_admins(self):
        return self._manager.get_all_values()
