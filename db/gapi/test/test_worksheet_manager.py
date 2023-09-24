from typing import List

import pytest

from config.config import getconf
from db.gapi.gsheets_manager import GSheetsManager
from db.gapi.worksheet_manager import WorksheetManager, Matrix


@pytest.fixture
def manager_factory():
    def create_manager(spreadsheet_name: str, worksheet_name: str) -> WorksheetManager:
        return GSheetsManager().open(spreadsheet_name).get_worksheet(worksheet_name)

    return create_manager


@pytest.fixture
def manager(manager_factory):
    ss_name = getconf("TEST_GTABLE_NAME")
    ws_name = getconf("TEST_PAGE_NAME")
    return manager_factory(ss_name, ws_name)


@pytest.mark.parametrize(
    "values", [[["1", "2", "3"], ["4", "5", "6"]], [["9", "8"], ["7", "6"], ["5", "4"]]]
)
@pytest.mark.gdrive_access
def test_update_values(manager: WorksheetManager, values: Matrix):
    manager.update_all_values(values, True)

    actual_values = manager.get_all_values()
    assert actual_values == values


@pytest.mark.gdrive_access
def test_update_values_with_header(manager: WorksheetManager):
    header = ["First", "Second", "Third"]
    values_with_header = [header, ["1", "2", "3"]]
    manager.update_all_values(values_with_header, True)

    actual_values = manager.get_all_values()
    assert actual_values == values_with_header

    new_values = ["4", "5", "6"]
    manager.update_all_values([new_values], False)

    actual_values = manager.get_all_values()
    assert len(actual_values) == 2
    assert actual_values[0] == header
    assert actual_values[1] == new_values


def merge_columns(columns: List[Matrix]) -> Matrix:
    result: Matrix = []
    for row in zip(*columns):
        merged_row = []
        for v in list(row):
            merged_row.append(v[0])
        result.append(merged_row)
    return result


ASC_ROW_0_9 = [str(i) for i in range(10)]
DESC_ROW_9_0 = [str(i) for i in range(9, -1, -1)]
ASC_COL = [[v] for v in ASC_ROW_0_9]
DESC_COL = [[v] for v in DESC_ROW_9_0]
DAD_MATRIX = merge_columns([DESC_COL, ASC_COL, DESC_COL])
ADA_MATRIX = merge_columns([ASC_COL, DESC_COL, ASC_COL])
HEADER = [["First", "Second", "Third"]]
DAD_HEADER = HEADER + DAD_MATRIX
ADA_HEADER = HEADER + ADA_MATRIX


@pytest.mark.parametrize(
    "input_values, expected_values, column_index, sort_header, sort_order",
    [
        (DESC_COL, ASC_COL, 0, True, "ASCENDING"),
        (ASC_COL, DESC_COL, 0, True, "DESCENDING"),
        (ADA_MATRIX, DAD_MATRIX, 1, True, "ASCENDING"),
        (DAD_MATRIX, ADA_MATRIX, 1, True, "DESCENDING"),
        (ADA_HEADER, DAD_HEADER, 1, False, "ASCENDING"),
        (DAD_HEADER, ADA_HEADER, 1, False, "DESCENDING"),
    ],
)
@pytest.mark.gdrive_access
@pytest.mark.slow
def test_sort_values(
    manager: WorksheetManager,
    input_values: Matrix,
    expected_values: Matrix,
    column_index: int,
    sort_header: bool,
    sort_order: str,
):
    # Given
    manager.update_all_values(input_values, True)

    # When
    manager.sort_table(column_index, sort_header, sort_order)

    # Then
    actual_values = manager.get_all_values()
    assert actual_values == expected_values


MAT_3V3 = []
for i in range(3):
    MAT_3V3.append([])
    for j in range(3):
        MAT_3V3[i].append(str(j + i * 3))


@pytest.mark.parametrize(
    "row",
    [["1"], ["1", "2"], ["2", "1"], []],
)
@pytest.mark.gdrive_access
@pytest.mark.slow
def test_add_row(manager: WorksheetManager, row: List[str]):
    init_values = MAT_3V3
    manager.update_all_values(init_values, True)

    manager.add_row(row)

    expected = init_values + [row]
    assert manager.get_all_values() == expected


@pytest.mark.gdrive_access
def test_add_row_after_empty(manager: WorksheetManager):
    init_values = MAT_3V3
    manager.update_all_values(init_values, True)
    empty_row = []
    two_cell_row = ["1", "2"]

    manager.add_row(empty_row)
    manager.add_row(two_cell_row)

    expected = init_values + [empty_row] + [two_cell_row]
    assert manager.get_all_values() == expected
