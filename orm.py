import inspect
import sqlite3
from typing import Tuple, List


# TODO: Use jinja2 templates for constructing SQL queries


class Database:
    def __init__(self, path: str):
        self.connection = sqlite3.Connection(path)

    def create(self, table):
        self.connection.execute(table._get_create_sql())

    def save(self, instance: "Table"):
        sql, values = instance._get_insert_sql()
        cursor = self.connection.execute(sql, values)
        instance._data["id"] = cursor.lastrowid
        self.connection.commit()

    def all(self, table: "Table"):
        pass

    @property
    def tables(self):
        SELECT_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type = 'table';"
        return {x[0] for x in self.connection.execute(SELECT_TABLES_SQL).fetchall()}


class Table:
    def __init__(self, **kwargs) -> None:
        self._data = {
            "id": None
        }
        for key, value in kwargs.items():
            self._data[key] = value

    def __getattribute__(self, key: str):
        _data = super().__getattribute__("_data")
        if key in _data:
            return _data[key]
        return super().__getattribute__(key)

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

    def _get_insert_sql(self) -> Tuple[str, List]:
        INSERT_SQL = "INSERT INTO {name} ({fields}) VALUES ({placeholders});"
        cls = self.__class__
        fields, placeholders, values = [], [], []

        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
                values.append(getattr(self, name))
                placeholders.append("?")
            elif isinstance(field, ForeignKey):
                fields.append(name + "_id")
                values.append(getattr(self, name).id)
                placeholders.append("?")

        fields = ", ".join(fields)
        placeholders = ", ".join(placeholders)

        sql = INSERT_SQL.format(
            name=cls.__name__.lower(),
            fields=fields,
            placeholders=placeholders
        )
        return sql, values


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
    def __init__(self, table):
        self.table = table
