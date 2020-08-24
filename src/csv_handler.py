import os
import re
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

class CSVFilesFinder():
    """DirectoryReader identifies CSV files located in a specified folder."""

    CSV_FILE_EXT_RE = re.compile(r".+\.csv$", re.IGNORECASE)

    def __init__(self, dir_path):
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            self._abs_dir_path = os.path.abspath(dir_path)
        else:
            raise RuntimeError("Please provide a valid directory path")

        self.__find_csv_files()

    def no_files_available(self):
        if self._csv_files:
            return False
        else:
            return True

    def print_files_info(self):
        print(f"{len(self._csv_files)} tables found:")
        if (self._csv_files):
            for filename in sorted(self._csv_files): print(filename)
        print()

    def __find_csv_files(self):
        files = os.listdir(self._abs_dir_path)
        self._csv_files = [f for f in files if self.CSV_FILE_EXT_RE.match(f)]

class CSVDataBase(CSVFilesFinder):
    """
    CSVDataBase represents a set of data tables corresponding to the CSV files
    located in a specified folder. It relies on its parent class capabilities
    when it comes to locating CSV files.
    """

    _DEFAULT_DATA_TABLE_CLASS = DataTable

    def __init__(self, dir_path, data_table_cls=_DEFAULT_DATA_TABLE_CLASS):
        super(CSVDataBase, self).__init__(dir_path)

        self._data_table_cls = data_table_cls
        self._database = {}
        self.__create_database()

    def get_data_table(self, table_name):
        return self._database.get(table_name)

    def __create_database(self):
        for f in self._csv_files:
            data_table = self.__instantiate_data_table(f)
            self._database[data_table.name()] = data_table

    def __instantiate_data_table(self, file_name):
        return self._data_table_cls(os.path.join(self._abs_dir_path, file_name))
