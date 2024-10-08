from enum import Enum
from typing import List

from db.ratings import ratings_db, Rating
from db.tournament import TournamentDB
from db.tournament_structures import RegistrationRow, Match
from logger.NMDLogger import nmd_logger
from nmd_exceptions import (
    TournamentStartedError,
    TournamentFinishedError,
    MatchWithPlayersNotFound,
    MatchResultWasAlreadyRegistered,
    PlayerNotFoundError,
    MatchResultTryingToBeChanged,
    TechWinCannotBeChanged,
    TournamentNotStartedError,
)
from tg.utils import get_player_rating_view
from tournament.mcmahon.mcmahon_pairing import McMahonPairing
from tournament.ratings_math import update_player_with_rating
from .player import Player


class TournamentState(Enum):
    REGISTRATION = 0
    IN_PROGRESS = 1
    FINISHED = 2


class Tournament:
    def __init__(self, tournament_db: TournamentDB):
        nmd_logger.info("Tournament is created")
        self.db: TournamentDB = tournament_db
        self._state: TournamentState = (
            TournamentState.IN_PROGRESS
            if self.db.get_tours_number() > 0
            else TournamentState.REGISTRATION
        )
        nmd_logger.info(f"Current state is {self._state.name}")

        self._pairing: McMahonPairing = None
        self.restore_pairing()

    @property
    def state(self) -> TournamentState:
        return self._state

    def _set_map_difficulty(self, pairs: List[Match]):
        unrivaled = self.db.settings.unrivaled_matches.value
        nightmare = self.db.settings.nightmare_matches.value
        dangerous = self.db.settings.dangerous_matches.value
        nightmare_idx = unrivaled + nightmare
        dangerous_idx = nightmare_idx + dangerous
        for p in pairs[0:unrivaled]:
            p.map.set_value("Unrivaled")
        for p in pairs[unrivaled:nightmare_idx]:
            p.map.set_value("Nightmare")
        for p in pairs[nightmare_idx:dangerous_idx]:
            p.map.set_value("Dangerous")
        for p in pairs[dangerous_idx:]:
            p.map.set_value("Hard")

        bo3_matches = self.db.settings.bo3_matches.value
        for p in pairs[0:bo3_matches]:
            p.rounds.value = 3
        for p in pairs[bo3_matches:]:
            p.rounds.value = 1

    def restore_pairing(self):
        registrations = self.db.get_registered_players()
        players: List[Player] = []
        for reg_row in registrations:
            rating = ratings_db.get_rating(reg_row.tg_id.value)
            players.append(Player.from_rating(rating))
        previous_tours = []
        for i in range(self.db.get_tours_number()):
            previous_tours.append(self.db.get_results(i))
        self._pairing = McMahonPairing(players, previous_tours)

    def get_players(self) -> List[Player]:
        return self._pairing.get_players()

    def new_round(self) -> List[Match]:
        nmd_logger.info("New round start")
        if self._state == TournamentState.FINISHED:
            nmd_logger.error("Tournament state is Finished, exception")
            raise TournamentFinishedError
        if self._state == TournamentState.IN_PROGRESS:
            nmd_logger.info("Update coefficients with results of last round")
            self._pairing.update_coefficients(self.db.get_results())
        pairs = self._pairing.gen_pairs()
        self._set_map_difficulty(pairs)

        self.db.start_new_tour(pairs)
        self._state = TournamentState.IN_PROGRESS
        return pairs

    def add_player(self, player: Player):
        nmd_logger.info(f"Try to register new player: {player.username}")
        if self._state != TournamentState.REGISTRATION:
            nmd_logger.error("Tournament state is not in registration, exception")
            raise TournamentStartedError
        rating = ratings_db.get_rating(player.tg_id)
        if not rating:
            nmd_logger.error("Rating not found, exception")
            raise PlayerNotFoundError
        nmd_logger.info(f"Player rating {get_player_rating_view(rating)}")
        registration_row = RegistrationRow.from_rating(rating)
        self.db.register_player(registration_row)
        self._pairing.add_player(player)

    def remove_player(self, player_id: int):
        nmd_logger.info(f"Try to remove a player. id: {player_id}")
        if self._state != TournamentState.REGISTRATION:
            nmd_logger.error("Tournament state is not in registration, exception")
            raise TournamentStartedError
        self.db.unregister_player(player_id)
        self._pairing.remove_player(player_id)

    def update_player_info(self, player: Rating):
        nmd_logger.info(f"Update player info {get_player_rating_view(player)}")
        if self._state != TournamentState.REGISTRATION:
            nmd_logger.error("Can't update player info not in registration, exception")
            raise TournamentStartedError
        self.db.register_player(RegistrationRow.from_rating(player))
        self._pairing.add_player(Player.from_rating(player))

    def add_result(
        self,
        user_id: int,
        won: bool,
        force_update: bool = False,
    ):
        nmd_logger.info(
            f"Register result of user {user_id}, won: {won}, force_update: {force_update}"
        )
        match_index = None
        match = None
        for i, result in enumerate(self.db.get_results()):
            if (result.first_id.value == user_id) or (
                result.second_id.value == user_id
            ):
                match_index = i
                match = result
                break
        if match_index is None:
            nmd_logger.error("No match found with the user, exception")
            raise MatchWithPlayersNotFound
        if not match.second.value:
            nmd_logger.info("Match of one player, raise exception")
            raise TechWinCannotBeChanged

        # swap result in case of players swapped
        new_result = Match.MatchResult.SecondWon
        if match.first_id.value == user_id and won:
            new_result = Match.MatchResult.FirstWon
        elif match.second_id.value == user_id and not won:
            new_result = Match.MatchResult.FirstWon

        old_result: Match.MatchResult = Match.STR_TO_MATCH_RESULT[match.result_str]
        if old_result != Match.MatchResult.NotPlayed:
            if old_result == new_result:
                nmd_logger.info("Same result was already registered")
                raise MatchResultWasAlreadyRegistered
            elif not force_update:
                nmd_logger.warning(
                    f"Result mismatch, old: {old_result.name}, new: {new_result.name}"
                )
                raise MatchResultTryingToBeChanged
        self.db.register_result(match_index, Match.MATCH_RESULT_TO_STR[new_result])

    @staticmethod
    def _update_ratings_db(players: List[Player]):
        ratings = ratings_db.get_ratings()
        ratings_id_to_index = {r.tg_id.value: i for i, r in enumerate(ratings)}

        for player in players:
            rating: Rating
            index: int
            if player.tg_id in ratings_id_to_index:
                nmd_logger.info(f"Player {player.username} exist in ratings db")
                index = ratings_id_to_index[player.tg_id]
                rating = ratings[index]
            else:
                nmd_logger.warning(
                    f"Player {player.username} doesn't exist in ratings db"
                )
                rating = Rating.default(player.tg_id)
                ratings.append(rating)
                index = len(ratings) - 1
                ratings_id_to_index[player.tg_id] = index
            rating.rating.value = player.rating
            rating.deviation.value = player.deviation
            rating.update_date()
            ratings[index] = rating

        ratings_db.update_all_user_ratings(ratings)

    def finish_tournament(self, should_update_coefficients):
        nmd_logger.info("Finish tournament")
        self._state = TournamentState.FINISHED
        if should_update_coefficients:
            try:
                self._pairing.update_coefficients(self.db.get_results())
            except TournamentNotStartedError:
                self.db.finish_tournament([])
                raise
        players = self._pairing.get_players()

        result_list = []
        for i, player in enumerate(players):
            old_rating = player.rating
            update_player_with_rating(player)

            registration = self.db.get_registered_player(player.tg_id)
            result = player.to_result(i + 1, registration)
            result.rating.value = f"{old_rating} -> {player.rating}"
            result_list.append(result)

        self._update_ratings_db(players)
        self.db.finish_tournament(result_list)
