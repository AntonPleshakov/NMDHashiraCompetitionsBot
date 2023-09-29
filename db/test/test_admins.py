import pytest

from db.admins_db import AdminsDB
from db.test.conftest import TEST_DATA_ADMINS


@pytest.fixture(scope="module")
def db() -> AdminsDB:
    res = AdminsDB()
    yield res
    res._manager.update_values([[]])


@pytest.mark.parametrize("user_name, user_id", TEST_DATA_ADMINS)
@pytest.mark.gdrive_access
def test_add_admin(db: AdminsDB, user_name: str, user_id: str):
    admins = db.get_admins()
    if len(admins) > 0:
        assert admins[-1] != [user_name, user_id]

    db.add_admin(user_name, user_id)
    admins = db.get_admins()
    assert admins[-1] == [user_name, user_id]


@pytest.mark.parametrize("user_name, user_id", TEST_DATA_ADMINS)
@pytest.mark.gdrive_access
def test_del_admin(db: AdminsDB, user_name: str, user_id: str):
    admins = db.get_admins()
    assert [user_name, user_id] in admins

    db.del_admin(user_id)
    admins = db.get_admins()
    assert [user_name, user_id] not in admins
