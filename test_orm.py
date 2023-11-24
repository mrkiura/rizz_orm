import pytest
import sqlite3
from orm import Database, Table

from pprint import pprint


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


def test_create_author_instance(db: Database, Author: type[Table]):
    db.create(Author)

    alex = Author(name="Alex Mwangi", age=69)

    assert alex.name == "Alex Mwangi"
    assert alex.age == 69
    assert alex.id is None


def test_save_author_instance(db: Database, Author: type[Table]):
    db.create(Author)
    alex = Author(name="Alex Mwangi", age=69)
    db.save(alex)
    assert alex._get_insert_sql() == (
        "INSERT INTO author (age, name) VALUES (?, ?);",
        [69, "Alex Mwangi"]
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


def test_query_all(db: Database, Author: Table):
    db.create(Author)

    anna = Author(name="Anna Beba", age=43)
    jane = Author(name="Jane Doe", age=28)

    for author in {anna, jane}:
        db.save(author)

    authors = db.all(Author)

    assert Author._get_select_all_sql() == (
        "SELECT id, age, name FROM author;",
        ["id", "age", "name"]
    )
    assert len(authors) == 2
    assert isinstance(authors[0], Author)
    assert {author.age for author in authors} == {43, 28}


def test_get_author(db, Author):
    db.create(Author)
    paul = Author(name="Paul Apostle", age=28)
    db.save(paul)

    query_result = db.get(Author, id=1)

    assert Author._get_select_where_sql(id=1) == (
        "SELECT id, age, name FROM author WHERE id = ?;",
        ["id", "age", "name"],
        [1]
    )
    assert isinstance(query_result, Author)
    assert query_result.age == 28
    assert query_result.name == "Paul Apostle"
    assert query_result.id == 1


def test_get_book(db: type[Database], Author: type[Table], Book: type[Table]):
    db.create(Author)
    db.create(Book)

    penny = Author(name="Penny", age=69)
    rajesh = Author(name="Rajesh", age=50)

    book1 = Book(title="Writing a book", published=False, author=penny)
    book2 = Book(title="How to meet Lions", published=True, author=rajesh)
    db.save(penny)
    db.save(rajesh)

    db.save(book1)
    db.save(book2)

    book1_query_result = db.get(Book, book1.id)

    assert book1_query_result.title == book1.title
    assert book1_query_result.author.name == penny.name
    assert book1_query_result.author.id == penny.id


def test_query_all_books_foreign_key(db, Author, Book):
    db.create(Author)
    db.create(Book)
    wainaina = Author(name="Wainaina Miano", age=43)
    mercy = Author(name="Mercy Cindy Mutua", age=50)
    book = Book(title="Writing a book", published=False, author=wainaina)
    book2 = Book(title="No River, No sauce", published=True, author=mercy)
    db.save(wainaina)
    db.save(mercy)
    db.save(book)
    db.save(book2)

    books = db.all(Book)

    assert len(books) == 2
    assert books[1].author.name == mercy.name
