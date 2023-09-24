from enum import Enum

from tournament.player import Player


class MatchResult(Enum):
    Tie = 0
    NotPlayed = 1
    FirstWon = 2
    SecondWon = 3


class Match:
    def __init__(self, first_player: Player, second_player: Player):
        self.first_player: Player = first_player
        self.second_player: Player = second_player
        self.result: MatchResult = MatchResult.NotPlayed
