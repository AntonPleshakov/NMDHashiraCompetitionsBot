from datetime import datetime
from typing import List, Optional

from config.config import getconf
from db.gapi.gsheets_manager import GSheetsManager
from db.gapi.spreadsheet_manager import SpreadsheetManager
from db.gapi.worksheet_manager import WorksheetManager
from nmd_exceptions import PlayerNotFoundError
from tournament.match import Match, MatchResult, MATCH_RESULT_TO_STR, MatchColumnIndexes
from tournament.player import Player, PlayerColumnIndexes


class TournamentDB:
    def __init__(self, spreadsheet_manager: SpreadsheetManager):
        self._manager: SpreadsheetManager = spreadsheet_manager
        self._registration_page: WorksheetManager = self._manager.get_worksheet(
            getconf("TOURNAMENT_REGISTER_PAGE_NAME")
        )
        self._registration_page.set_header([Player.PLAYER_FIELDS])
        self._tours: List[WorksheetManager] = []
        self._results_page: Optional[WorksheetManager] = None

    @classmethod
    def create_new_tournament(cls):
        date = datetime.today().strftime("%d.%m.%Y")
        spreadsheet_name = getconf("TOURNAMENT_GTABLE_NAME") + " " + date
        manager = GSheetsManager().create(spreadsheet_name)
        manager.rename_worksheet(getconf("TOURNAMENT_REGISTER_PAGE_NAME"))
        return cls(manager)

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
            return
        tour = self._tours[-1]
        start_range = (pair_index + 2, MatchColumnIndexes.RESULT.value + 1)
        tour.update_values([[MATCH_RESULT_TO_STR[result]]], start_range=start_range)

    def get_results(self) -> List[Match]:
        if not self._tours:
            return []
        tour = self._tours[-1]
        matrix = tour.get_all_values()[1:]
        results = [Match.from_list(row) for row in matrix]
        return results

    def finish_tournament(self, tournament_table: List[Player]):
        results_title = getconf("TOURNAMENT_RESULTS_PAGE_NAME")
        results_page = self._manager.add_worksheet(results_title)
        results_page.set_header([Player.PLAYER_FIELDS])
        matrix = [player.to_list() for player in tournament_table]
        results_page.update_values(matrix)
        self._results_page = results_page
