from config.config import getconf


class Player:
    def __init__(
        self,
        tg_username: str,
        nmd_username: str = "",
        rating: int = 100,
        deviation: int = getconf("DEFAULT_K"),
        attack: int = 0,
        arena_place: int = 0,
    ):
        self.tg_username: str = tg_username
        self.nmd_username: str = nmd_username
        self.rating: int = rating
        self.deviation: int = deviation
        self.attack: int = attack
        self.arena_place: int = arena_place
