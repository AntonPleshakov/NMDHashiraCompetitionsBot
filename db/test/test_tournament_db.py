import pytest
from pygsheets import Worksheet

from db.gapi.gsheets_manager import GSheetsManager
from db.test.conftest import TEST_DATA_PLAYERS
from db.tournament_db import TournamentDB
from tournament.match import Match, MatchResult
from tournament.player import Player


@pytest.fixture(scope="module")
def tournament():
    result = TournamentDB.create_new_tournament()
    yield result
    GSheetsManager().delete(result._manager._ss.title)


@pytest.mark.gdrive_access
def test_new_tournament(tournament: TournamentDB):
    worksheets = tournament._manager._ss.worksheets()
    assert len(worksheets) == 1
    assert worksheets[0].title == "Список зарегистрировавшихся"


@pytest.mark.parametrize("player", TEST_DATA_PLAYERS)
@pytest.mark.gdrive_access
def test_registration(tournament: TournamentDB, player: Player):
    registered_players = tournament.get_registered_players()
    assert player not in registered_players

    tournament.register_player(player)
    registered_players = tournament.get_registered_players()
    assert len(registered_players) > 0
    assert registered_players[0] == player  # List must be sorted by rating


@pytest.mark.parametrize("player", TEST_DATA_PLAYERS)
@pytest.mark.gdrive_access
def test_update_player_info(tournament: TournamentDB, player: Player):
    registered_players = tournament.get_registered_players()
    assert registered_players[-1] == player  # Each next user must be the last by rating

    player.rating = int(registered_players[0].rating) + 1
    tournament.update_player_info(player)
    registered_players = tournament.get_registered_players()
    # With the new rating the user must be the first
    assert registered_players[0] == player


@pytest.mark.gdrive_access
def test_start_new_tour(tournament: TournamentDB):
    # Given
    pairs = []
    for i in range(0, len(TEST_DATA_PLAYERS), 2):
        first_player = TEST_DATA_PLAYERS[i]
        second_player = TEST_DATA_PLAYERS[i + 1]
        match = Match(first_player, second_player)
        pairs.append(match)
    rounds = 5

    # When
    for _ in range(rounds):
        tournament.start_new_tour(pairs)

    # Then
    worksheets = tournament._manager._ss.worksheets()
    assert len(worksheets) == (rounds + 1)  # Additional worksheet for registration
    for i in range(rounds):
        worksheet: Worksheet = worksheets[i]
        assert worksheet.title == ("Тур " + str(i + 1))
        assert tournament._manager.get_worksheet(worksheet.title).get_all_values()


@pytest.mark.gdrive_access
def test_results_registration(tournament: TournamentDB):
    # Given
    matches = tournament.get_results()
    for match in matches:
        assert match.result == MatchResult.NotPlayed

    expected_results = []
    for i in range(len(matches)):
        result = MatchResult(i % len(MatchResult))
        expected_results.append(result)

    # When
    for i in range(len(expected_results)):
        tournament.register_result(i, expected_results[i])

    # Then
    matches = tournament.get_results()
    assert len(matches) == len(expected_results)
    for i in range(len(matches)):
        assert matches[i].result == expected_results[i]


@pytest.mark.gdrive_access
def test_finish_tournament(tournament: TournamentDB):
    worksheets_number = len(tournament._manager._ss.worksheets())

    tournament.finish_tournament(TEST_DATA_PLAYERS)

    worksheets = tournament._manager._ss.worksheets()
    assert len(worksheets) == (worksheets_number + 1)
    ws = tournament._manager.get_worksheet("Турнирная таблица")
    assert ws.get_all_values()
