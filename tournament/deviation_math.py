# all formulas were taken from russian go federation:https://gofederation.ru/pages/277294472
import math
from typing import List, Dict

from db.ratings import Rating
from nmd_exceptions import NewPlayerError
from tournament.player import Player

MAX_RATING = 3000
DAN_DEVIATION = 100
DAN_RATING = 2100
DAN_MIN_K = 10
NEWBIE_DEVIATION = 220
NEWBIE_RATING = 100
NEWBIE_MIN_K = 70


def _max_deviation(rating: int) -> int:
    ratio = (rating - NEWBIE_RATING) / (DAN_RATING - NEWBIE_RATING)
    return round(NEWBIE_DEVIATION + ratio * (DAN_DEVIATION - NEWBIE_DEVIATION))


def _k_by_time(rating: int, weeks_passed: int) -> float:
    return min(1.0, 0.001 * (MAX_RATING - rating) * (weeks_passed / 24))


def _calculate_b(deviation: int, max_deviation: int) -> float:
    return 1.0 / math.sqrt(1 + 3 * (deviation / (math.pi * max_deviation)) ** 2)


def _ideal_rating_distance(rating: int, opponent_rating: int) -> float:
    return math.sqrt(
        0.5 * ((MAX_RATING - rating) ** 2 + (MAX_RATING - opponent_rating) ** 2)
    )


def _calculate_probability(rating_diff, rating_distance):
    rating_distance = min(1000, rating_distance)
    return max(0, min(1, 0.5 + rating_diff / rating_distance))


def _calculate_results_dispersion(rating: int, opponents: List[Rating]):
    result = 0
    for player in opponents:
        opponent_rating = player.rating.value
        deviation = player.deviation.value
        max_dev = _max_deviation(opponent_rating)
        b = _calculate_b(deviation, max_dev)
        rating_distance = _ideal_rating_distance(rating, opponent_rating)
        rating_diff = b * (rating - opponent_rating)
        p = _calculate_probability(rating_diff, rating_distance)
        result = result + b**2 * p * (1 - p)
    return result


def _get_min_K(rating: int):
    ratio = (rating - NEWBIE_RATING) / (DAN_RATING - NEWBIE_RATING)
    return max(round(NEWBIE_MIN_K + ratio * (DAN_MIN_K - NEWBIE_MIN_K)), DAN_MIN_K)


def _calculate_K_dyn(
    rating: int, deviation: int, max_deviation: int, results_dispersion: float
):
    K_dyn = max_deviation / ((max_deviation / deviation) ** 2 + results_dispersion)
    return max(K_dyn, _get_min_K(rating))


def recalc_deviation_by_time(player: Rating) -> int:
    deviation = player.deviation.value
    rating = player.rating.value
    max_dev = _max_deviation(rating)
    try:
        weeks_passed = player.get_weeks()
    except NewPlayerError:
        return max_dev
    k = _k_by_time(rating, weeks_passed)
    new_deviation = deviation * (1 + k * ((max_dev / deviation) ** 2 - 1) ** 0.5)
    return new_deviation


TgID = int


def calc_new_deviation(
    player: Player, rating_row: Rating, all_ratings: Dict[TgID, Rating]
) -> int:
    deviation = rating_row.deviation.value
    rating = player.rating
    max_dev = _max_deviation(rating)
    opponents = [all_ratings[opponent] for opponent in player.opponents]
    results_dispersion = _calculate_results_dispersion(rating, opponents)
    k_din = _calculate_K_dyn(deviation, max_dev, results_dispersion)

    return (k_din * max_dev) ** 0.5
