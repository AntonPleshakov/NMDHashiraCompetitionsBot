import logging

from config.config import getconf
from .RotatingGDriveHandler import RotatingGDriveHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NMDHashiraBot")

fmt = getconf("LOG_FORMAT")
date_fmt = getconf("LOG_DATE_FORMAT")
handler = RotatingGDriveHandler(
    getconf("LOG_FILE_NAME"), max_bytes=10000, backup_count=10
)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(fmt, date_fmt))
logger.addHandler(handler)
