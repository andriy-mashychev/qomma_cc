import pytest

# from src import query_lang_parser

@pytest.fixture(scope="module")
def csv_files_location():
    return 'tests/resources/'
