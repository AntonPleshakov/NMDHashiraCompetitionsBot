from typing import List, Dict, Tuple

from db.ratings import ratings_db, Rating
from db.tournament_structures import Match
from logger.NMDLogger import nmd_logger
from tournament.player import Player


def update_elo(
    winner_elo: int, loser_elo: int, k_winner: int, k_loser: int
) -> Tuple[int, int]:
    expected_winner_win = expected_result(winner_elo, loser_elo)
    expected_loser_win = expected_result(loser_elo, winner_elo)
    new_winner_elo = round(winner_elo + k_winner * (1 - expected_winner_win))
    new_loser_elo = round(loser_elo + k_loser * (0 - expected_loser_win))
    nmd_logger.info(
        f"Update elo. Winner {winner_elo} -> {new_winner_elo}, Loser {loser_elo} -> {new_loser_elo}"
    )
    return new_winner_elo, new_loser_elo


def expected_result(elo_a: int, elo_b: int, elo_width: int = 400):
    expect_a = 1.0 / (1 + 10 ** ((elo_b - elo_a) / elo_width))
    nmd_logger.info(
        f"Prediction. a: {elo_a}, b: {elo_b}, width: {elo_width}, expect_a: {expect_a}"
    )
    return expect_a


def calc_new_ratings(
    players: List[Player], tours: List[List[Match]]
) -> Dict[int, Rating]:
    nmd_logger.info("Calc new ratings")
    ratings = {r.tg_id.value: r for r in ratings_db.get_ratings()}
    match_results = {}
    for matches in tours:
        for match in matches:
            if not match.second.value:
                continue
            left = match.first_id.value
            right = match.second_id.value
            if left not in match_results:
                match_results[left] = {}
            match_results[left][right] = match.result
            if right not in match_results:
                match_results[right] = {}
            match_results[right][left] = match.result.reversed()

    for player in players:
        for opponent in player.opponents:
            player_rating = ratings[player.tg_id]
            opponent_rating = ratings[opponent]
            res = match_results[player.tg_id][opponent]
            if res == Match.MatchResult.FirstWon:
                winner = player_rating
                loser = opponent_rating
            elif res == Match.MatchResult.SecondWon:
                winner = opponent_rating
                loser = player_rating
            else:
                nmd_logger.info(
                    f"Match between {player_rating.tg_username} and {opponent_rating.tg_username} wasn't finished"
                )
                continue
            nmd_logger.info(
                f"Update elo for {winner.tg_username} (winner) and {loser.tg_username} (loser)"
            )
            winner_rating, loser_rating = update_elo(
                winner.rating.value,
                loser.rating.value,
                winner.deviation.value,
                loser.deviation.value,
            )
            ratings[winner.tg_id.value].rating.value = winner_rating
            ratings[loser.tg_id.value].rating.value = loser_rating

    return ratings
