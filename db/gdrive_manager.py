import json

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from config.config import config, MODE


class GDriveManager:
    def __init__(self):
        with open("../gapi_service_file.json", "r") as service_file:
            service_dict = json.load(service_file)
        gauth_settings = {
            "service_config": {
                "client_json_dict": service_dict,
                "client_user_email": config[MODE]["GSERVICE_EMAIL"],
            }
        }
        gauth = GoogleAuth(settings=gauth_settings)
        gauth.ServiceAuth()
        self._drive = GoogleDrive(gauth)
        self._files = {}
        self._folder_path = config[MODE]["GDRIVE_FOLDER_PATH"]

    def create_file(self, file_name):
        file = self._drive.CreateFile(
            {"parents": [{"id": self._folder_path}], "title": file_name}
        )
        self._files[file_name] = file

        return file

    def get_file(self, file_name):
        if file_name not in self._files:
            return self.create_file(file_name)
        else:
            return self._files[file_name]

    def rename_file(self, old_name, new_name):
        file = self.get_file(old_name)
        file["title"] = new_name
        file.Upload()

        self._files[new_name] = self._files.pop(old_name)

    def delete_file(self, file_name):
        file = self.get_file(file_name)
        file.Delete()

        self._files.pop(file_name)

    def is_file_exists(self, file_name):
        files_in_account = self._drive.ListFile()
        files_in_main_folder = []
        for file in files_in_account.GetList():
            for parent in file["parents"]:
                if self._folder_path in parent["selfLink"]:
                    files_in_main_folder.append(file["title"])
                    break
        return file_name in files_in_main_folder
