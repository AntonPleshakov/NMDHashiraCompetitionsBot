from enum import Enum
from typing import List, Dict

from db.ratings_db import RatingsDB
from db.tournament_db import TournamentDB
from match import MatchResult
from mcmahon_pairing import McMahonPairing
from nmd_exceptions import TournamentStartedError, TournamentFinishedError
from player import Player


class TournamentState(Enum):
    REGISTRATION = 0
    IN_PROGRESS = 1
    FINISHED = 2


class Tournament:
    def __init__(self):
        tournament_db = TournamentDB.get_latest_tournament()
        if not tournament_db or tournament_db.is_finished():
            tournament_db = TournamentDB.create_new_tournament()
        self._tournament_db: TournamentDB = tournament_db
        ratings = RatingsDB().get_ratings()
        self._players: Dict[str, Player] = {
            player.tg_username: player for player in ratings
        }
        self._state: TournamentState = (
            TournamentState.IN_PROGRESS
            if self._tournament_db.get_tours_number() > 0
            else TournamentState.REGISTRATION
        )

        players_list = self._tournament_db.get_registered_players()
        previous_tours = []
        for i in range(self._tournament_db.get_tours_number() - 1):
            previous_tours.append(self._tournament_db.get_results(i))
        self._pairing: McMahonPairing = McMahonPairing(players_list, previous_tours)

    def new_round(self):
        if self._state == TournamentState.FINISHED:
            raise TournamentFinishedError
        self._pairing.update_coefficients(
            self._tournament_db.get_results(), self._tournament_db.get_tours_number()
        )
        pairs = self._pairing.gen_pairs()
        self._tournament_db.start_new_tour(pairs)
        self._state = TournamentState.IN_PROGRESS

    def add_player(self, player_tg_username: str):
        if self._state != TournamentState.REGISTRATION:
            raise TournamentStartedError
        if player_tg_username not in self._players:
            new_player = Player(player_tg_username)
            RatingsDB().add_user_rating(new_player)
            self._players[player_tg_username] = new_player
        player = self._players[player_tg_username]
        self._tournament_db.register_player(player)
        self._pairing.add_player(player)

    def add_result(self, players_tg_name: List[str], result: MatchResult):
        if len(players_tg_name) != 2:
            raise KeyError("Error: only 2 players in pair accepted")
        pairs = self._tournament_db.get_results()
        for i, match in enumerate(pairs):
            if match.first_player.tg_username in players_tg_name:
                if match.second_player.tg_username not in players_tg_name:
                    raise KeyError("Error: wrong pair")
                # swap result in case of players swapped
                if match.first_player.tg_username == players_tg_name[1] and result in [
                    MatchResult.FirstWon,
                    MatchResult.SecondWon,
                ]:
                    result = (
                        MatchResult.FirstWon
                        if result == MatchResult.SecondWon
                        else MatchResult.SecondWon
                    )
                self._tournament_db.register_result(i, result)
                return

    def finish_tournament(self):
        self._pairing.update_coefficients(
            self._tournament_db.get_results(), self._tournament_db.get_tours_number()
        )
        self._state = TournamentState.FINISHED
