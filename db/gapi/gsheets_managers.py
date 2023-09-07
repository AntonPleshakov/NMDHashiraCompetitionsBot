import pygsheets

from config.config import config, MODE
from db.gapi.spreadsheet_manager import SpreadsheetManager


class GSheetsManager:
    def __init__(self):
        self._client = pygsheets.authorize(service_file="gapi_service_file.json")

    def open(self, spreadsheet_name):
        ss = self._client.open(spreadsheet_name)
        return SpreadsheetManager(ss)

    def create(self, spreadsheet_name):
        ss = self._client.create(
            spreadsheet_name, folder=config[MODE]["GDRIVE_FOLDER_PATH"]
        )
        return SpreadsheetManager(ss)

    def get_spreadsheets(self):
        query = f'"{config[MODE]["GDRIVE_FOLDER_PATH"]}" in parents'
        spreadsheets = self._client.spreadsheet_titles(query)
        return spreadsheets
