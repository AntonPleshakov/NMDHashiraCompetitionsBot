import time

import pytest

from config.config import getconf
from db.gapi.gsheets_managers import GSheetsManager
from db.gapi.spreadsheet_manager import SpreadsheetManager


@pytest.fixture
def manager_factory():
    def create_manager(spreadsheet_name: str) -> SpreadsheetManager:
        return GSheetsManager().open(spreadsheet_name)

    return create_manager


@pytest.fixture
def manager(manager_factory):
    ss_name = getconf("RATING_LIST_GTABLE_NAME")
    return manager_factory(ss_name)


@pytest.mark.gdrive_access
@pytest.mark.parametrize(
    "worksheet_name, is_exist",
    [(getconf("RATING_LIST_PAGE_NAME"), True), ("test", False)],
)
def test_worksheet_existence(
    manager: SpreadsheetManager, worksheet_name: str, is_exist: bool
):
    assert manager.is_worksheet_exist(worksheet_name) == is_exist


@pytest.mark.gdrive_access
@pytest.mark.slow
def test_ws_creation(manager: SpreadsheetManager):
    ws_name = "test"
    assert not manager.is_worksheet_exist(ws_name)

    # Create a worksheet
    manager.add_worksheet(ws_name)
    cnt = 0
    while (not manager.is_worksheet_exist(ws_name)) and (cnt < 20):
        time.sleep(0.1)
        cnt += 1
    assert cnt < 20

    # Delete the worksheet
    manager.delete_worksheet(ws_name)
    assert not manager.is_worksheet_exist(ws_name)


@pytest.mark.gdrive_access
def test_ws_open(manager: SpreadsheetManager):
    ws_name = getconf("RATING_LIST_PAGE_NAME")
    ws = manager.get_worksheet(ws_name)
    values = ws.get_all_values()
    assert "NMD Username" in values[0]
    assert "Test" not in values[0]
