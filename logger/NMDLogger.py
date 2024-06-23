import logging

from config.config import getconf
from .RotatingGDriveHandler import RotatingGDriveHandler

logging.basicConfig(level=logging.INFO)

fmt = getconf("LOG_FORMAT")
date_fmt = getconf("LOG_DATE_FORMAT")

gdrive_handler = RotatingGDriveHandler(
    getconf("LOG_FILE_NAME"), max_bytes=10000, backup_count=10
)
gdrive_handler.setLevel(logging.INFO)
gdrive_handler.setFormatter(logging.Formatter(fmt, date_fmt))

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter(fmt, date_fmt))

nmd_logger = logging.getLogger("NMDHashiraBot")
nmd_logger.addHandler(gdrive_handler)
nmd_logger.addHandler(stream_handler)
nmd_logger.setLevel(logging.INFO)

bot_logger = logging.getLogger("TeleBot")
bot_logger.addHandler(gdrive_handler)
bot_logger.setLevel(logging.INFO)
