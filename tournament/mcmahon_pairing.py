from typing import List, Dict

from db.tournament_structures import Match, RegistrationRow
from logger.NMDLogger import nmd_logger
from .player import Player


class McMahonPairing:
    def __init__(
        self,
        players: List[RegistrationRow] = None,
        previous_matches: List[List[Match]] = None,
    ):
        nmd_logger.info("Create pairing class")
        self._players: Dict[int, Player] = {}
        self._registrations: Dict[int, RegistrationRow] = {}
        for p in players:
            self._players[p.tg_id.value] = Player.from_registration(p)
            self._registrations[p.tg_id.value] = p
        for i, pairs in enumerate(previous_matches):
            self._populate_opponents(pairs)
            self.update_coefficients(pairs)

    def _populate_opponents(self, matches: List[Match]):
        nmd_logger.info(f"Populate opponents for {len(matches)} matches")
        for match in matches:
            if not match.second.value:
                continue
            first_player = self._players[match.first_id]
            second_player = self._players[match.second_id]
            first_player.opponents.add(match.second_id)
            second_player.opponents.add(match.first_id)

    def get_players(self) -> List[Player]:
        players = list(self._players.values())
        players.sort(key=lambda x: (x.mm, x.sos, x.sodos, x.rating), reverse=True)
        return players

    def get_user(self, player: Player):
        return self._registrations[player.tg_id]

    def update_coefficients(self, tour_result: List[Match]):
        nmd_logger.info(f"Update coefficients for {len(tour_result)} matches")
        first_won = Match.MatchResult.FirstWon
        second_won = Match.MatchResult.SecondWon
        # calculate mm score first
        for match in tour_result:
            first = self._players[match.first_id]
            second = self._players[match.second_id]

            if match.result == first_won:
                first.mm += 1
            elif match.result == second_won:
                second.mm += 1

        # calculate SOS and SODOS
        for match in tour_result:
            first = self._players[match.first_id]
            second = self._players[match.second_id]

            first.sos += second.mm
            second.sos += first.mm

            if match.result == first_won:
                first.sodos += second.mm
            elif match.result == second_won:
                second.sodos += first.mm

    def gen_pairs(self) -> List[Match]:
        nmd_logger.info("Gen pairs")
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
            result.append(Match.new_match(self.get_user(player), opponent))
        self._populate_opponents(result)
        return result
