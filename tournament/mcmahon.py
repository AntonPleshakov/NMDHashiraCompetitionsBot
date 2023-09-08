from typing import List, Dict

from tournament.player import Player


class McMahonPairing:
    def __init__(self, players: List[Player], prev_opponents: Dict[str, List[Player]]):
        self._players: List[Player] = players
        self._prev_opponents: Dict[str, List[Player]] = prev_opponents

    def gen_pairs(self):
        pass
