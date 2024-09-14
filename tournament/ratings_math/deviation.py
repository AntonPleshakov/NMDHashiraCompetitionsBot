# all formulas were taken from russian go federation:https://gofederation.ru/pages/277294472

from tournament.ratings_math.common import *


# K - коэффициент, определяющий рост неопределенности рейтинга со временем.
# K = min {1, 0.001·(3000 - R)·(T/24)}
def _calc_uncertainty_growth_rate(rating: int, weeks_passed: int) -> float:
    uncertainty_growth_rate: float = min(
        1.0, 0.001 * (MAX_RATING - rating) * (weeks_passed / 4 / MONTHS_TO_MAX_DEV)
    )
    nmd_logger.debug(f"K = {uncertainty_growth_rate}")
    return uncertainty_growth_rate


# Формула для нового стартового в текущем турнире отклонения St, учитывающая время неучастия t
# St = S · {1 + K·[(S*/S)^2 - 1]}^1/2
def calc_new_deviation_by_time(rating: int, deviation: int, weeks_passed: int) -> int:
    max_dev: float = calc_max_deviation(rating)
    K: float = _calc_uncertainty_growth_rate(rating, weeks_passed)
    new_deviation: float = deviation * (1 + K * ((max_dev / deviation) ** 2 - 1)) ** 0.5
    nmd_logger.debug(f"St = {new_deviation}")
    return round(new_deviation)


# Итоговый пересчет отклонений
# S' = (Kd·S*)^0.5
def calc_new_deviation(player: Player) -> int:
    max_dev: float = calc_max_deviation(player.rating)
    Kd = calculate_dynamics_coefficient(player)
    new_dev = round((Kd * max_dev) ** 0.5)
    nmd_logger.info(f"S' = {new_dev}")
    return new_dev
