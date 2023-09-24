from datetime import datetime
from typing import List

from config.config import getconf
from db.gapi.gsheets_manager import GSheetsManager
from db.gapi.spreadsheet_manager import SpreadsheetManager
from tournament.match import Match, MatchResult
from tournament.player import Player


class TournamentDB:
    def __init__(self, spreadsheet_manager: SpreadsheetManager):
        self._manager: SpreadsheetManager = spreadsheet_manager

    @classmethod
    def create_new_tournament(cls):
        date = datetime.today().strftime("%d.%m.%Y")
        spreadsheet_name = getconf("TOURNAMENT_GTABLE_NAME") + " " + date
        manager = GSheetsManager().create(spreadsheet_name)
        return cls(manager)

    def register_player(self, player: Player):
        pass

    def get_registered_players(self) -> List[Player]:
        pass

    def update_player_info(self, player: Player):
        pass

    def start_new_tour(self, pairs: List[Match]):
        pass

    def register_result(self, pair_index: int, result: MatchResult):
        pass

    def get_results(self) -> List[Match]:
        pass

    def finish_tournament(self, tournament_table: List[Player]):
        pass
