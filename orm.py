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

    def get(self, table: type["Table"], id: str | int):
        sql, fields, params = table._get_select_where_sql(id)
        row = self.connection.execute(sql, params).fetchone()
        if row is None:
            raise Exception(f"{table.__name__} instance with id {id} does not exist")
        instance = table()
        for field, value in zip(fields, row):
            if field.endswith("_id"):
                field = field[:-3]
                fk = getattr(table, field)
                value = self.get(fk.table, id=value)
            setattr(instance, field, value)
        return instance

    def save(self, instance: "Table"):
        sql, values = instance._get_insert_sql()
        cursor: sqlite3.Cursor = self.connection.execute(sql, values)
        instance._data["id"] = cursor.lastrowid
        self.connection.commit()

    def update(self, instance: "Table"):
        sql, values = instance._get_update_sql()
        self.connection.execute(sql, values)
        self.connection.commit()

    def delete(self, table: type["Table"], id: Union[str, int]):
        sql, parameters = table._get_delete_sql(id)
        self.connection.execute(sql, parameters)
        self.connection.commit()

    def all(self, table: type["Table"]) -> List["Table"]:
        sql, fields = table._get_select_all_sql()

        results = []
        for row in self.connection.execute(sql).fetchall():
            instance = table()
            for field, value in zip(fields, row):
                if field.endswith("_id"):
                    field = field[:-3]
                    fk = getattr(table, field)
                    value = self.get(fk.table, id=value)
                setattr(instance, field, value)
            results.append(instance)
        return results

    @property
    def tables(self) -> List[str]:
        SELECT_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type = 'table';"
        return [x[0] for x in self.connection.execute(SELECT_TABLES_SQL).fetchall()]


class Table:
    def __init__(self, **kwargs) -> None:
        self._data: dict[str, Value] = {"id": None}
        for key, value in kwargs.items():
            self._data[key] = value

    def __getattribute__(self, key: str):
        _data = super().__getattribute__("_data")
        if key in _data:
            return _data[key]
        return super().__getattribute__(key)

    def __setattr__(self, key: str, value: Value) -> None:
        super().__setattr__(key, value)
        if key in self._data:
            self._data[key] = value

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

    @property
    def fields(self) -> List[str]:
        fields, cls = [], type(self)
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
        return fields

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
            name=cls.__name__.lower(), fields=fields, placeholders=placeholders
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

        sql = SELECT_ALL_SQL.format(name=cls.__name__.lower(), fields=", ".join(fields))

        return sql, fields

    def asdict(self) -> dict:
        serialized = {field: getattr(self, field) for field in self.fields}
        serialized["id"] = self.id

        return serialized

    @classmethod
    def _get_select_where_sql(cls, id: str | int) -> Tuple[str, List[str], List[str]]:
        SELECT_WHERE_SQL = "SELECT {fields} FROM {name} WHERE id = ?;"
        fields = ["id"]
        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
            if isinstance(field, ForeignKey):
                fields.append(name + "_id")

        sql = SELECT_WHERE_SQL.format(
            name=cls.__name__.lower(), fields=", ".join(fields)
        )
        params = [id]
        return sql, fields, params

    def _get_update_sql(self):
        UPDATE_SQL = "UPDATE {name} SET {fields} WHERE id = ?"
        cls = self.__class__
        fields, values = [], []

        for name, field in inspect.getmembers(cls):
            if isinstance(field, Column):
                fields.append(name)
                values.append(getattr(self, name))
            elif isinstance(field, ForeignKey):
                fields.append(name + "_id")
                values.append(getattr(self, name).id)
        values.append(getattr(self, "id"))

        sql = UPDATE_SQL.format(
            name=cls.__name__.lower(),
            fields=", ".join([f"{field} = ?" for field in fields]),
        )

        return sql, values

    @classmethod
    def _get_delete_sql(cls, id):
        DELETE_SQL = "DELETE FROM {name} WHERE id = ?"

        sql = DELETE_SQL.format(name=cls.__name__.lower())

        return sql, [id]


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
