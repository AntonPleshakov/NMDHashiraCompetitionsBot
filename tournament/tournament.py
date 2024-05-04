from enum import Enum

from db.ratings import ratings_db
from db.tournament import TournamentDB
from db.tournament_structures import RegistrationRow
from nmd_exceptions import (
    TournamentStartedError,
    TournamentFinishedError,
    MatchWithPlayersNotFound,
    MatchResultWasAlreadyRegistered,
    PlayerNotFoundError,
)
from .mcmahon_pairing import McMahonPairing
from .player import Player


class TournamentState(Enum):
    REGISTRATION = 0
    IN_PROGRESS = 1
    FINISHED = 2


class Tournament:
    def __init__(self, tournament_db: TournamentDB):
        self.db: TournamentDB = tournament_db
        self._state: TournamentState = (
            TournamentState.IN_PROGRESS
            if self.db.get_tours_number() > 0
            else TournamentState.REGISTRATION
        )

        players_list = self.db.get_registered_players()
        previous_tours = []
        for i in range(self.db.get_tours_number() - 1):
            previous_tours.append(self.db.get_results(i))
        self._pairing: McMahonPairing = McMahonPairing(players_list, previous_tours)

    def new_round(self):
        if self._state == TournamentState.FINISHED:
            raise TournamentFinishedError
        self._pairing.update_coefficients(
            self.db.get_results(), self.db.get_tours_number()
        )
        pairs = self._pairing.gen_pairs()
        self.db.start_new_tour(pairs)
        self._state = TournamentState.IN_PROGRESS

    def add_player(self, player: Player):
        if self._state != TournamentState.REGISTRATION:
            raise TournamentStartedError
        rating = ratings_db.get_rating(player.tg_id)
        if not rating:
            raise PlayerNotFoundError
        self.db.register_player(RegistrationRow.from_rating(rating))
        self._pairing.add_player(player)

    def update_player_info(self, player: RegistrationRow):
        if self._state != TournamentState.REGISTRATION:
            raise TournamentStartedError
        self.db.register_player(player)

    def add_result(
        self,
        user_id: int,
        won: bool,
        force_update: bool = False,
    ):
        match_index = None
        match = None
        for i, result in enumerate(self.db.get_results()):
            if (result.first_id == user_id) or (result.second_id == user_id):
                match_index = i
                match = result
                break
        if not match_index:
            raise MatchWithPlayersNotFound
        if match.result.value != "-" and not force_update:
            raise MatchResultWasAlreadyRegistered
        # swap result in case of players swapped
        result = "0:1"
        if match.first_id == user_id and won:
            result = "1:0"
        elif match.second_id == user_id and not won:
            result = "1:0"
        self.db.register_result(match_index, result)

    def finish_tournament(self):
        self._pairing.update_coefficients(
            self.db.get_results(), self.db.get_tours_number()
        )
        self._state = TournamentState.FINISHED
