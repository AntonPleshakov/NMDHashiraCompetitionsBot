import pytest

from db.admins import AdminsDB, Admin
from .conftest import TEST_DATA_ADMINS


@pytest.fixture(scope="module")
def db() -> AdminsDB:
    res = AdminsDB()
    yield res
    res._manager.update_values([[]])


@pytest.mark.parametrize("user_name, user_id", TEST_DATA_ADMINS)
@pytest.mark.gdrive_access
def test_add_admin(db: AdminsDB, user_name: str, user_id: int):
    test_admin = Admin(user_name, user_id)
    admins = db.get_admins()
    if len(admins) > 0:
        assert admins[-1] != test_admin

    db.add_admin(test_admin)
    admins = db.get_admins()
    assert admins[-1] == test_admin


@pytest.mark.parametrize("user_name, user_id", TEST_DATA_ADMINS)
@pytest.mark.gdrive_access
def test_del_admin(db: AdminsDB, user_name: str, user_id: int):
    test_admin = Admin(user_name, user_id)
    admins = db.get_admins()
    assert test_admin in admins

    db.del_admin(user_id)
    admins = db.get_admins()
    assert test_admin not in admins
