import configparser
import os

_MODE = os.getenv("MODE", "Debug")
_config = configparser.ConfigParser()
_config.read("config/config.ini", encoding="utf-8")


def getconf(option: str) -> str:
    return _config.get(_MODE, option)


def reset_config(filepath: str):
    _config.read(filepath, encoding="utf-8")
