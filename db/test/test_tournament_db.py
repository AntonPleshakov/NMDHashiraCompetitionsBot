import pytest
from pygsheets import Worksheet

from common.nmd_datetime import nmd_now
from config.config import getconf
from db.gapi.gsheets_manager import GSheetsManager
from db.ratings import Rating
from db.tournament import TournamentDB, RegistrationRow
from db.tournament_structures import Match, Result
from .conftest import (
    TEST_DATA_PLAYERS,
    DEFAULT_TOURNAMENT_SETTINGS,
    ratingToRegistration,
)


@pytest.fixture
def spreadsheets():
    manager = GSheetsManager()

    def create_ss(date: str):
        table_name = getconf("TOURNAMENT_GTABLE_NAME") + " " + date
        ss_manager = manager.create(table_name)
        settings_ws = ss_manager.rename_worksheet(
            getconf("TOURNAMENT_SETTINGS_PAGE_NAME")
        )
        settings_ws.update_values(DEFAULT_TOURNAMENT_SETTINGS.to_matrix())
        registration_page = ss_manager.add_worksheet(
            getconf("TOURNAMENT_REGISTER_PAGE_NAME")
        )
        registration_page.set_header([RegistrationRow().params_views()])
        return ss_manager

    spreadsheets = [
        create_ss("10.05.2000"),
        create_ss("10.10.1999"),
        create_ss("10.01.2001"),
        create_ss("01.05.2000"),
        create_ss("20.05.2000"),
        create_ss("01.01.2000"),
    ]
    yield
    for ss in spreadsheets:
        manager.delete(ss._ss.title)


@pytest.mark.gdrive_access
def test_latest_tournament(spreadsheets):
    latest = TournamentDB.get_latest_tournament()
    assert latest._manager._ss.title.split()[-1] == "10.01.2001"


@pytest.mark.gdrive_access
def test_empty_latest_tournament():
    latest = TournamentDB.get_latest_tournament()
    assert latest is None


@pytest.fixture(scope="module")
def tournament():
    result = TournamentDB.create_new_tournament(DEFAULT_TOURNAMENT_SETTINGS)
    yield result
    GSheetsManager().delete(result._manager._ss.title)


@pytest.mark.gdrive_access
def test_new_tournament(tournament: TournamentDB):
    date = nmd_now().strftime("%d.%m.%Y")
    assert (
        tournament._manager._ss.title == getconf("TOURNAMENT_GTABLE_NAME") + " " + date
    )
    worksheets = tournament._manager._ss.worksheets()
    assert len(worksheets) == 2
    assert worksheets[0].title == getconf("TOURNAMENT_SETTINGS_PAGE_NAME")
    assert worksheets[1].title == getconf("TOURNAMENT_REGISTER_PAGE_NAME")


@pytest.mark.parametrize("player", TEST_DATA_PLAYERS)
@pytest.mark.gdrive_access
def test_registration(tournament: TournamentDB, player: Rating):
    player_registration = ratingToRegistration(player)
    registered_players = tournament.get_registered_players()
    assert player_registration not in registered_players

    tournament.register_player(player_registration)
    registered_players = tournament.get_registered_players()
    assert len(registered_players) > 0
    assert registered_players[0] == player_registration  # List must be sorted by rating


@pytest.mark.gdrive_access
def test_start_new_tour(tournament: TournamentDB):
    # Given
    pairs = []
    for i in range(0, len(TEST_DATA_PLAYERS), 2):
        first_player = TEST_DATA_PLAYERS[i].tg_username.value_repr()
        second_player = TEST_DATA_PLAYERS[i + 1].tg_username.value_repr()
        default_res = "-"
        default_map = "default_map"
        default_bg = "default_bg"
        match = Match.from_row(
            [first_player, default_res, second_player, default_map, default_bg]
        )
        pairs.append(match)
    rounds = 5

    # When
    for _ in range(rounds):
        tournament.start_new_tour(pairs)

    # Then
    worksheets = tournament._manager._ss.worksheets()
    assert len(worksheets) == (
        rounds + 2
    )  # Additional worksheets for registration and settings
    for i in range(rounds):
        worksheet: Worksheet = worksheets[i + 2]
        assert worksheet.title == (
            getconf("TOURNAMENT_TOUR_PAGE_NAME") + " " + str(i + 1)
        )
        assert tournament._manager.get_worksheet(worksheet.title).get_all_values()


@pytest.mark.gdrive_access
def test_results_registration(tournament: TournamentDB):
    # Given
    matches = tournament.get_results()
    for match in matches:
        default_result = "-"
        assert match.result.value_repr() == default_result

    expected_results = []
    for i in range(len(matches)):
        result = "1:0" if i % 2 == 0 else "0:1"
        expected_results.append(result)

    # When
    for i in range(len(expected_results)):
        tournament.register_result(i, expected_results[i])

    # Then
    matches = tournament.get_results()
    assert len(matches) == len(expected_results)
    for i in range(len(matches)):
        assert matches[i].result.value_repr() == expected_results[i]


@pytest.mark.gdrive_access
def test_finish_tournament(tournament: TournamentDB):
    worksheets_number = len(tournament._manager._ss.worksheets())

    result = []
    for i in range(len(TEST_DATA_PLAYERS)):
        rating = TEST_DATA_PLAYERS[i]
        row = Result.from_row(
            [
                i + 1,
                rating.tg_username.value_repr(),
                rating.tg_id.value_repr(),
                rating.nmd_username.value_repr(),
                1,
                1,
                1,
                1,
            ]
        )
        result.append(row)
    tournament.finish_tournament(result)

    worksheets = tournament._manager._ss.worksheets()
    assert len(worksheets) == (worksheets_number + 1)
    ws = tournament._manager.get_worksheet(getconf("TOURNAMENT_RESULTS_PAGE_NAME"))
    assert ws.get_all_values()
