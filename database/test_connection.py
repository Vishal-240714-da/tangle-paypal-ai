from sqlalchemy import text

from database.connection import engine


try:
    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        version = result.fetchone()[0]

        print("PostgreSQL connection successful!")
        print(version)

except Exception as error:

    print("PostgreSQL connection failed.")
    print(error)