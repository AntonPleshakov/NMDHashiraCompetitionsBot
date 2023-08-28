import pygsheets
from ConfigManager import config, MODE
from enum import Enum


class Worksheets(Enum):
    RATING = 0
    TOURNAMENT = 1
    ADMINS = 2


class DBManager:
    @staticmethod
    def __get_all_values(worksheet):
        return worksheet.get_all_values(
            include_tailing_empty_rows=False, include_tailing_empty=False
        )

    def __init__(self):
        client = pygsheets.authorize(service_file="nmdhashiracompetitionsbot-9ace8e5ff078.json")
        spreadsheet = client.open(config[MODE]['GTABLE_NAME'])

        self.__rating_worksheet = spreadsheet[Worksheets.RATING.value]
        self.__tournament_worksheet = spreadsheet[Worksheets.TOURNAMENT.value]
        self.__admins_worksheet = spreadsheet[Worksheets.ADMINS.value]
        self.__rating = self.__get_all_values(self.__rating_worksheet)
        self.__tournament = self.__get_all_values(self.__tournament_worksheet)
        self.__admins = self.__get_all_values(self.__admins_worksheet)

    def add_admin(self, user_name, user_id):
        last_row = len(self.__admins)
        new_row = [user_name, user_id]
        self.__admins_worksheet.insert_rows(row=last_row, values=new_row)
        self.__admins = self.__get_all_values(self.__admins_worksheet)

    def get_admins(self):
        admins = self.__admins[1:]
        return admins
