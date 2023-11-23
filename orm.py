import inspect
import sqlite3
from typing import Tuple, List, Union


# TODO: Use jinja2 templates for constructing SQL queries

Value = Union[str, int, None, float, bytes, bool]


class Database:
    def __init__(self, path: str):
        self.connection = sqlite3.Connection(path)

    def create(self, table: type["Table"]):
        self.connection.execute(table._get_create_sql())

    def save(self, instance: "Table"):
        sql, values = instance._get_insert_sql()
        cursor: sqlite3.Cursor = self.connection.execute(sql, values)
        instance._data["id"] = cursor.lastrowid
        self.connection.commit()

    def all(self, table: type["Table"]) -> List["Table"]:
        sql, fields = table._get_select_all_sql()

        results = []
        for row in self.connection.execute(sql).fetchall():
            instance = table()
            for field, value in zip(fields, row):
                setattr(instance, field, value)
            results.append(instance)
        return results

    @property
    def tables(self) -> List[str]:
        SELECT_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type = 'table';"
        return [x[0] for x in self.connection.execute(SELECT_TABLES_SQL).fetchall()]


class Table:
    def __init__(self, **kwargs) -> None:
        self._data: dict[str, Value] = {
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
    def _get_create_sql(cls) -> str:
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

    def _get_insert_sql(self) -> Tuple[str, List[Value]]:
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

    @classmethod
    def _get_select_all_sql(cls) -> Tuple[str, List[str]]:
        SELECT_ALL_SQL = "SELECT {fields} FROM {name};"

        fields = ["id"]
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
            if isinstance(field, ForeignKey):
                fields.append(name + "_id")

        sql = SELECT_ALL_SQL.format(
            name=cls.__name__.lower(),
            fields=", ".join(fields)
        )

        return sql, fields


class Column:

    def __init__(self, column_type: type) -> None:
        self._type = column_type

    @property
    def sql_type(self) -> str:
        TYPE_MAP: dict[type, str] = {
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
