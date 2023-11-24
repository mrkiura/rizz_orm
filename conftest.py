import os
import pytest
from orm import Database, Table, Column, ForeignKey


@pytest.fixture
def db() -> Database:
    """Database fixture that creates a new test database for each test session."""
    db_path = "test.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    test_db = Database(db_path)
    yield test_db
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def UserProfile(db: Database) -> type[Table]:
    """UserProfile model fixture."""
    class UserProfile(Table):
        username = Column(str)
        email = Column(str)
    db.create(UserProfile)
    return UserProfile


@pytest.fixture
def StatusUpdate(db: Database, UserProfile: type[Table]) -> type[Table]:
    """StatusUpdate model fixture with a foreign key to UserProfile."""
    class StatusUpdate(Table):
        content = Column(str)
        user_profile = ForeignKey(UserProfile)
    db.create(StatusUpdate)
    return StatusUpdate
