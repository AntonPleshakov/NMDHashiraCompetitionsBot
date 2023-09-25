from typing import List, Optional

from pygsheets.worksheet import Worksheet

Matrix = List[List[str]]


class WorksheetManager:
    def __init__(self, worksheet: Worksheet):
        self._ws: Worksheet = worksheet
        self._cache: Optional[Matrix] = None
        self._header_range = ()

    def fetch(self):
        self._cache = self._ws.get_all_values(
            include_tailing_empty_rows=False, include_tailing_empty=False
        )

    def cache(self) -> Matrix:
        if not self._cache:
            self.fetch()
        return self._cache

    def bold_cells(self, end_range: tuple, to_bold: bool = True):
        start_range = (1, 1)
        self._ws.apply_format(
            [[start_range, end_range]], {"textFormat": {"bold": to_bold}}
        )

    def set_header(self, header: Matrix):
        if self._header_range:
            self.bold_cells(self._header_range, False)
        self._ws.frozen_rows = len(header)
        self.update_all_values(header, True)
        if len(header) > 0:
            self._header_range = (len(header), len(header[0]))
            self.bold_cells(self._header_range)
        self.fetch()

    def get_all_values(self) -> Matrix:
        return self.cache()

    def add_row(self, row: List[str]):
        row_index = len(self.cache())
        self._ws.insert_rows(row=row_index, values=row)
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
        self.fetch()

    def update_all_values(self, values: Matrix, update_header: bool = False):
        start_range = (1, 1) if update_header else (2, 1)
        self._ws.clear(start_range, (self._ws.cols, self._ws.rows))
        values = [[]] if not values else values
        self._ws.update_values(start_range, values, extend=True)
        self.fetch()
