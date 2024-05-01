from datetime import date
from typing import List, Optional

from config.config import getconf
from nmd_exceptions import PlayerNotFoundError, TournamentNotStartedError
from tournament.tournament_settings import TournamentSettings
from .gapi.gsheets_manager import GSheetsManager
from .gapi.spreadsheet_manager import SpreadsheetManager
from .gapi.worksheet_manager import WorksheetManager
from .tournament_structures import RegistrationRow, Match, Result


class TournamentDB:
    def __init__(self, spreadsheet_manager: SpreadsheetManager):
        self._manager: SpreadsheetManager = spreadsheet_manager
        settings_page_name = getconf("TOURNAMENT_SETTINGS_PAGE_NAME")
        settings_page = self._manager.get_worksheet(settings_page_name)
        self._settings: TournamentSettings = TournamentSettings.from_matrix(
            settings_page.get_all_values()
        )
        self._registration_page: WorksheetManager = self._manager.get_worksheet(
            getconf("TOURNAMENT_REGISTER_PAGE_NAME")
        )
        self._tours: List[WorksheetManager] = []
        self._results_page: Optional[WorksheetManager] = None

    @classmethod
    def create_new_tournament(cls, settings: TournamentSettings):
        spreadsheet_name = (
            getconf("TOURNAMENT_GTABLE_NAME") + " " + date.today().strftime("%d.%m.%Y")
        )
        manager = GSheetsManager().create(spreadsheet_name)
        settings_page = manager.rename_worksheet(
            getconf("TOURNAMENT_SETTINGS_PAGE_NAME")
        )
        settings_page.update_values(settings.to_matrix())
        registration_page = manager.add_worksheet(
            getconf("TOURNAMENT_REGISTER_PAGE_NAME")
        )
        registration_page.set_header([RegistrationRow().params_views()])
        return cls(manager)

    @classmethod
    def get_latest_tournament(cls):
        conf_ss_name = getconf("TOURNAMENT_GTABLE_NAME")
        manager = GSheetsManager()
        tournaments_ss = [
            ss for ss in manager.get_spreadsheets() if conf_ss_name in ss.name
        ]
        if not tournaments_ss:
            return None

        latest_date = None
        latest_ss = None
        for ss in tournaments_ss:
            date_list = ss.name.split()[-1].split(".")
            ss_date = date(int(date_list[2]), int(date_list[1]), int(date_list[0]))
            if latest_date is None or latest_date < ss_date:
                latest_date = ss_date
                latest_ss = ss
        ss = manager.open(latest_ss.id)
        return TournamentDB(ss)

    def register_player(self, player: RegistrationRow):
        self._registration_page.add_row(player.to_row())
        self._registration_page.sort_table(player.rating.index)

    def get_registered_players(self) -> List[RegistrationRow]:
        matrix = self._registration_page.get_all_values()
        players = [RegistrationRow.from_row(row) for row in matrix]
        return players

    def update_player_info(self, player: RegistrationRow):
        players = self.get_registered_players()
        player_indexes = [
            i for i, v in enumerate(players) if v.tg_username == player.tg_username
        ]
        if not player_indexes:
            raise PlayerNotFoundError
        row = player_indexes[0] + 2  # starting from 1 plus header
        start_range = (row, 1)
        self._registration_page.update_values(
            [player.to_row()], start_range=start_range
        )
        self._registration_page.sort_table(player.rating.index)

    def start_new_tour(self, pairs: List[Match]):
        tour_number = len(self._tours) + 1
        tour_title = getconf("TOURNAMENT_TOUR_PAGE_NAME") + " " + str(tour_number)
        tour_page = self._manager.add_worksheet(tour_title)
        tour_page.set_header([Match().params_views()])
        matrix = [match.to_row() for match in pairs]
        tour_page.update_values(matrix)
        self._tours.append(tour_page)

    def register_result(self, pair_index: int, result: str):
        if not self._tours:
            raise TournamentNotStartedError
        tour = self._tours[-1]
        start_range = (pair_index + 2, Match().result.index + 1)
        tour.update_values([[result]], start_range=start_range)

    def get_results(self, tour_idx: int = -1) -> List[Match]:
        if not self._tours:
            raise TournamentNotStartedError
        tour = self._tours[tour_idx]
        matrix = tour.get_all_values()
        results = [Match.from_row(row) for row in matrix]
        return results

    def get_tours_number(self) -> int:
        return len(self._tours)

    def finish_tournament(self, tournament_table: List[Result]):
        results_title = getconf("TOURNAMENT_RESULTS_PAGE_NAME")
        results_page = self._manager.add_worksheet(results_title)
        results_page.set_header([Result().params_views()])
        matrix = [player.to_row() for player in tournament_table]
        results_page.update_values(matrix)
        self._results_page = results_page

    def is_finished(self) -> bool:
        return self._results_page is not None

    @property
    def settings(self) -> TournamentSettings:
        return self._settings
