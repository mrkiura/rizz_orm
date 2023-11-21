import os
import pytest
from orm import Database, Table, Column, ForeignKey


@pytest.fixture
def Author():
    class Author(Table):
        name = Column(str)
        age = Column(int)

    return Author


@pytest.fixture
def Book(Author):
    class Book(Table):
        title = Column(str)
        published = Column(int)
        author = ForeignKey(Author)

    return Book


@pytest.fixture
def db():
    DB_PATH = "./test.db"
    if os.path.exists(DB_PATH):
        os.remove("./test.db")
    db = Database(DB_PATH)
    return db
