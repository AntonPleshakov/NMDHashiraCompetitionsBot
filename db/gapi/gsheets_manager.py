from typing import List

import pygsheets
from pygsheets.client import Client

from config.config import getconf
from logger.NMDLogger import nmd_logger
from .spreadsheet_manager import SpreadsheetManager


class SpreadsheetData:
    def __init__(self, name: str, id: str):
        self.name: str = name
        self.id: str = id


class GSheetsManager:
    def __init__(self):
        self._client: Client = pygsheets.authorize(
            service_file="gapi_service_file.json"
        )

    def open(self, spreadsheet_key: str) -> SpreadsheetManager:
        nmd_logger.info(f"GAPI: open ss {spreadsheet_key}")
        ss = self._client.open_by_key(spreadsheet_key)
        return SpreadsheetManager(ss)

    def create(self, spreadsheet_name: str) -> SpreadsheetManager:
        nmd_logger.info(f"GAPI: create ss {spreadsheet_name}")
        # There is an issue with ss creation in right folder: https://github.com/nithinmurali/pygsheets/issues/466
        ss = self._client.create(spreadsheet_name)
        self._client.drive.move_file(ss.id, None, getconf("GDRIVE_FOLDER_PATH"))
        return SpreadsheetManager(ss)

    def delete(self, spreadsheet_name: str):
        nmd_logger.info(f"GAPI: delete ss {spreadsheet_name}")
        filter_query = f"name='{spreadsheet_name}' and mimeType='application/vnd.google-apps.spreadsheet'"
        spreadsheets = self._client.drive.list(q=filter_query)
        if spreadsheets:
            ss = spreadsheets[0]
            self._client.drive.delete(ss["id"])

    def get_spreadsheets(self) -> List[SpreadsheetData]:
        query = f'"{getconf("GDRIVE_FOLDER_PATH")}" in parents'
        spreadsheets = [
            SpreadsheetData(x["name"], x["id"])
            for x in self._client.drive.spreadsheet_metadata(query)
        ]
        return spreadsheets
