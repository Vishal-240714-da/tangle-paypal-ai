from database.connection import engine
from sqlalchemy import text


with engine.connect() as connection:

    print("=" * 60)
    print("CASES TABLE COLUMNS")
    print("=" * 60)

    result = connection.execute(
        text(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'cases'
            ORDER BY ordinal_position
            """
        )
    )

    for row in result:
        print(row)

    print()
    print("=" * 60)
    print("CASE SAMPLE")
    print("=" * 60)

    result = connection.execute(
        text(
            """
            SELECT
                case_id,
                status,
                risk_level,
                priority_score,
                human_review_required
            FROM cases
            LIMIT 3
            """
        )
    )

    for row in result:
        print(row)