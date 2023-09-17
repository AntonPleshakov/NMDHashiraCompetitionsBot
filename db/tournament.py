from datetime import datetime

from py_singleton import singleton

from config.config import getconf
from db.gapi.gsheets_managers import GSheetsManager
from db.gapi.spreadsheet_manager import SpreadsheetManager


@singleton
class Tournament:
    def __init__(self, spreadsheet_manager: SpreadsheetManager):
        self._manager: SpreadsheetManager = spreadsheet_manager

    @classmethod
    def create_new_tournament(cls):
        date = datetime.today().strftime("%d/%m/%Y")
        spreadsheet_name = getconf("TOURNAMENT_GTABLE_NAME") + " " + date
        manager = GSheetsManager().create(spreadsheet_name)
        return cls(manager)
