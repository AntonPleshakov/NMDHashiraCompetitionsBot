from typing import Dict

from pygsheets.spreadsheet import Spreadsheet
from pygsheets.worksheet import Worksheet

from db.gapi.worksheet_manager import WorksheetManager


class SpreadsheetManager:
    def __init__(self, spreadsheet: Spreadsheet):
        self._ss: Spreadsheet = spreadsheet
        self._cache: Dict[str, Worksheet] = dict()

    def cache(self, worksheet_title: str) -> Worksheet:
        if worksheet_title not in self._cache:
            self._cache[worksheet_title] = self._ss.worksheet_by_title(worksheet_title)
        return self._cache[worksheet_title]

    def get_worksheet(self, worksheet_title: str) -> WorksheetManager:
        ws_manager = WorksheetManager(self.cache(worksheet_title))
        return ws_manager

    def is_worksheet_exist(self, worksheet_name: str) -> bool:
        worksheets = self._ss.worksheets()
        return any(ws.title == worksheet_name for ws in worksheets)

    def add_worksheet(self, worksheet_name: str):
        self._ss.add_worksheet(worksheet_name, index=0)
