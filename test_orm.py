import sqlite3
import pytest

from orm import Database


def test_create_db():
    db = Database("./test.db")

    assert isinstance(db.connection, sqlite3.Connection)
    assert db.tables == []


def test_define_tables(Author, Book):
    assert Author.name.type == str
    assert Book.author.table == Author

    assert Author.name.sql_type == "TEXT"
    assert Author.age.sql_type == "INTEGER"
