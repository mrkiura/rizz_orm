import pytest

from orm import Table, Column, ForeignKey


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
