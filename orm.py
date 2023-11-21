import sqlite3


class Database:
    def __init__(self, path: str):
        self.connection = sqlite3.Connection(path)

    @property
    def tables(self):
        return []


class Table:
    ...


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
