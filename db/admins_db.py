from typing import Set, List

from config.config import getconf
from db.gapi.gsheets_manager import GSheetsManager
from db.gapi.worksheet_manager import WorksheetManager


class Admin:
    def __init__(self, username: str, user_id: int):
        self.username: str = username
        self.user_id: int = user_id

    def __eq__(self, other):
        username = self.username == other.username
        user_id = self.user_id == other.user_id
        return username and user_id

    def to_list(self) -> List[str]:
        return [self.username, self.user_id]


class AdminsDB:
    def __init__(self):
        ss_name = getconf("ADMINS_GTABLE_KEY")
        ws_name = getconf("ADMINS_PAGE_NAME")

        self._manager: WorksheetManager = (
            GSheetsManager().open(ss_name).get_worksheet(ws_name)
        )
        admins_matrix = self._manager.get_all_values()[1:]
        self._admins_id_set: Set[int] = {int(row[1]) for row in admins_matrix}
        self._admins: List[Admin] = [
            Admin(row[0], int(row[1])) for row in admins_matrix
        ]

    def add_admin(self, new_admin: Admin):
        self._manager.add_row(new_admin.to_list())
        self._admins.append(new_admin)
        self._admins_id_set.add(new_admin.user_id)

    def get_admins(self) -> List[Admin]:
        return self._admins

    def is_admin(self, user_id: int):
        return user_id in self._admins_id_set

    def del_admin(self, user_id: str):
        admins = self.get_admins()
        new_admins = [admin.to_list() for admin in admins if admin.user_id != user_id]
        self._manager.update_values(new_admins)
        self._admins = [admin for admin in admins if admin.user_id != user_id]
        self._admins_id_set = {admin.user_id for admin in self._admins}

    def fetch_admins(self):
        self._manager.fetch()
        admins_matrix = self._manager.get_all_values()[1:]
        self._admins_id_set: Set[int] = {int(row[1]) for row in admins_matrix}
        self._admins: List[Admin] = [
            Admin(row[0], int(row[1])) for row in admins_matrix
        ]


admins_db = AdminsDB()
