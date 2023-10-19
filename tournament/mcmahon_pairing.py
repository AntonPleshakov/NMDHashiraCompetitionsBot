from typing import List, Dict

from tournament.match import Match, MatchResult
from tournament.player import Player


class McMahonPairing:
    def __init__(
        self,
        players_list: List[Player] = None,
        previous_matches: List[List[Match]] = None,
    ):
        self._players: Dict[str, Player] = {p.tg_username: p for p in players_list}
        self._tours_counted: int = 0
        for i, pairs in enumerate(previous_matches):
            self._populate_opponents(pairs)
            self.update_coefficients(pairs, i + 1)

    def _populate_opponents(self, matches: List[Match]):
        for match in matches:
            if not match.second_player:
                continue
            first_player_name = match.first_player.tg_username
            second_player_name = match.second_player.tg_username
            first_player = self._players[first_player_name]
            second_player = self._players[second_player_name]
            first_player.opponents.append(second_player_name)
            second_player.opponents.append(first_player_name)

    def add_player(self, player: Player):
        # init scores
        player.mm = player.rating / 100
        player.sos = 0
        player.sodos = 0
        self._players[player.tg_username] = player

    def update_coefficients(self, tour_result: List[Match], tour_number: int):
        if tour_number <= self._tours_counted:
            return
        # calculate mm score first
        for pair in tour_result:
            first = self._players[pair.first_player.tg_username]
            second = self._players[pair.second_player.tg_username]
            if pair.result == MatchResult.FirstWon:
                first.mm += 1
            elif pair.result == MatchResult.SecondWon:
                second.mm += 1
            elif pair.result == MatchResult.Tie:
                first.mm += 0.5
                second.mm += 0.5

        # calculate SOS and SODOS
        for pair in tour_result:
            first = self._players[pair.first_player.tg_username]
            second = self._players[pair.second_player.tg_username]

            first.sos += second.mm
            second.sos += first.mm

            if pair.result == MatchResult.FirstWon:
                first.sodos += second.mm
            elif pair.result == MatchResult.SecondWon:
                second.sodos += first.mm
        self._tours_counted = tour_number

    def gen_pairs(self) -> List[Match]:
        players = list(self._players.values())
        players.sort(key=lambda x: (x.mm, x.sos, x.sodos, x.rating), reverse=True)
        result = []
        while len(players) > 0:
            player = players.pop(0)
            opponent = None
            for second_player in players:
                if second_player not in player.opponents:
                    opponent = second_player
                    break
            if opponent:
                players.remove(opponent)
            result.append(Match(player, opponent))
        self._populate_opponents(result)
        return result
