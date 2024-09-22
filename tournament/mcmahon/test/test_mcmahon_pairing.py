import math
from typing import List, Dict

import pytest

from db.ratings import Rating
from db.tournament_structures import Match
from tournament.mcmahon.mcmahon_pairing import McMahonPairing
from tournament.mcmahon.test.conftest import RATINGS
from tournament.player import Player


@pytest.fixture(scope="module")
def pairing() -> McMahonPairing:
    players: List[Player] = []
    for row in RATINGS:
        players.append(Player.from_rating(Rating.from_row(row)))
    res = McMahonPairing(players, [])
    return res


@pytest.mark.gdrive_access
def test_gen_pairs(pairing: McMahonPairing):
    scores: Dict[int, int] = {}
    for row in RATINGS:
        rating = Rating.from_row(row)
        scores[rating.tg_id.value] = math.floor(rating.rating.value / 100)

    pairs: List[Match] = pairing.gen_pairs()
    cost = 0
    for match in pairs:
        assert match.second.value is not None
        cost += abs(scores[match.first_id.value] - scores[match.second_id.value])
    assert cost == 3
