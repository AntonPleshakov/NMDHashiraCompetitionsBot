from logger.NMDLogger import nmd_logger
from tournament.player import Player
from tournament.ratings_math.common import calc_max_deviation
from tournament.ratings_math.deviation import (
    calc_new_deviation_by_time,
    calc_new_deviation,
)
from tournament.ratings_math.rating import calc_new_rating


def update_player_with_rating(player: Player):
    nmd_logger.debug(f"Update rating for {player.username}")
    if player.weeks_to_last_tournament >= 0:
        player.deviation = calc_new_deviation_by_time(
            player.rating, player.deviation, player.weeks_to_last_tournament
        )
    else:
        player.deviation = calc_max_deviation(player.rating)

    player.rating = calc_new_rating(player)
    player.deviation = calc_new_deviation(player)
