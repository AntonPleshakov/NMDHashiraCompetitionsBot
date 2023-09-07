from config.config import config, MODE


class Player:
    def __init__(
        self,
        tg_username,
        nmd_username="",
        rating=100,
        deviation=config[MODE]["DEFAULT_K"],
        attack=0,
        arena_place=0,
    ):
        self.tg_username = tg_username
        self.nmd_username = nmd_username
        self.rating = rating
        self.deviation = deviation
        self.attack = attack
        self.arena_place = arena_place
