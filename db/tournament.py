from py_singleton import singleton

from config.config import config, MODE
from gsheets_manager import GSheetsManager


@singleton
class Tournament:
    def __init__(self):
        self._manager = GSheetsManager(config[MODE]["COMPETITIONS_GTABLE_NAME"])

    # TODO: Will be updated to work with competitions pairing worksheets
    # def is_log_worksheet_exist(self, worksheet_name):
    #     worksheets = self.__logs_ss.worksheets()
    #     return any(getattr(ws, 'title') == worksheet_name for ws in worksheets)
    #
    # def add_log_worksheet(self, worksheet_name, rows, cols):
    #     self.__logs_ss.add_worksheet(worksheet_name, rows=rows, cols=cols, index=0)
    #
    # def delete_log_worksheet(self, worksheet_name):
    #     if not self.is_log_worksheet_exist(worksheet_name):
    #         return
    #
    #     ws = self.__logs_ss.worksheet_by_title(worksheet_name)
    #     self.__logs_ss.del_worksheet(ws)
    #
    # def rename_log_worksheet(self, old_name, new_name):
    #     if not self.is_log_worksheet_exist(old_name):
    #         return
    #
    #     ws = self.__logs_ss.worksheet_by_title(old_name)
    #     ws.title = new_name
