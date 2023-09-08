from typing import List, Optional

from pygsheets.worksheet import Worksheet

Matrix = List[List[str]]


class WorksheetManager:
    def __init__(self, worksheet: Worksheet):
        self._ws: Worksheet = worksheet
        self._cache: Optional[Matrix] = None

    def fetch(self):
        self._cache = self._ws.get_all_values(
            include_tailing_empty_rows=False, include_tailing_empty=False
        )

    def cache(self) -> Matrix:
        if not self._cache:
            self.fetch()
        return self._cache

    def get_all_values(self) -> Matrix:
        return self.cache()

    def add_row(self, row: List[str]):
        row_index = len(self.cache())
        self._ws.insert_rows(row_index, row)
        self.cache().append(row)

    def sort_table(
        self,
        column_index: int,
        sort_header: bool = False,
        sort_order: str = "DESCENDING",
    ):
        start_range = (1, 1) if sort_header else (2, 1)
        cache = self.cache()
        end_range = (len(cache), len(cache[0]))
        self._ws.sort_range(start_range, end_range, column_index, sort_order)
        cache.sort(key=lambda x: x[column_index])

    def update_all_values(self, values: Matrix, update_header: bool = False):
        start_range = (1, 1) if update_header else (2, 1)
        self._ws.clear(start_range, self._ws.rows)
        self._ws.update_values(start_range, values, extend=True)
        self.fetch()
