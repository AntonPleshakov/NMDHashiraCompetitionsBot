import json
import os

import pygsheets
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from ConfigManager import config, MODE


class UsernameAlreadyExistsError(Exception):
    pass


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DBManager(metaclass=Singleton):
    @staticmethod
    def __get_all_values(worksheet):
        return worksheet.get_all_values(
            include_tailing_empty_rows=False, include_tailing_empty=False
        )[1:]

    @staticmethod
    def add_row(worksheet, ws_values, row):
        last_row = len(ws_values) + 1
        worksheet.insert_rows(row=last_row, values=row)
        ws_values.append(row)

    def __init__(self):
        sheets_client = pygsheets.authorize(
            service_file="nmdhashiracompetitionsbot-9ace8e5ff078.json"
        )

        with open("nmdhashiracompetitionsbot-9ace8e5ff078.json", "r") as service_file:
            service_dict = json.load(service_file)
        gauth_settings = {
            "service_config": {
                "client_json_dict": service_dict,
                "client_user_email": config[MODE]["GSERVICE_EMAIL"],
            }
        }
        gauth = GoogleAuth(settings=gauth_settings)
        gauth.ServiceAuth()
        self.__drive = GoogleDrive(gauth)
        self.__files = {}

        admins_ss = sheets_client.open(config[MODE]["ADMINS_GTABLE_NAME"])
        self.__admins_worksheet = admins_ss[0]
        self.__admins = self.__get_all_values(self.__admins_worksheet)

        ratings_ss = sheets_client.open(config[MODE]["RATING_LIST_GTABLE_NAME"])
        self.__ratings_worksheet = ratings_ss[0]
        self.__ratings = self.__get_all_values(self.__ratings_worksheet)

    def add_admin(self, user_name, user_id):
        self.add_row(self.__admins_worksheet, self.__admins, [user_name, user_id])

    def get_admins(self):
        return self.__admins

    def add_user_rating(
        self,
        tg_username,
        nmd_username="",
        rating=100,
        deviation=200,
        attack=0,
        arena_place=0,
    ):
        if any(tg_username == rating[0] for rating in self.__ratings):
            raise UsernameAlreadyExistsError

        new_row = [tg_username, nmd_username, rating, deviation, attack, arena_place]
        self.add_row(self.__ratings_worksheet, self.__ratings, new_row)

        # pygsheets decrement start indexes by 1, but not decrement end indexes
        # 1 row must be indented for a header
        start_range = (2, 1)
        end_range = (len(self.__ratings) + 1, len(self.__ratings[0]))
        sort_column_index = 2
        self.__ratings_worksheet.sort_range(
            start_range, end_range, sort_column_index, "DESCENDING"
        )
        self.__ratings.sort(key=lambda x: x[sort_column_index])

    def update_all_user_ratings(self, ratings):
        sort_column_index = 2
        ratings.sort(key=lambda x: x[sort_column_index])
        self.__ratings_worksheet.update_values((2, 1), ratings, extend=True)
        self.__ratings = ratings

    def get_ratings(self):
        return self.__ratings

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

    def create_file(self, file_name):
        folder_path = config[MODE]["GDRIVE_FOLDER_PATH"]
        file = self.__drive.CreateFile(
            {"parents": [{"id": folder_path}], "title": file_name}
        )
        self.__files[file_name] = file

        return file

    def get_file(self, file_name):
        if file_name not in self.__files:
            self.create_file(file_name)

        return self.__files[file_name]

    def rename_file(self, old_name, new_name):
        file = self.get_file(old_name)
        file["title"] = new_name
        file.Upload()

        self.__files[new_name] = self.__files.pop(old_name)

    def delete_file(self, file_name):
        file = self.get_file(file_name)
        file.Delete()

        self.__files.pop(file_name)

    def is_file_exists(self, file_name):
        folder_path = config[MODE]["GDRIVE_FOLDER_PATH"]
        files = self.__drive.ListFile()
        titles = []
        for file in files.GetList():
            for parent in file["parents"]:
                if folder_path in parent["selfLink"]:
                    titles.append(file["title"])
                    break
        return file_name in titles

    def upload_log_file(self, file_path):
        file = self.get_file(os.path.basename(file_path))
        file.SetContentFile(file_path)
        file.Upload()
