from database.connection import engine
from database.models import Base


def initialize_database():
    print("Creating TANGLE database tables...")

    Base.metadata.create_all(
        bind=engine
    )

    print("TANGLE database tables created successfully.")


if __name__ == "__main__":
    initialize_database()