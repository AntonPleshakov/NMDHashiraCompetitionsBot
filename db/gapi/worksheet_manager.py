class WorksheetManager:
    def __init__(self, worksheet):
        self._ws = worksheet
        self._cache = None

    def fetch(self):
        self._cache = self._ws.get_all_values(
            include_tailing_empty_rows=False, include_tailing_empty=False
        )

    def cache(self):
        if not self._cache:
            self.fetch()
        return self._cache

    def get_all_values(self):
        return self.cache()

    def add_row(self, row):
        row_index = len(self.cache())
        self._ws.insert_rows(row_index, row)
        self._ws.append(row)

        self.cache().append(row)

    def sort_table(self, column_index, sort_header=False, sort_order="DESCENDING"):
        start_range = (1, 1) if sort_header else (2, 1)
        cache = self.cache()
        end_range = (len(cache), len(cache[0]))
        self._ws.sort_range(start_range, end_range, column_index, sort_order)
        cache.sort(key=lambda x: x[column_index])

    def update_all_values(self, values, update_header=False):
        start_range = (1, 1) if update_header else (2, 1)
        self._ws.clear(start_range, self._ws.rows)
        self._ws.update_values(start_range, values, extend=True)
        self.fetch()
