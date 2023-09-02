import os
from logging.handlers import RotatingFileHandler

import db.logs


class RotatingGDriveHandler(RotatingFileHandler):
    def __init__(self, filename, max_bytes=0, backup_count=0, delay=False):
        super().__init__(
            filename, maxBytes=max_bytes, backupCount=backup_count, delay=delay
        )

    def doRollover(self):
        super().doRollover()
        logs_db = db.logs.Logs()
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                old_name = os.path.basename(
                    self.rotation_filename("%s.%d" % (self.baseFilename, i))
                )
                new_name = os.path.basename(
                    self.rotation_filename("%s.%d" % (self.baseFilename, i + 1))
                )
                if logs_db.is_file_exists(new_name):
                    logs_db.delete_file(new_name)
                if logs_db.is_file_exists(old_name):
                    logs_db.rename_file(old_name, new_name)
            logs_db.upload_log_file(self.baseFilename + ".1")
