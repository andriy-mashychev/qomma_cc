"""
Raw draft of the target BNF grammar:
    <query specification> ::= SELECT <select list> <table expression>
    <select list> ::= <select sublist> [ { <comma> <select sublist> }... ]
    <select sublist> ::= <value expression> | <asterisk>
    <value expression> ::= <column name> | <set function specification>
    <set function specification> ::= COUNT <left paren> <asterisk> <right paren>
    <table expression> ::= <from clause> [ <where clause> ] <semicolon>
    <from clause> ::= FROM <table reference>
    <where clause> ::= WHERE <search condition>
    <search condition> ::= <boolean term> | <search condition> OR <boolean term>
    <boolean term> ::= <boolean factor> | <boolean term> AND <boolean factor>
    <boolean factor> ::= <comparison predicate> | <left paren> <search condition> <right paren>
    <comparison predicate> ::= <column name> <equals operator> <character string literal>
    <character string literal> ::= <quote> [ <character set specification> ... ] <quote>
    <comma> ::= ,
    <equals operator> ::= =
    <semicolon> ::= ;
    <left paren> ::= (
    <right paren> ::= )
    <asterisk> ::= *
    <quote> ::= '
"""

import re
from src.query_builder import QueryBuilder

class QueryLangParser():
    """
    QueryLangParser parses SQL-like expressions. It does not translate them
    directly. Instead it creates internal query representation objects that can
    be bound to a database and executed later.
    """

    # Regular expressions for parsing specific query language sections
    _BLANK_LINE_TMPL = r"^\s*$"
    _SELECT_T_TMPL = r"^\s*select\s"            # SELECT terminal
    _COUNT_T_TMPL = r"^\s*count\(\*\)\s"        # COUNT(*) terminal
    _ASTERISK_T_TMPL = r"^\s*\*"                # * terminal
    _COLUMN_ID_TMPL = r"^\s*(\w+)"              # column identifier
    _COMMA_ASTERISK_TMPL = r"^\s*,\s*\*"        # * terminal after comma
    _COMMA_COLUMN_ID_TMPL = r"^\s*,\s*(\w+)"    # * column identifier after comma
    _FROM_T_TABLE_ID_TMPL = r"^\s*from\s+(\w+)" # FROM terminal followed by a table identifier
    _WHERE_T_TMPL = r"^\s+where\s"              # WHERE terminal
    _SEMICOLON_T_TMPL = r"^\s*;"                # ; terminal
    _SEARCH_CONDITION_TMPL = r"^\s*(\w+)\s*=\s*[‘']([\w ]+)['’]" # equality search condition
    _AND_OPERATOR_T_TMPL = r"^\s*and\s"         # AND terminal
    _OR_OPERATOR_T_TMPL = r"^\s*or\s"           # OR terminal

    # Compiled regular expressions for parsing specific query language sections
    BLANK_LINE_RE = re.compile(_BLANK_LINE_TMPL, re.IGNORECASE)
    SELECT_T_RE = re.compile(_SELECT_T_TMPL, re.IGNORECASE)
    COUNT_T_RE = re.compile(_COUNT_T_TMPL, re.IGNORECASE)
    ASTERISK_T_RE = re.compile(_ASTERISK_T_TMPL, re.IGNORECASE)
    COLUMN_ID_RE = re.compile(_COLUMN_ID_TMPL, re.IGNORECASE)
    COMMA_ASTERISK_RE = re.compile(_COMMA_ASTERISK_TMPL, re.IGNORECASE)
    COMMA_COLUMN_ID_RE = re.compile(_COMMA_COLUMN_ID_TMPL, re.IGNORECASE)
    FROM_T_TABLE_ID_RE = re.compile(_FROM_T_TABLE_ID_TMPL, re.IGNORECASE)
    WHERE_T_RE = re.compile(_WHERE_T_TMPL, re.IGNORECASE)
    SEMICOLON_T_RE = re.compile(_SEMICOLON_T_TMPL, re.IGNORECASE)
    SEARCH_CONDITION_RE = re.compile(_SEARCH_CONDITION_TMPL, re.IGNORECASE)
    AND_OPERATOR_T_RE = re.compile(_AND_OPERATOR_T_TMPL, re.IGNORECASE)
    OR_OPERATOR_T_RE = re.compile(_OR_OPERATOR_T_TMPL, re.IGNORECASE)

    _DEFAULT_QUERY_BUILDER_CLASS = QueryBuilder

    def __init__(self, query_builder_cls=_DEFAULT_QUERY_BUILDER_CLASS):
        self._query_builder_cls = query_builder_cls
        self._built_queries = []

    def clear_queries(self):
        self._built_queries.clear()

    def get_queries(self):
        return self._built_queries

    def pop_query(self):
        return self._built_queries.pop(0)

    def expr(self, query_str):
        select_terminal = self.SELECT_T_RE.match(query_str)
        blank_str = self.BLANK_LINE_RE.match(query_str)

        if select_terminal:
            remaining_str = query_str[select_terminal.end():]
            query_builder_obj = self._query_builder_cls()
            self._select_list(remaining_str, query_builder_obj)
        elif not query_str or blank_str:
            pass
        else:
            raise SyntaxError("SQL syntax error")

    def _select_list(self, look_ahead_str, query_builder_obj):
        count_terminal = self.COUNT_T_RE.match(look_ahead_str)
        select_list_asterisk = self.ASTERISK_T_RE.match(look_ahead_str)
        select_list_column = self.COLUMN_ID_RE.match(look_ahead_str)

        if count_terminal:
            query_builder_obj.count_table_rows() # memorize COUNT(*)
            remaining_str = look_ahead_str[count_terminal.end():]
            self._table_expr(remaining_str, query_builder_obj)
        elif select_list_asterisk:
            query_builder_obj.select_all_table_columns() # memorize *
            remaining_str = look_ahead_str[select_list_asterisk.end():]
            self._select_sublist_stmt(remaining_str, query_builder_obj)
        elif select_list_column:
            query_builder_obj.select_table_column(select_list_column.group(1))
            remaining_str = look_ahead_str[select_list_column.end():]
            self._select_sublist_stmt(remaining_str, query_builder_obj)
        else:
            raise SyntaxError("SQL syntax error")

    def _select_sublist_stmt(self, look_ahead_str, query_builder_obj):
        select_sublist_asterisk = self.COMMA_ASTERISK_RE.match(look_ahead_str)
        select_sublist_column = self.COMMA_COLUMN_ID_RE.match(look_ahead_str)

        if select_sublist_asterisk:
            query_builder_obj.select_all_table_columns() # memorize *
            remaining_str = look_ahead_str[select_sublist_asterisk.end():]
            self._select_sublist_stmt(remaining_str, query_builder_obj)
        elif select_sublist_column:
            query_builder_obj.select_table_column(select_sublist_column.group(1))
            remaining_str = look_ahead_str[select_sublist_column.end():]
            self._select_sublist_stmt(remaining_str, query_builder_obj)
        else:
            self._table_expr(look_ahead_str, query_builder_obj)

    def _table_expr(self, look_ahead_str, query_builder_obj):
        from_clause = self.FROM_T_TABLE_ID_RE.match(look_ahead_str)

        if from_clause:
            query_builder_obj.use_table(from_clause.group(1)) # memorize the table name
            remaining_str = look_ahead_str[from_clause.end():]
            self._where_expr(remaining_str, query_builder_obj)
        else:
            raise SyntaxError("SQL syntax error")

    def _where_expr(self, look_ahead_str, query_builder_obj):
        where_terminal = self.WHERE_T_RE.match(look_ahead_str)
        semicolon_terminal = self.SEMICOLON_T_RE.match(look_ahead_str)

        if where_terminal:
            remaining_str = look_ahead_str[where_terminal.end():]
            self._search_conditions_stmt(remaining_str, query_builder_obj)
        elif semicolon_terminal:
            # the query object has been successfully built, let's store it
            self._built_queries.append(query_builder_obj)
            # repeat the whole parsing process if there is one more query
            remaining_str = look_ahead_str[semicolon_terminal.end():]
            self.expr(remaining_str)
        else:
            raise SyntaxError("SQL syntax error")

    def _search_conditions_stmt(self, look_ahead_str, query_builder_obj):
        search_condition = self.SEARCH_CONDITION_RE.match(look_ahead_str)

        if search_condition:
            query_builder_obj.add_condition(search_condition.group(1),
                                            search_condition.group(2))
            remaining_str = look_ahead_str[search_condition.end():]
            self._search_conditions_combination(remaining_str, query_builder_obj)
        else:
            raise SyntaxError("SQL syntax error in the WHERE clause condition(s)")

    def _search_conditions_combination(self, look_ahead_str, query_builder_obj):
        and_operator = self.AND_OPERATOR_T_RE.match(look_ahead_str)
        or_operator = self.OR_OPERATOR_T_RE.match(look_ahead_str)
        semicolon_terminal = self.SEMICOLON_T_RE.match(look_ahead_str)

        if and_operator:
            query_builder_obj.add_logical_and_operator()
            remaining_str = look_ahead_str[and_operator.end():]
            self._search_conditions_stmt(remaining_str, query_builder_obj)
        elif or_operator:
            query_builder_obj.add_logical_or_operator()
            remaining_str = look_ahead_str[or_operator.end():]
            self._search_conditions_stmt(remaining_str, query_builder_obj)
        elif semicolon_terminal:
            # the query object has been successfully built, let's store it
            self._built_queries.append(query_builder_obj)
            # repeat the whole parsing process if there is one more query
            remaining_str = look_ahead_str[semicolon_terminal.end():]
            self.expr(remaining_str)
        else:
            raise SyntaxError("SQL syntax error in the WHERE clause condition(s)")
