import pytest

from db.ratings import Rating


@pytest.fixture(scope="module")
def db() -> Rating:
    res = Rating()
    yield res
    res._manager.update_all_values([[]])


# Each next user should be placed first after sort by rating
TEST_DATA_USERS = [
    (["Anton", "NMD_Anton", 100, 100, 100, 1]),
    (["Ivan", "NMD_Ivan", 200, 100, 100, 2]),
    (["Max", "NMD_Max", 300, 100, 100, 3]),
    (["Sam", "NMD_Sam", 400, 100, 100, 4]),
    (["Nikita", "NMD_Nikita", 500, 100, 100, 5]),
    (["Sergey", "NMD_Sergey", 600, 100, 100, 6]),
    (["Kirill", "NMD_Kirill", 700, 100, 100, 7]),
    (["Georgiy", "NMD_Georgiy", 800, 100, 100, 8]),
]


@pytest.mark.parametrize("rating_row", TEST_DATA_USERS)
@pytest.mark.gdrive_access
def test_add_rating(db: Rating, rating_row):
    ratings = db.get_ratings()
    assert rating_row not in ratings

    db.add_user_rating(*rating_row)
    ratings = db.get_ratings()
    assert len(ratings) > 0
    assert ratings[0][0] == rating_row[0]  # List must be sorted by rating


@pytest.mark.parametrize("rating_row", TEST_DATA_USERS)
@pytest.mark.gdrive_access
def test_update_rating(db: Rating, rating_row):
    ratings = db.get_ratings()
    assert ratings[-1][0] == rating_row[0]  # Each next user must be the last by rating

    ratings[-1][2] = str(int(ratings[0][2]) + 1)
    db.update_all_user_ratings(ratings)
    ratings = db.get_ratings()
    # With the new rating the user must be the first
    assert ratings[0][0] == rating_row[0]
