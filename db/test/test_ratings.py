import pytest

from db.ratings import RatingsDB, UsernameAlreadyExistsError, Rating
from .conftest import TEST_DATA_PLAYERS


@pytest.fixture(scope="module")
def db() -> RatingsDB:
    res = RatingsDB()
    yield res
    res._manager.update_values([[]])


@pytest.mark.parametrize("player", TEST_DATA_PLAYERS)
@pytest.mark.gdrive_access
def test_add_rating(db: RatingsDB, player: Rating):
    ratings = db.get_ratings()
    assert player not in ratings

    db.add_user_rating(player)
    ratings = db.get_ratings()
    assert len(ratings) > 0
    assert ratings[0] == player  # List must be sorted by rating


@pytest.mark.gdrive_access
def test_add_existing_rating(db: RatingsDB):
    player = TEST_DATA_PLAYERS[0]
    assert player in db.get_ratings()

    with pytest.raises(UsernameAlreadyExistsError):
        db.add_user_rating(player)


@pytest.mark.parametrize("player", TEST_DATA_PLAYERS)
@pytest.mark.gdrive_access
def test_update_rating(db: RatingsDB, player: Rating):
    ratings = db.get_ratings()
    assert ratings[-1] == player  # Each next user must be the last by rating

    player.rating.value = int(ratings[0].rating) + 1
    ratings[-1] = player
    db.update_all_user_ratings(ratings)
    ratings = db.get_ratings()
    # With the new rating the user must be the first
    assert ratings[0] == player
