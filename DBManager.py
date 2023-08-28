import pygsheets
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
        client = pygsheets.authorize(service_file="nmdhashiracompetitionsbot-9ace8e5ff078.json")

        admins_ss = client.open(config[MODE]['ADMINS_GTABLE_NAME'])
        self.__admins_worksheet = admins_ss[0]
        self.__admins = self.__get_all_values(self.__admins_worksheet)

    def add_admin(self, user_name, user_id):
        last_row = len(self.__admins)
        new_row = [user_name, user_id]
        self.__admins_worksheet.insert_rows(row=last_row, values=new_row)
        self.__admins = self.__get_all_values(self.__admins_worksheet)

    def get_admins(self):
        admins = self.__admins[1:]
        return admins
