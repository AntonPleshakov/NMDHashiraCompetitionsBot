import logging

from config.config import config, MODE
from logger.RotatingGDriveHandler import RotatingGDriveHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NMDHashiraBot")

fmt = config[MODE]["LOG_FORMAT"]
date_fmt = config[MODE]["LOG_DATE_FORMAT"]
handler = RotatingGDriveHandler(
    config[MODE]["LOG_FILE_NAME"], max_bytes=10000, backup_count=10
)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(fmt, date_fmt))
logger.addHandler(handler)
