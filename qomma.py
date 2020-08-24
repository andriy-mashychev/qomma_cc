#!/usr/bin/env python3

import argparse
from src.query_lang_parser import QueryLangParser
from src.csv_handler import CSVFilesFinder, CSVDataBase

class Qomma():
    """
    Qomma implements a command line utility for running SQL queries against CSV
    files.
    """

    _DEFAULT_FILES_FINDER_CLASS = CSVFilesFinder
    _DEFAULT_DATABASE_CLASS = CSVDataBase
    _DEFAULT_PARSER_CLASS = QueryLangParser

    def __init__(self,
                 files_finder_cls=_DEFAULT_FILES_FINDER_CLASS,
                 database_cls=_DEFAULT_DATABASE_CLASS,
                 parser_cls=_DEFAULT_PARSER_CLASS):
        self._files_finder_cls = files_finder_cls
        self._parser_cls = parser_cls
        self._parser = None
        self._database_cls = database_cls
        self._database = None
        self._directory = None

    def run(self):
        self.__parse_command_line_argument()
        self.__print_directory_contents()
        self.__create_database()
        self.__instantiate_parser()
        self.__readline_loop()

    def set_directory(self, dir_name):
        self._directory = dir_name

    def __parse_command_line_argument(self):
        parser = argparse.ArgumentParser(description="Run SQL queries against CSV files.")
        parser.add_argument("directory", help="Path to a directory containing CSV files")
        self._directory = parser.parse_args().directory

    def __print_directory_contents(self):
        self._files_finder_cls(self._directory).print_files_info()

    def __create_database(self):
        self._database = self._database_cls(self._directory)

    def database(self):
        return self._database
    
    def __instantiate_parser(self):
        self._parser = self._parser_cls()
        
    def __console_info_message(self):
        return f"{self._directory}# "

    def __translate(self, sql_query):
        self._parser.expr(sql_query)
        for query in self._parser.get_queries():
            query.bind_database(self.database())
            query.print_execution_result()
        self._parser.clear_queries()

    def __readline_loop(self):
        while True:
            try: input_string = input(self.__console_info_message())
            except EOFError: break
            except KeyboardInterrupt: break

            if not input_string: continue
            elif input_string.__contains__("\\q"): break
            self.__translate(input_string)

def main(): Qomma().run()

if __name__ == "__main__": main()
