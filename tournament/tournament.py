from enum import Enum
from typing import List

from db.ratings import ratings_db, Rating
from db.tournament import TournamentDB
from db.tournament_structures import RegistrationRow, Match, Result
from logger.NMDLogger import nmd_logger
from nmd_exceptions import (
    TournamentStartedError,
    TournamentFinishedError,
    MatchWithPlayersNotFound,
    MatchResultWasAlreadyRegistered,
    PlayerNotFoundError,
    MatchResultTryingToBeChanged,
)
from tg.utils import get_player_rating_view
from .deviation_math import recalc_deviation_by_time, calc_new_deviation
from .elo import calc_new_ratings
from .mcmahon_pairing import McMahonPairing
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

        players_list = self.db.get_registered_players()
        previous_tours = []
        for i in range(self.db.get_tours_number() - 1):
            previous_tours.append(self.db.get_results(i))
        self._pairing: McMahonPairing = McMahonPairing(players_list, previous_tours)

    @property
    def state(self) -> TournamentState:
        return self._state

    def new_round(self) -> List[Match]:
        nmd_logger.info("New round start")
        if self._state == TournamentState.FINISHED:
            nmd_logger.error("Tournament state is Finished, exception")
            raise TournamentFinishedError
        if self._state == TournamentState.IN_PROGRESS:
            nmd_logger.info("Update coefficients with results of last round")
            self._pairing.update_coefficients(self.db.get_results())
        pairs = self._pairing.gen_pairs()
        self.db.start_new_tour(pairs)
        self._state = TournamentState.IN_PROGRESS
        return pairs

    def add_player(self, player: Player):
        nmd_logger.info(f"Try to register new player, id:{player.tg_id}")
        if self._state != TournamentState.REGISTRATION:
            nmd_logger.error("Tournament state is not in registration, exception")
            raise TournamentStartedError
        rating = ratings_db.get_rating(player.tg_id)
        if not rating:
            nmd_logger.error("Rating not found, exception")
            raise PlayerNotFoundError
        nmd_logger.info(f"Player rating {get_player_rating_view(rating)}")
        self.db.register_player(RegistrationRow.from_rating(rating))

    def update_player_info(self, player: RegistrationRow):
        nmd_logger.info(f"Update player info {get_player_rating_view(player)}")
        if self._state != TournamentState.REGISTRATION:
            nmd_logger.error("Can't update player info not in registration, exception")
            raise TournamentStartedError
        self.db.register_player(player)

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
            if (result.first_id == user_id) or (result.second_id == user_id):
                match_index = i
                match = result
                break
        if not match_index:
            nmd_logger.error("No match found with the user, exception")
            raise MatchWithPlayersNotFound
        # swap result in case of players swapped
        new_result = Match.MatchResult.SecondWon
        if match.first_id == user_id and won:
            new_result = Match.MatchResult.FirstWon
        elif match.second_id == user_id and not won:
            new_result = Match.MatchResult.FirstWon
        old_result: Match.MatchResult = Match.STR_TO_MATCH_RESULT[match.result.value]
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

    def finish_tournament(self):
        nmd_logger.info("Finish tournament")
        self._pairing.update_coefficients(self.db.get_results())
        players = self._pairing.get_players()
        ratings = ratings_db.get_ratings()
        for player in ratings:
            new_deviation = recalc_deviation_by_time(player)
            player.deviation.value = new_deviation
        ratings_id_to_index = {r.tg_id.value: i for i, r in enumerate(ratings)}

        tours = []
        for i in range(self.db.get_tours_number() - 1):
            tours.append(self.db.get_results(i))
        new_ratings = calc_new_ratings(players, tours)

        tournament_table = []
        for i, player in enumerate(players):
            user = self._pairing.get_user(player)
            result = Result.create(i, player, user)
            new_rating = new_ratings[player.tg_id].rating.value
            result.rating.value = f"{player.rating} -> {new_rating}"
            tournament_table.append(result)
            rating: Rating
            index: int
            if player.tg_id in ratings_id_to_index:
                nmd_logger.info(f"Player {player.tg_id} exist in ratings db")
                index = ratings_id_to_index[player.tg_id]
                rating = ratings[index]
            else:
                nmd_logger.warning(f"Player {player.tg_id} doesn't exist in ratings db")
                rating = Rating.default(player.tg_id)
                ratings.append(rating)
                index = len(ratings) - 1
                ratings_id_to_index[player.tg_id] = index
            rating.rating.value = new_rating
            rating.update_date()
            new_deviation = calc_new_deviation(player, rating, new_ratings)
            rating.deviation.value = new_deviation
            ratings[index] = rating

        self.db.finish_tournament(tournament_table)
        ratings_db.update_all_user_ratings(ratings)

        self._state = TournamentState.FINISHED
