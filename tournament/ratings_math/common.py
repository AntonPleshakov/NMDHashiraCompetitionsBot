import math

from config.config import getconf_int
from logger.NMDLogger import nmd_logger
from tournament.player import Player

MIN_RATING = getconf_int("MIN_RATING")
RATING_25K = getconf_int("25K_RATING")
NEWBIE_RATING = getconf_int("20K_RATING")
NEWBIE_DEVIATION = getconf_int("20K_MAX_DEVIATION")
NEWBIE_MIN_K = getconf_int("20K_MIN_K")
DAN_RATING = getconf_int("DAN_RATING")
DAN_MAX_DEVIATION = getconf_int("DAN_MAX_DEVIATION")
DAN_MIN_K = getconf_int("DAN_MIN_K")
MAX_RATING = getconf_int("MAX_RATING")
MONTHS_TO_MAX_DEV = getconf_int("MONTHS_TO_MAX_DEV")
HANDICAP_TO_RATING = getconf_int("HANDICAP_TO_RATING")


# S* – максимальное отклонение в РС (для игроков 1 дана принято значение 100,
# для остальных уровней − по линейной интерполяции так, что для 20 кю это значение равно 220)
def calc_max_deviation(rating: int) -> float:
    ratio: float = (rating - NEWBIE_RATING) / (DAN_RATING - NEWBIE_RATING)
    max_deviation: int = round(
        NEWBIE_DEVIATION + ratio * (DAN_MAX_DEVIATION - NEWBIE_DEVIATION)
    )
    nmd_logger.debug(f"S* = {max_deviation}")
    return max_deviation


# Bj – коэффициент неопределенности рейтинга j-того соперника
# 1/Bj^2 = 1 + 3*[Sj/(𝝅*S*j)]^2
def calc_opponent_deviation_coefficient(rating: int, deviation: int) -> float:
    max_deviation: float = calc_max_deviation(rating)
    rating_uncertainty_coefficient: float = 1.0 / math.sqrt(
        1 + 3 * (deviation / (math.pi * max_deviation)) ** 2
    )
    nmd_logger.debug(f"Bj = {rating_uncertainty_coefficient}")
    return rating_uncertainty_coefficient


# DRj = Bj·(R - Rj + Hj) - разница в рейтингах с учетом неопределенности рейтинга соперника и форы
def _calc_rating_diff(
    rating: int,
    opponent_rating: int,
    opponent_deviation_coefficient: float,
    handicap: int,
) -> float:
    rating_diff: float = opponent_deviation_coefficient * (
        rating - opponent_rating + handicap * HANDICAP_TO_RATING
    )
    nmd_logger.debug(f"DRj = {rating_diff}")
    return rating_diff


# Dj - среднее квадратичное расстояние рейтингов игрока и соперника от рейтинга идеального игрока (3000)
# Dj^2 = 0.5·[(3000 - R)^2 + (3000 - Rj)^2]
def _ideal_rating_distance(rating: int, opponent_rating: int) -> float:
    rating_diff: int = MAX_RATING - rating
    op_rating_diff: int = MAX_RATING - opponent_rating
    ideal_dist: float = math.sqrt(0.5 * (rating_diff**2 + op_rating_diff**2))
    nmd_logger.debug(f"Dj = {ideal_dist}")
    return ideal_dist


# pj = P(DRj,Dj) - прогнозы результатов (условные априорные математические ожидания набираемых турнирных очков)
# P(DR,D) = max {0, min {1, 0.5 + DR/D}} – для игроков дан-уровня; для остальных
# P(DR,D) = max {0, min {1, 0.5 + DR/1000}}
def calc_win_probability(
    rating: int,
    opponent_rating: int,
    opponent_deviation_coefficient: float,
    handicap: int,
) -> float:
    rating_diff: float = _calc_rating_diff(
        rating, opponent_rating, opponent_deviation_coefficient, handicap
    )
    rating_distance: float = 1000.0
    if rating >= DAN_RATING:
        rating_distance = _ideal_rating_distance(rating, opponent_rating)
    win_probability: float = max(0.0, min(1.0, 0.5 + rating_diff / rating_distance))
    nmd_logger.debug(f"pj = {win_probability}")
    return win_probability


# Дисперсия результатов
# Db = ∑j=1,...,N Bj^2·pj·(1 - pj)
def _calc_results_dispersion(player: Player) -> float:
    result: float = 0
    for op in player.opponents:
        op_deviation_k: float = calc_opponent_deviation_coefficient(
            op.rating, op.deviation
        )
        win_probability: float = calc_win_probability(
            player.rating, op.rating, op_deviation_k, op.handicap
        )
        result += op_deviation_k**2 * win_probability * (1 - win_probability)
    nmd_logger.debug(f"Db = {result}")
    return result


# ограничивается снизу минимальным значением 10 для данов,
# а для остальных нижняя граница Kd увеличивается линейно при снижении уровня игрока так,
# что для 20 кю она становится равной 70
def _calc_min_dynamic_coefficient(rating: int) -> float:
    ratio: float = (rating - NEWBIE_RATING) / (DAN_RATING - NEWBIE_RATING)
    _min_dynamic_coefficient: float = max(
        NEWBIE_MIN_K + ratio * (DAN_MIN_K - NEWBIE_MIN_K), DAN_MIN_K
    )
    nmd_logger.debug(f"Min Kd = {_min_dynamic_coefficient}")
    return _min_dynamic_coefficient


# Коэффициент динамичности, являющийся индивидуально вычисляемой функцией отклонений рейтингов игрока и его соперников,
# а также прогнозов результатов в каждой из учитываемых встреч
# Kd = max{S*/[(S*/S)^2 + Db], Kmin}
def calculate_dynamics_coefficient(player: Player) -> float:
    max_deviation: float = calc_max_deviation(player.rating)
    results_dispersion = _calc_results_dispersion(player)
    dynamics_coefficient: float = max_deviation / (
        (max_deviation / player.deviation) ** 2 + results_dispersion
    )
    res: float = max(dynamics_coefficient, _calc_min_dynamic_coefficient(player.rating))
    nmd_logger.debug(f"Kd = {res}")
    return res
