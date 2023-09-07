from datetime import datetime

from py_singleton import singleton

from config.config import config, MODE
from db.gapi.gsheets_managers import GSheetsManager


@singleton
class Tournament:
    def __init__(self, spreadsheet_manager):
        self._manager = spreadsheet_manager

    @classmethod
    def create_new_tournament(cls):
        date = datetime.today().strftime("%d/%m/%Y")
        spreadsheet_name = config[MODE]["TOURNAMENT_GTABLE_NAME"] + " " + date
        manager = GSheetsManager().create(spreadsheet_name)
        return cls(manager)
