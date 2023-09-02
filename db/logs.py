import os

from gdrive_manager import GDriveManager


class Logs(GDriveManager):
    def upload_log_file(self, file_path):
        file = self.get_file(os.path.basename(file_path))
        file.SetContentFile(file_path)
        file.Upload()
