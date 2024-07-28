from typing import List, Dict

from db.tournament_structures import Match, RegistrationRow
from logger.NMDLogger import nmd_logger
from nmd_exceptions import (
    PairingCantFindByePlayer,
    PairingCantFindFreeOpponent,
    PairingNoPlayers,
)
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
        for pairs in previous_matches[:-1]:
            self._populate_opponents(pairs)
            self.update_coefficients(pairs)
        if len(previous_matches) > 0:
            self._populate_opponents(previous_matches[-1])

    def _populate_opponents(self, matches: List[Match]):
        nmd_logger.info(f"Populate opponents for {len(matches)} matches")
        for match in matches:
            first_player = self._players[match.first_id.value]
            if not match.second.value:
                first_player.had_bye = True
                continue
            second_player = self._players[match.second_id.value]
            first_player.opponents.add(match.second_id.value)
            first_player.results[match.second_id.value] = match.result
            second_player.opponents.add(match.first_id.value)
            second_player.results[match.first_id.value] = match.result.reversed()

    def add_player(self, player: RegistrationRow):
        self._players[player.tg_id.value] = Player.from_registration(player)
        self._registrations[player.tg_id.value] = player

    def get_players(self) -> List[Player]:
        players = list(self._players.values())
        players.sort(key=lambda x: (x.mm, x.sos, x.sodos, x.rating), reverse=True)
        return players

    def get_user(self, player: Player):
        return self._registrations[player.tg_id]

    def _update_sos_sodos(self):
        for player in self._players.values():
            player.sos = 0
            player.sodos = 0
            for opponent_id in player.opponents:
                opponent = self._players[opponent_id]
                player.sos += opponent.mm
                if player.results[opponent_id] == Match.MatchResult.FirstWon:
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
        for player in self._players.values():
            player_row = self.get_user(player)
            nmd_logger.debug(
                f"{player_row.tg_username} | {player.mm} | {player.sos} | {player.sodos}"
            )

    def _get_bye_player(self, players):
        bye_player = None
        if len(players) % 2 == 1:
            for player in reversed(players):
                if player.had_bye:
                    continue
                nmd_logger.info(f"Bye player is {self.get_user(player).tg_username}")
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
        players = list(self._players.values())
        players.sort(key=lambda x: (x.mm, x.sos, x.sodos, x.rating), reverse=True)

        bye_player = self._get_bye_player(players)

        if len(players) == 0:
            nmd_logger.warning("No players")
            raise PairingNoPlayers

        result = []
        while len(players) > 0:
            player = players.pop(0)
            player_row = self.get_user(player)
            opponent = None
            for second_player in players:
                if second_player.tg_id not in player.opponents:
                    opponent = self.get_user(second_player)
                    players.remove(second_player)
                    break
            if opponent is None:
                nmd_logger.warning(
                    f"Can't find free opponent for {player_row.tg_username}"
                )
                raise PairingCantFindFreeOpponent
            nmd_logger.info(
                f"Add pair {player_row.tg_username} vs {opponent.tg_username}"
            )
            result.append(Match.new_match(player_row, opponent))

        if bye_player is not None:
            result.append(Match.new_match(self.get_user(bye_player), None))

        self._populate_opponents(result)
        return result
