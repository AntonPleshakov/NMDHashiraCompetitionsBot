from typing import List, Dict, Optional

from db.tournament_structures import Match
from logger.NMDLogger import nmd_logger
from nmd_exceptions import (
    PairingCantFindByePlayer,
    PairingNoPlayers,
)
from .player import Player


class McMahonPairing:
    def __init__(
        self,
        players: List[Player] = None,
        previous_matches: List[List[Match]] = None,
    ):
        nmd_logger.info("Create pairing class")
        self._players: Dict[int, Player] = {}
        for p in players:
            self._players[p.tg_id] = p
        for i, pairs in enumerate(previous_matches):
            self._populate_opponents(pairs)
            if i < (len(previous_matches) - 1):
                self.update_coefficients(pairs)

    def _populate_opponents(self, matches: List[Match]):
        nmd_logger.info(f"Populate opponents for {len(matches)} matches")
        for match in matches:
            first_player = self._players[match.first_id.value]
            if not match.second.value:
                first_player.had_bye = True
                continue
            second_player = self._players[match.second_id.value]
            first_player.opponents.add(second_player)
            first_player.results[match.second_id.value] = match.result
            second_player.opponents.add(first_player)
            second_player.results[match.first_id.value] = match.result.reversed()

    def add_player(self, player: Player):
        self._players[player.tg_id] = player

    def get_players(self) -> List[Player]:
        players = list(self._players.values())
        players.sort(key=lambda x: (x.mm, x.sos, x.sodos, x.rating), reverse=True)
        return players

    def _update_sos_sodos(self):
        for player in self._players.values():
            player.sos = 0
            player.sodos = 0
            for opponent in player.opponents:
                player.sos += opponent.mm
                if player.results[opponent.tg_id] == Match.MatchResult.FirstWon:
                    player.sodos += opponent.mm

    def update_coefficients(self, tour_result: List[Match]):
        nmd_logger.info(f"Update coefficients for {len(tour_result)} matches")
        first_won = Match.MatchResult.FirstWon
        second_won = Match.MatchResult.SecondWon
        # calculate mm score first
        for match in tour_result:
            first = self._players[match.first_id.value]
            if not match.second.value:
                first.mm += 1
                continue
            second = self._players[match.second_id.value]

            if match.result == first_won:
                first.mm += 1
            elif match.result == second_won:
                second.mm += 1

        # calculate SOS and SODOS
        self._update_sos_sodos()

        nmd_logger.debug("name | mm | sos | sodos")
        for p in self.get_players():
            nmd_logger.debug(f"{p.username} | {p.mm} | {p.sos} | {p.sodos}")

    @staticmethod
    def _get_bye_player(players) -> Optional[Player]:
        bye_player = None
        if len(players) % 2 == 1:
            for player in reversed(players):
                if player.had_bye:
                    continue
                nmd_logger.info(f"Bye player is {player.username}")
                bye_player = player
                player.had_bye = True
                players.remove(player)
                break
            if bye_player is None:
                nmd_logger.warning("Can't find a bye player")
                raise PairingCantFindByePlayer
        return bye_player

    def gen_pairs(self) -> List[Match]:
        nmd_logger.info("Gen pairs")
        players = self.get_players()
        bye_player = self._get_bye_player(players)

        if len(players) == 0:
            nmd_logger.warning("No players")
            raise PairingNoPlayers

        result = []
        while len(players) > 0:
            player = players.pop(0)
            opponent = None
            opponents_ids = set(op.tg_id for op in player.opponents)
            for second_player in players:
                if second_player.tg_id not in opponents_ids:
                    opponent = second_player
                    players.remove(second_player)
                    break
            if opponent is None:
                nmd_logger.warning(f"Can't find free opponent for {player.username}")
                result.append(Match.new_match(player.username, player.tg_id))
                continue
            nmd_logger.info(f"Add pair {player.username} vs {opponent.username}")
            new_match = Match.new_match(
                player.username, player.tg_id, opponent.username, opponent.tg_id
            )
            result.append(new_match)

        if bye_player is not None:
            result.append(Match.new_match(bye_player.username, bye_player.tg_id))

        self._populate_opponents(result)
        return result
