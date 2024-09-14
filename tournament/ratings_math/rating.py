from db.tournament_structures import Match
from tournament.ratings_math.common import *


# Разница набранных и ожидаемых очков
# DN = ∑j=1,...,N Bj·(rj - pj),
def _calc_expected_points_diff(player: Player) -> float:
    res: float = 0
    for op in player.opponents:
        B: float = calc_opponent_deviation_coefficient(op.rating, op.deviation)
        p: float = calc_win_probability(player.rating, op.rating, B, op.handicap)
        result_point: int = 0
        if op.tg_id in player.results:
            match_result = player.results[op.tg_id]
            if match_result == Match.MatchResult.FirstWon:
                result_point = 1
        res += B * (result_point - p)
    nmd_logger.debug(f"DN = {res}")
    return res


# Для игроков ниже 300 (25 кю) производится обрезание отрицательной составляющей изменения рейтинга так,
# что для игроков ниже 100 рейтинг может только расти.
# Для плавного перехода в зоне между рейтингами 100 и 300 при отрицательном изменении рейтинга
# Kd домножается на понижающий коэффициент, не превосходящий 1 и пропорциональный расстоянию от точки 100:
# K‘дин = Kd·(R – 100)/200
def _cut_dynamics_coefficient_for_weak_players(
    rating: int, dynamics_coefficient: float
) -> float:
    if rating < RATING_25K:
        if rating <= MIN_RATING:
            nmd_logger.debug(f"Kd = 0.0")
            return 0.0
        else:
            player_rating_diff = rating - MIN_RATING
            min_rating_diff = RATING_25K - MIN_RATING
            ratio = player_rating_diff / min_rating_diff
            new_Kd = dynamics_coefficient * ratio
            nmd_logger.debug(f"Kd = {new_Kd}")
            return new_Kd
    return dynamics_coefficient


# Принцип А. Эло: Изменение рейтинга пропорционально разнице результата и вероятностного прогноза
# R' = Kd·DN + R
def calc_new_rating(player: Player) -> int:
    Kd: float = calculate_dynamics_coefficient(player)
    DN: float = _calc_expected_points_diff(player)
    if (Kd * DN) < 0:
        Kd = _cut_dynamics_coefficient_for_weak_players(player.rating, Kd)
    nmd_logger.debug(f"TMP Kd {Kd}; DN {DN}")
    res: int = round(Kd * DN + player.rating)
    nmd_logger.debug(f"R' = {res}")
    return res
