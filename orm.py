import inspect
import sqlite3


# TODO: Use jinja2 templates for constructing SQL


class Database:
    def __init__(self, path: str):
        self.connection = sqlite3.Connection(path)

    @property
    def tables(self):
        return []

    def create(self, table):
        self.connection.execute(table._get_create_sql())


class Table:
    @classmethod
    def _get_create_sql(cls):
        CREATE_TABLE_SQL = "CREATE TABLE IF NOT EXISTS {name} ({fields});"
        fields = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT",
        ]

        for column_name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(f"{column_name} {field.sql_type}")
            elif isinstance(field, ForeignKey):
                fields.append(f"{column_name}_id INTEGER")

        fields = ", ".join(fields)
        table_name = cls.__name__.lower()
        return CREATE_TABLE_SQL.format(name=table_name, fields=fields)


class Column:

    def __init__(self, column_type) -> None:
        self._type = column_type

    @property
    def sql_type(self):
        TYPE_MAP = {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            bytes: "BLOB",
            bool: "INTEGER",  # 0 or 1
        }
        return TYPE_MAP[self._type]


class ForeignKey:
    def __init__(self, table) -> None:
        self.table = table
