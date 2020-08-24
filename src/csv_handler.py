import os
from csv import DictReader

class DataTable:
    """DataTable is a CSV file wrapper providing convenient access methods."""

    def __init__(self, abs_file_path):
        self._abs_file_path = abs_file_path
        self._name = os.path.basename(abs_file_path).split(".")[0]
        self._rows = []
        self._header_fields = []

    def headers(self):
        if not self._header_fields: self.__read_table_headers()
        return self._header_fields

    def name(self):
        return self._name

    def rows(self):
        if not self._rows: self.__read_table_content()
        return self._rows

    def __read_table_headers(self):
        with open(self._abs_file_path) as csv_file:
            self._header_fields = DictReader(csv_file, skipinitialspace=True).fieldnames

    def __read_table_content(self):
        with open(self._abs_file_path) as csv_file:
            self._rows = [row for row in DictReader(csv_file, skipinitialspace=True)]
