# Qomma

Qomma is a command line utility for running SQL queries against CSV files.

This is a prototype with limited functionality. SQL queries are case-insensitive, end with “;” and get executed when you hit “Enter”. The ​\​q​ command exits the program.

The following SQL-syntax is supported:

```sql
SELECT​ select_expression ​​FROM​ ​table_name​ WHERE ​condition_expression​;
```

*select_expression* ​​is either *​column_selector​* or *​count_expression*.

*column_selector​* ​​can be an individual item or a comma separated list of either *​column_name​​* or​ *\** which means “all the columns”.
*count_expression* ​​represents COUNT(*) and returns the scalar value of the number of records.

WHERE part is optional.
*condition_expression​* is a boolean expression, either a single ​condition​ or combination of conditions​ with AND, OR. A condition​ is only the equality check: *​column_name​= ‘​value​’*. Every value is casted to a string for conditional checks.

## Usage

To run it open a shell, enter the project directory and type the following:

```bash
./qomma.py tests/resources
```

The script requires one command line argument, which should be the path to a directory containing CSV files that you would like to query.

If you are still not sure about the usage, then type this:

```bash
./qomma.py -h
```
