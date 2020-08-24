class QueryBuilder:
    """
    QueryBuilder encapsulates desired query properties. It defines an
    executable procedure based on a given set of query properties. Such 
    procedure can be executed on a database (object).
    """

    def __init__(self):
        self._database = None
        self._table = None
        self._count = False
        self._columns_for_selection = []
        self._table_name = None
        self._conditions = [] # list of tuples (str, str)
        self._boolean_operators = [] # possible values: "and", "or"

    def bind_database(self, csv_database_obj):
        self._database = csv_database_obj

    def count_table_rows(self):
        self._count = True

    def is_counter(self):
        return self._count

    def select_table_column(self, column_name):
        self._columns_for_selection.append(column_name)

    def select_all_table_columns(self):
        self._columns_for_selection.append("*")

    def table_columns(self):
        return self._columns_for_selection

    def use_table(self, table_name):
        self._table_name = table_name

    def table_name(self):
        return self._table_name

    def add_condition(self, column_name, column_value):
        self._conditions.append((column_name, column_value))

    def conditions(self):
        return self._conditions

    def add_logical_or_operator(self):
        self._boolean_operators.append("or")

    def add_logical_and_operator(self):
        self._boolean_operators.append("and")

    def logical_operators(self):
        return self._boolean_operators

    def __bind_table(self):
        if not self._database:
            raise RuntimeError("Database is not available. Use bind_database() first.")
        self._table = self._database.get_data_table(self.table_name())
        if not self._table:
            raise RuntimeError(f"\"{self.table_name()}\" table is not available.")

    def execute(self):
        self.__bind_table()

        search_conditions_func = self.__define_search_conditions()
        return filter(search_conditions_func, self._table.rows())

    def print_execution_result(self):
        filtered_rows = self.execute()

        if self.is_counter():
            self.__print_number_of_rows(filtered_rows)
        else:
            self.__print_selected_row_values(filtered_rows)
        print()

    def __print_selected_row_values(self, table_rows):
        for row in table_rows:
            print(*[row[column_name] for column_name in self.__expand_asterisk_column()],
                  sep=', ')

    def __print_number_of_rows(self, table_rows):
        print(len(list(table_rows)))

    def __expand_asterisk_column(self):
        result = []
        for column in self.table_columns():
            if column == "*":
                result += self._table.headers()
            else:
                result.append(column)
        return result

    def __define_condition(self, column_name, column_value):
        if column_name not in self._table.headers():
            raise RuntimeError(f"\"{column_name}\" column does not exist in the table.")

        return lambda table_row : table_row[column_name] == column_value

    def __define_logical_and_operation(self, first_operand, second_operand):
        return lambda table_row : first_operand(table_row) and second_operand(table_row)

    def __define_logical_or_operation(self, first_operand, second_operand):
        return lambda table_row : first_operand(table_row) or second_operand(table_row)

    def __define_dummy_condition(self):
        return lambda table_row : True

    def __define_search_conditions(self):
        result = self.__define_dummy_condition() # for the sake of consistency

        if self.conditions():
            it = iter(self.conditions())
            cond_params = next(it)
            result = self.__define_condition(*cond_params)

            for i, next_cond_params in enumerate(it):
                if self.logical_operators()[i] == "and":
                    next_cond_func = self.__define_condition(*next_cond_params)
                    result = self.__define_logical_and_operation(result, next_cond_func)
                elif self.logical_operators()[i] == "or":
                    next_cond_func = self.__define_condition(*next_cond_params)
                    result = self.__define_logical_or_operation(result, next_cond_func)
                else:
                    raise NotImplementedError("Operator is not supprted")

        return result

    def print_query_state(self):
        print(id(self))

        if self.is_counter(): print("SELECT COUNT(*)")
        if self.table_columns(): print("SELECT ", self.table_columns())
        if self.table_name(): print("FROM ", self.table_name())
        if self.conditions(): print("WHERE ", self.conditions())
        if self.logical_operators(): print("logical operators: ", self.logical_operators())
