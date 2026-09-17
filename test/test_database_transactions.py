import pytest
from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal
from database.models import User


def test_database_session_can_open_and_close():
    session = SessionLocal()

    try:
        assert session is not None
    finally:
        session.close()


def test_database_session_can_execute_query():
    session = SessionLocal()

    try:
        user_count = session.query(User).count()

        assert isinstance(user_count, int)
        assert user_count >= 0
    finally:
        session.close()


def test_database_transaction_rollback_removes_uncommitted_user():
    session = SessionLocal()

    test_email = "rollback_test_unique@tangle.test"

    try:
        user = User(
            name="Rollback Test User",
            email=test_email,
            role="ANALYST",
        )

        session.add(user)
        session.flush()

        assert (
            session.query(User)
            .filter(User.email == test_email)
            .count()
            == 1
        )

        session.rollback()

        assert (
            session.query(User)
            .filter(User.email == test_email)
            .count()
            == 0
        )

    finally:
        session.rollback()
        session.close()


def test_database_transaction_commit_persists_user_then_cleanup():
    session = SessionLocal()

    test_email = "commit_test_unique@tangle.test"

    try:
        user = User(
            name="Commit Test User",
            email=test_email,
            role="ANALYST",
        )

        session.add(user)
        session.commit()

        persisted_user = (
            session.query(User)
            .filter(User.email == test_email)
            .first()
        )

        assert persisted_user is not None
        assert persisted_user.email == test_email

    finally:
        session.query(User).filter(User.email == test_email).delete(
            synchronize_session=False
        )
        session.commit()
        session.close()


def test_duplicate_email_causes_transaction_failure_and_rollback():
    session = SessionLocal()

    test_email = "duplicate_transaction_test@tangle.test"

    try:
        first_user = User(
            name="Duplicate Test One",
            email=test_email,
            role="ANALYST",
        )

        session.add(first_user)
        session.commit()

        second_user = User(
            name="Duplicate Test Two",
            email=test_email,
            role="ANALYST",
        )

        session.add(second_user)

        with pytest.raises(SQLAlchemyError):
            session.commit()

        session.rollback()

        users = (
            session.query(User)
            .filter(User.email == test_email)
            .all()
        )

        assert len(users) == 1
        assert users[0].name == "Duplicate Test One"

    finally:
        session.rollback()

        session.query(User).filter(User.email == test_email).delete(
            synchronize_session=False
        )

        session.commit()
        session.close()


def test_rollback_after_flush_keeps_database_clean():
    session = SessionLocal()

    test_email = "flush_rollback_test@tangle.test"

    try:
        user = User(
            name="Flush Rollback Test",
            email=test_email,
            role="ANALYST",
        )

        session.add(user)
        session.flush()

        assert (
            session.query(User)
            .filter(User.email == test_email)
            .count()
            == 1
        )

        session.rollback()

        assert (
            session.query(User)
            .filter(User.email == test_email)
            .count()
            == 0
        )

    finally:
        session.rollback()
        session.close()