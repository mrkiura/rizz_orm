import pytest
from orm import Database, Table


def test_database_creation(db: Database):
    assert db.tables == [], "Database should start with no tables."


def test_table_creation(db: Database, UserProfile: type[Table]):
    assert 'userprofile' in db.tables, "UserProfile table should be created in the database."


def test_column_definition(UserProfile: type[Table]):
    assert hasattr(UserProfile, 'username'), "UserProfile should have a 'username' column."
    assert hasattr(UserProfile, 'email'), "UserProfile should have an 'email' column."
    assert UserProfile.username.sql_type == "TEXT", "UserProfile 'username' should be of type TEXT."
    assert UserProfile.email.sql_type == "TEXT", "UserProfile 'email' should be of type TEXT."


def test_foreign_key_definition(StatusUpdate: type[Table], UserProfile: type[Table]):
    assert hasattr(StatusUpdate, 'user_profile'), "StatusUpdate should have a 'user_profile' ForeignKey."
    assert StatusUpdate.user_profile.table == UserProfile, "StatusUpdate 'user_profile' should reference UserProfile."


def test_insert_and_query(db: Database, UserProfile: type[Table]):
    user = UserProfile(username="testuser", email="test@example.com")
    db.save(user)
    assert user.id is not None, "User should have an id after being saved to the database."

    queried_user = db.get(UserProfile, user.id)
    assert queried_user.username == "testuser", "Queried user should have the correct username."
    assert queried_user.email == "test@example.com", "Queried user should have the correct email."


def test_update_and_query(db: Database, UserProfile: type[Table]):
    user = UserProfile(username="updatable", email="update@example.com")
    db.save(user)
    user.email = "newemail@example.com"
    db.save(user)

    queried_user = db.get(UserProfile, user.id)
    assert queried_user.email == "newemail@example.com", "User email should be updated in the database."


def test_all_query(db: Database, UserProfile: type[Table]):
    user1 = UserProfile(username="user1", email="user1@example.com")
    user2 = UserProfile(username="user2", email="user2@example.com")
    db.save(user1)
    db.save(user2)

    users = db.all(UserProfile)
    assert len(users) == 2, "There should be two users in the database."
    assert set(user.username for user in users) == {"user1", "user2"}, "All users should be retrieved."


def test_foreign_key_query(db: Database, UserProfile: type[Table], StatusUpdate: type[Table]):
    user = UserProfile(username="fk_user", email="fkuser@example.com")
    db.save(user)
    status = StatusUpdate(content="Testing foreign keys", user_profile=user)
    db.save(status)

    queried_status = db.get(StatusUpdate, status.id)
    assert queried_status.user_profile.id == user.id, "StatusUpdate should reference the correct UserProfile."
    assert queried_status.user_profile.username == user.username, "The referenced UserProfile should have the correct username."


def test_update_record(db: Database, UserProfile: type[Table]):
    user = UserProfile(username="update_test", email="update_test@example.com")
    db.save(user)
    assert user.id is not None, "User should have an id after being saved to the database."

    user.email = "updated_email@example.com"
    db.update(user)

    updated_user = db.get(UserProfile, user.id)
    assert updated_user.email == "updated_email@example.com", "User email should be updated in the database."


def test_delete_record(db: Database, UserProfile: type[Table]):
    user = UserProfile(username="delete_test", email="delete_test@example.com")
    db.save(user)
    assert user.id is not None, "User should have an id after being saved to the database."

    db.delete(user)

    try:
        db.get(UserProfile, user.id)
        assert False, "Deleted user should not be found in the database."
    except Exception as e:
        assert str(e) == f"{UserProfile.__name__} instance with id {user.id} does not exist", "Exception message should indicate that the user does not exist."
