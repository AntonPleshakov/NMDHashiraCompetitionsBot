import pytest

from db.ratings import Rating, UsernameAlreadyExistsError
from db.test.conftest import TEST_DATA_PLAYERS
from tournament.player import Player


@pytest.fixture(scope="module")
def db() -> Rating:
    res = Rating()
    yield res
    res._manager.update_all_values([[]])


@pytest.mark.parametrize("player", TEST_DATA_PLAYERS)
@pytest.mark.gdrive_access
def test_add_rating(db: Rating, player: Player):
    ratings = db.get_ratings()
    assert player not in ratings

    db.add_user_rating(player)
    ratings = db.get_ratings()
    assert len(ratings) > 0
    assert ratings[0][0] == player.tg_username  # List must be sorted by rating


@pytest.mark.gdrive_access
def test_add_existing_rating(db: Rating):
    player = TEST_DATA_PLAYERS[0]
    assert player in db.get_ratings()

    with pytest.raises(UsernameAlreadyExistsError):
        db.add_user_rating(player)


@pytest.mark.parametrize("player", TEST_DATA_PLAYERS)
@pytest.mark.gdrive_access
def test_update_rating(db: Rating, player: Player):
    ratings = db.get_ratings()
    assert (
        ratings[-1][0] == player.tg_username
    )  # Each next user must be the last by rating

    ratings[-1][2] = str(int(ratings[0][2]) + 1)
    db.update_all_user_ratings(ratings)
    ratings = db.get_ratings()
    # With the new rating the user must be the first
    assert ratings[0][0] == player.tg_username
