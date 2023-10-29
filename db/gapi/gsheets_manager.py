from typing import List

import pygsheets
from pygsheets.client import Client

from config.config import getconf
from db.gapi.spreadsheet_manager import SpreadsheetManager


class GSheetsManager:
    def __init__(self):
        self._client: Client = pygsheets.authorize(
            service_file="gapi_service_file.json"
        )

    def open(self, spreadsheet_key: str) -> SpreadsheetManager:
        ss = self._client.open_by_key(spreadsheet_key)
        return SpreadsheetManager(ss)

    def create(self, spreadsheet_name: str) -> SpreadsheetManager:
        # There is an issue with ss creation in right folder: https://github.com/nithinmurali/pygsheets/issues/466
        ss = self._client.create(spreadsheet_name)
        self._client.drive.move_file(ss.id, None, getconf("GDRIVE_FOLDER_PATH"))
        return SpreadsheetManager(ss)

    def delete(self, spreadsheet_name: str):
        filter_query = f"name='{spreadsheet_name}' and mimeType='application/vnd.google-apps.spreadsheet'"
        spreadsheets = self._client.drive.list(q=filter_query)
        if spreadsheets:
            ss = spreadsheets[0]
            self._client.drive.delete(ss["id"])

    def get_spreadsheets(self) -> List[str]:
        query = f'"{getconf("GDRIVE_FOLDER_PATH")}" in parents'
        spreadsheets = self._client.spreadsheet_titles(query)
        return spreadsheets
