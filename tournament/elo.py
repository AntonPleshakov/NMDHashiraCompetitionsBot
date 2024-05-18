from typing import List, Dict

from db.ratings import ratings_db, Rating
from db.tournament_structures import Match
from tournament.player import Player


def update_elo(winner_elo: int, loser_elo: int, k_winner: int, k_loser: int):
    expected_winner_win = expected_result(winner_elo, loser_elo)
    expected_loser_win = expected_result(loser_elo, winner_elo)
    winner_elo += k_winner * (1 - expected_winner_win)
    loser_elo += k_loser * (0 - expected_loser_win)
    return winner_elo, loser_elo


def expected_result(elo_a: int, elo_b: int, elo_width: int = 400):
    expect_a = 1.0 / (1 + 10 ** ((elo_b - elo_a) / elo_width))
    return expect_a


def calc_new_ratings(
    players: List[Player], tours: List[List[Match]]
) -> Dict[int, Rating]:
    ratings = {r.tg_id.value: r for r in ratings_db.get_ratings()}
    match_results = {}
    for matches in tours:
        for match in matches:
            match_results[match.first_id] = match.result
            match_results[match.second_id] = match.result.reversed()

    for player in players:
        for opponent in player.opponents:
            player_rating = ratings[player.tg_id]
            opponent_rating = ratings[opponent]
            res = match_results[player.tg_id]
            if res == Match.MatchResult.FirstWon:
                winner = player_rating
                loser = opponent_rating
            elif res == Match.MatchResult.SecondWon:
                winner = opponent_rating
                loser = player_rating
            else:
                continue
            winner_rating, loser_rating = update_elo(
                winner.rating.value,
                loser.rating.value,
                winner.deviation.value,
                loser.deviation.value,
            )
            ratings[winner.tg_id.value].rating.value = winner_rating
            ratings[loser.tg_id.value].rating.value = loser_rating

    return ratings
