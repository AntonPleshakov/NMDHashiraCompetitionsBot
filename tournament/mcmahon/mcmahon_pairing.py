from typing import List, Dict, Optional, Tuple

from db.tournament_structures import Match
from logger.NMDLogger import nmd_logger
from nmd_exceptions import (
    PairingCantFindByePlayer,
)
from tournament.mcmahon.mwmatching import maxWeightMatching
from tournament.player import Player


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
            first_player.add_opponent(second_player)
            second_player.add_opponent(first_player)

    def add_results(self, matches: List[Match]):
        nmd_logger.info(f"Add results for {len(matches)} matches")
        for match in matches:
            if not match.second.value:
                continue
            first_player = self._players[match.first_id.value]
            second_player = self._players[match.second_id.value]
            first_player.results[match.second_id.value] = match.result
            second_player.results[match.first_id.value] = match.result.reversed()

    def add_player(self, player: Player):
        self._players[player.tg_id] = player

    def remove_player(self, player_id: int):
        self._players.pop(player_id, None)

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
        self.add_results(tour_result)
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
                players.remove(player)
                break
            if bye_player is None:
                nmd_logger.warning("Can't find a bye player")
                raise PairingCantFindByePlayer
        return bye_player

    @staticmethod
    def _gen_weighted_players_edges(
        players: List[Player],
    ) -> List[Tuple[int, int, int]]:
        edges = []
        for i, p in enumerate(players):
            for j, op in enumerate(players):
                if i >= j:
                    continue
                if op.tg_id not in p.opponents_ids:
                    edges.append((i, j, -abs(p.mm - op.mm)))
        return edges

    def gen_pairs(self) -> List[Match]:
        nmd_logger.info("Gen pairs")

        players = list(self.get_players())
        bye_player = self._get_bye_player(players)
        edges = self._gen_weighted_players_edges(players)
        matching = maxWeightMatching(edges)

        result = []
        created_pairs = set()
        for i, j in enumerate(matching):
            if i in created_pairs:
                continue
            created_pairs.add(i)
            p = players[i]
            new_match = Match.new_match(p.username, p.tg_id)
            if j != -1:
                created_pairs.add(j)
                op = players[j]
                new_match.second.value = op.username
                new_match.second_id.value = op.tg_id
                nmd_logger.info(f"Add pair {p.username} vs {op.username}")
            else:
                nmd_logger.info(f"Add match without op for {p.username}")
            result.append(new_match)

        if bye_player is not None:
            result.append(Match.new_match(bye_player.username, bye_player.tg_id))

        self._populate_opponents(result)
        return result
