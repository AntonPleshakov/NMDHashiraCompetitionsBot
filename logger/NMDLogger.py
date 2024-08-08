import logging
import sys

from config.config import getconf
from .RotatingGDriveHandler import RotatingGDriveHandler

fmt = getconf("LOG_FORMAT")
date_fmt = getconf("LOG_DATE_FORMAT")

gdrive_handler = RotatingGDriveHandler(
    getconf("LOG_FILE_NAME"), max_bytes=100000, backup_count=5
)
gdrive_handler.setLevel(logging.DEBUG)
gdrive_handler.setFormatter(logging.Formatter(fmt, date_fmt))

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter(fmt, date_fmt))

nmd_logger = logging.getLogger("NMDHashiraBot")
nmd_logger.addHandler(stream_handler)
nmd_logger.addHandler(gdrive_handler)
nmd_logger.setLevel(logging.DEBUG)

bot_logger = logging.getLogger("TeleBot")
bot_logger.addHandler(gdrive_handler)
bot_logger.setLevel(logging.INFO)
