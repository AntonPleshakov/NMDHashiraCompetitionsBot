import pytest

from db.admins import Admins


@pytest.fixture(scope="module")
def db() -> Admins:
    res = Admins()
    yield res
    res._manager.update_all_values([[]])


TEST_DATA_ADMINS = [
    ("Anton", "1"),
    ("Ivan", "2"),
    ("Max", "3"),
    ("Sam", "4"),
    ("Nikita", "5"),
    ("Sergey", "6"),
    ("Kirill", "7"),
    ("Georgiy", "8"),
]


@pytest.mark.parametrize("user_name, user_id", TEST_DATA_ADMINS)
@pytest.mark.gdrive_access
def test_add_admin(db: Admins, user_name: str, user_id: str):
    admins = db.get_admins()
    if len(admins) > 0:
        assert admins[-1] != [user_name, user_id]

    db.add_admin(user_name, user_id)
    admins = db.get_admins()
    assert admins[-1] == [user_name, user_id]


@pytest.mark.parametrize("user_name, user_id", TEST_DATA_ADMINS)
@pytest.mark.gdrive_access
def test_del_admin(db: Admins, user_name: str, user_id: str):
    admins = db.get_admins()
    assert [user_name, user_id] in admins

    db.del_admin(user_id)
    admins = db.get_admins()
    assert [user_name, user_id] not in admins
