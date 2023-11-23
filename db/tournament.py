from datetime import date
from typing import List, Optional

from config.config import getconf
from nmd_exceptions import PlayerNotFoundError, TournamentNotStartedError
from tournament.match import Match, MatchResult, MATCH_RESULT_TO_STR, MatchColumnIndexes
from tournament.player import Player, PlayerColumnIndexes
from tournament.tournament_settings import TournamentSettings
from .gapi.gsheets_manager import GSheetsManager
from .gapi.spreadsheet_manager import SpreadsheetManager
from .gapi.worksheet_manager import WorksheetManager


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
        registration_page.set_header([Player.PLAYER_FIELDS])
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

    def register_player(self, player: Player):
        self._registration_page.add_row(player.to_list())
        self._registration_page.sort_table(PlayerColumnIndexes.RATING.value)

    def get_registered_players(self) -> List[Player]:
        matrix = self._registration_page.get_all_values()[1:]
        players = [Player.from_list(row) for row in matrix]
        return players

    def update_player_info(self, player: Player):
        players = self.get_registered_players()
        player_indexes = [
            i for i, v in enumerate(players) if v.tg_username == player.tg_username
        ]
        if not player_indexes:
            raise PlayerNotFoundError
        row = player_indexes[0] + 2  # starting from 1 plus header
        start_range = (row, 1)
        self._registration_page.update_values(
            [player.to_list()], start_range=start_range
        )
        self._registration_page.sort_table(PlayerColumnIndexes.RATING.value)

    def start_new_tour(self, pairs: List[Match]):
        tour_number = len(self._tours) + 1
        tour_title = getconf("TOURNAMENT_TOUR_PAGE_NAME") + " " + str(tour_number)
        tour_page = self._manager.add_worksheet(tour_title)
        tour_page.set_header([Match.MATCH_FIELDS])
        matrix = [match.to_list() for match in pairs]
        tour_page.update_values(matrix)
        self._tours.append(tour_page)

    def register_result(self, pair_index: int, result: MatchResult):
        if not self._tours:
            raise TournamentNotStartedError
        tour = self._tours[-1]
        start_range = (pair_index + 2, MatchColumnIndexes.RESULT.value + 1)
        tour.update_values([[MATCH_RESULT_TO_STR[result]]], start_range=start_range)

    def get_results(self, tour_idx: int = -1) -> List[Match]:
        if not self._tours:
            raise TournamentNotStartedError
        tour = self._tours[tour_idx]
        matrix = tour.get_all_values()[1:]
        results = [Match.from_list(row) for row in matrix]
        return results

    def get_tours_number(self) -> int:
        return len(self._tours)

    def finish_tournament(self, tournament_table: List[Player]):
        results_title = getconf("TOURNAMENT_RESULTS_PAGE_NAME")
        results_page = self._manager.add_worksheet(results_title)
        results_page.set_header([Player.PLAYER_FIELDS])
        matrix = [player.to_list() for player in tournament_table]
        results_page.update_values(matrix)
        self._results_page = results_page

    def is_finished(self) -> bool:
        return self._results_page is not None
