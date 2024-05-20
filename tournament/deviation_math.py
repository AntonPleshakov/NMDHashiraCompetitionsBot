# all formulas were taken from russian go federation:https://gofederation.ru/pages/277294472

from db.ratings import Rating
from nmd_exceptions import NewPlayerError


def max_deviation(rating: int) -> int:
    dan_default = 100
    dan = 2100
    newbie_default = 220
    newbie = 100
    ratio = (rating - newbie) / (dan - newbie)
    return round(newbie_default + ratio * (dan_default - newbie_default))


def k_by_time(rating: int, weeks_passed: int):
    return min(1.0, 0.001 * (3000 - rating) * (weeks_passed / 24))


def recalc_deviation_by_time(player: Rating) -> int:
    deviation = player.deviation.value
    rating = player.rating.value
    max_dev = max_deviation(rating)
    try:
        weeks_passed = player.get_weeks()
    except NewPlayerError:
        return max_dev
    k = k_by_time(rating, weeks_passed)
    new_deviation = deviation * (1 + k * ((max_dev / deviation) ** 2 - 1) ** 0.5)
    return new_deviation
