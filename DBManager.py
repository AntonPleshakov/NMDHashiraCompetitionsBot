import json
import os

import pygsheets
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from ConfigManager import config, MODE


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
        )

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

    def add_admin(self, user_name, user_id):
        last_row = len(self.__admins)
        new_row = [user_name, user_id]
        self.__admins_worksheet.insert_rows(row=last_row, values=new_row)
        self.__admins.append(new_row)

    def get_admins(self):
        admins = self.__admins[1:]
        return admins

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
