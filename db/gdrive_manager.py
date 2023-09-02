import json
import os

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from config.config import config, MODE


class GDriveManager:
    def __init__(self):
        with open("gapi_service_file.json", "r") as service_file:
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

    def _create_file(self, file_name):
        file = self._drive.CreateFile(
            {"parents": [{"id": self._folder_path}], "title": file_name}
        )
        self._files[file_name] = file

        return file

    def _get_file(self, file_name):
        param = {"q": f"title='{file_name}' and '{self._folder_path}' in parents"}
        files_result = self._drive.ListFile(param).GetList()
        if not files_result:
            return None

        file = files_result[0]
        self._files[file_name] = file
        return file

    def file(self, file_name):
        if file_name in self._files:
            return self._files[file_name]

        file = self._get_file(file_name)
        if file:
            return file
        else:
            return self._create_file(file_name)

    def rename_file(self, old_name, new_name):
        file = self.file(old_name)
        file["title"] = new_name
        file.Upload()

        self._files[new_name] = self._files.pop(old_name)

    def delete_file(self, file_name):
        file = self.file(file_name)
        file.Delete()

        self._files.pop(file_name)

    def is_file_exists(self, file_name):
        param = {"q": f"title='{file_name}' and '{self._folder_path}' in parents"}
        files_result = self._drive.ListFile(param).GetList()
        return len(files_result) > 0

    def download_file(self, gdrive_path, local_path):
        file = self.file(gdrive_path)
        file.GetContentFile(local_path)

    def upload_file(self, file_path):
        file = self.file(os.path.basename(file_path))
        file.SetContentFile(file_path)
        file.Upload()
