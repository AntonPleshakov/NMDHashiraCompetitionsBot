# all formulas were taken from russian go federation:https://gofederation.ru/pages/277294472
import math
from typing import List, Dict

from db.ratings import Rating
from logger.NMDLogger import nmd_logger
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
    max_deviation = round(NEWBIE_DEVIATION + ratio * (DAN_DEVIATION - NEWBIE_DEVIATION))
    nmd_logger.debug(f"Max deviation for {rating} = {max_deviation}")
    return max_deviation


def _k_by_time(rating: int, weeks_passed: int) -> float:
    k = min(1.0, 0.001 * (MAX_RATING - rating) * (weeks_passed / 24))
    nmd_logger.debug(
        f"K by time for rating {rating} when {weeks_passed} weeks passed = {k}"
    )
    return k


def _calculate_b(deviation: int, max_deviation: int) -> float:
    b = 1.0 / math.sqrt(1 + 3 * (deviation / (math.pi * max_deviation)) ** 2)
    nmd_logger.debug(f"B for dev {deviation} and max_dev {max_deviation} = {b}")
    return b


def _ideal_rating_distance(rating: int, opponent_rating: int) -> float:
    ideal_dist = math.sqrt(
        0.5 * ((MAX_RATING - rating) ** 2 + (MAX_RATING - opponent_rating) ** 2)
    )
    nmd_logger.debug(
        f"Ideal rating distance between {rating} and {opponent_rating} = {ideal_dist}"
    )
    return ideal_dist


def _calculate_probability(rating_diff, rating_distance):
    rating_distance = min(1000, rating_distance)
    prob = max(0, min(1, 0.5 + rating_diff / rating_distance))
    nmd_logger.debug(
        f"Probabilitiy with diff {rating_diff} and dist {rating_distance} = {prob}"
    )
    return prob


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
    nmd_logger.debug(
        f"Calc results dispersion with {rating} for opponents: {", ".join([p.tg_username.value for p in opponents])}"
        + f" = {result}"
    )
    return result


def _get_min_K(rating: int):
    ratio = (rating - NEWBIE_RATING) / (DAN_RATING - NEWBIE_RATING)
    min_k = max(round(NEWBIE_MIN_K + ratio * (DAN_MIN_K - NEWBIE_MIN_K)), DAN_MIN_K)
    nmd_logger.debug(f"Min k for {rating} = {min_k}")
    return min_k


def _calculate_K_dyn(
    rating: int, deviation: int, max_deviation: int, results_dispersion: float
):
    K_dyn = max_deviation / ((max_deviation / deviation) ** 2 + results_dispersion)
    res = max(K_dyn, _get_min_K(rating))
    nmd_logger.debug(
        f"Calc k dyn for {rating}, {deviation}, {max_deviation}, {results_dispersion} = {res}"
    )
    return res


def recalc_deviation_by_time(player: Rating) -> int:
    deviation = player.deviation.value
    rating = player.rating.value
    max_dev = _max_deviation(rating)
    try:
        weeks_passed = player.get_weeks()
    except NewPlayerError:
        nmd_logger.info(
            f"can't calc weeks for new player {player.tg_username.value}. New deviation equals max = {max_dev}"
        )
        return max_dev
    k = _k_by_time(rating, weeks_passed)
    new_deviation = deviation * (1 + k * ((max_dev / deviation) ** 2 - 1) ** 0.5)
    nmd_logger.info(
        f"Calc deviation by time for {player.tg_username.value} = {new_deviation}"
    )
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
    k_din = _calculate_K_dyn(rating, deviation, max_dev, results_dispersion)

    new_dev = round((k_din * max_dev) ** 0.5)
    nmd_logger.info(f"Calc new deviation for player {player.tg_id} = {new_dev}")
    return new_dev
