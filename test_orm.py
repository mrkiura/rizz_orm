import pytest
import sqlite3
from orm import Database, Table


def test_create_db(db):
    assert isinstance(db.connection, sqlite3.Connection)
    assert len(db.tables) == 0


def test_define_tables(Author, Book):
    assert Author.name._type == str
    assert Book.author.table == Author

    assert Author.name.sql_type == "TEXT"
    assert Author.age.sql_type == "INTEGER"

#
def test_create_tables(db, Author, Book):
    db.create(Author)
    db.create(Book)

    author_sql = Author._get_create_sql()
    assert author_sql == "CREATE TABLE IF NOT EXISTS author (id INTEGER PRIMARY KEY AUTOINCREMENT, age INTEGER, name TEXT);"

    book_sql = Book._get_create_sql()
    assert book_sql == "CREATE TABLE IF NOT EXISTS book (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, published INTEGER, title TEXT);"

    for table in ("author", "book"):
        assert table in db.tables


def test_create_author_instance(db: Database, Author: Table):
    db.create(Author)

    alex = Author(name="Alex Mwangi", age=69)

    assert alex.name == "Alex Mwangi"
    assert alex.age == 69
    assert alex.id is None


def test_save_author_instance(db: Database, Author: Table):
    db.create(Author)
    alex = Author(name="Alex Mwangi", age=69)
    db.save(alex)
    assert alex._get_insert_sql() == (
        "INSERT INTO author (age, name) VALUES (?, ?);",
        [23, "John Doe"]
    )
    assert alex.id == 1

    jane = Author(name="Jane Doe", age=28)
    db.save(jane)
    assert jane.id == 2

    anna = Author(name="Anna Beba", age=43)
    db.save(anna)
    assert anna.id == 3

    johnte = Author(name="John Te", age=39)
    db.save(johnte)
    assert johnte.id == 4
