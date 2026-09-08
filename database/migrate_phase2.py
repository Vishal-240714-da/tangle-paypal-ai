from sqlalchemy import inspect, text

from database.connection import engine


def column_exists(connection, table_name, column_name):
    inspector = inspect(connection)
    columns = inspector.get_columns(table_name)

    return any(
        column["name"] == column_name
        for column in columns
    )


def add_column_if_missing(
    connection,
    table_name,
    column_name,
    definition,
):
    if not column_exists(
        connection,
        table_name,
        column_name,
    ):
        print(
            f"Adding {table_name}.{column_name}..."
        )

        connection.execute(
            text(
                f"ALTER TABLE {table_name} "
                f"ADD COLUMN {column_name} {definition}"
            )
        )
    else:
        print(
            f"Already exists: "
            f"{table_name}.{column_name}"
        )


def migrate():

    print("=" * 60)
    print("TANGLE PHASE 2 DATABASE MIGRATION")
    print("=" * 60)

    with engine.begin() as connection:

        # ====================================================
        # USERS
        # ====================================================

        print("\nCreating users table...")

        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(150) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    role VARCHAR(50) NOT NULL
                        DEFAULT 'ANALYST',
                    created_at TIMESTAMP NOT NULL
                        DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )

        # ====================================================
        # INVOICES
        # ====================================================

        print("\nUpdating invoices table...")

        add_column_if_missing(
            connection,
            "invoices",
            "created_at",
            "TIMESTAMP",
        )

        # ====================================================
        # PAYMENTS
        # ====================================================

        print("\nUpdating payments table...")

        add_column_if_missing(
            connection,
            "payments",
            "created_at",
            "TIMESTAMP",
        )

        # ====================================================
        # CASES
        # ====================================================

        print("\nUpdating cases table...")

        add_column_if_missing(
            connection,
            "cases",
            "status",
            "VARCHAR(50)",
        )

        add_column_if_missing(
            connection,
            "cases",
            "risk_level",
            "VARCHAR(50)",
        )

        add_column_if_missing(
            connection,
            "cases",
            "priority_score",
            "DOUBLE PRECISION",
        )

        add_column_if_missing(
            connection,
            "cases",
            "human_review_required",
            "BOOLEAN",
        )

        add_column_if_missing(
            connection,
            "cases",
            "created_at",
            "TIMESTAMP",
        )

        add_column_if_missing(
            connection,
            "cases",
            "updated_at",
            "TIMESTAMP",
        )

        # ====================================================
        # INVESTIGATIONS
        # ====================================================

        print("\nUpdating investigations table...")

        add_column_if_missing(
            connection,
            "investigations",
            "finding",
            "TEXT",
        )

        add_column_if_missing(
            connection,
            "investigations",
            "recommendation",
            "TEXT",
        )

        add_column_if_missing(
            connection,
            "investigations",
            "confidence",
            "DOUBLE PRECISION",
        )

        add_column_if_missing(
            connection,
            "investigations",
            "evidence",
            "TEXT",
        )

        add_column_if_missing(
            connection,
            "investigations",
            "created_at",
            "TIMESTAMP",
        )

        # ====================================================
        # RISK ASSESSMENTS
        # ====================================================

        print("\nUpdating risk_assessments table...")

        add_column_if_missing(
            connection,
            "risk_assessments",
            "risk_score",
            "DOUBLE PRECISION",
        )

        add_column_if_missing(
            connection,
            "risk_assessments",
            "created_at",
            "TIMESTAMP",
        )

        # ====================================================
        # REVIEWS
        # ====================================================

        print("\nUpdating reviews table...")

        add_column_if_missing(
            connection,
            "reviews",
            "reviewer",
            "VARCHAR(255)",
        )

        add_column_if_missing(
            connection,
            "reviews",
            "decision",
            "VARCHAR(100)",
        )

        add_column_if_missing(
            connection,
            "reviews",
            "comment",
            "TEXT",
        )

        add_column_if_missing(
            connection,
            "reviews",
            "created_at",
            "TIMESTAMP",
        )

        # ====================================================
        # BANK TRANSACTIONS
        # ====================================================

        print("\nUpdating bank_transactions table...")

        add_column_if_missing(
            connection,
            "bank_transactions",
            "payment_id",
            "VARCHAR(100)",
        )

        add_column_if_missing(
            connection,
            "bank_transactions",
            "created_at",
            "TIMESTAMP",
        )

        # ====================================================
        # CASE HISTORY
        # ====================================================

        print("\nCreating case_history table...")

        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS case_history (
                    id SERIAL PRIMARY KEY,

                    case_id VARCHAR(100) NOT NULL,

                    previous_status VARCHAR(50),

                    new_status VARCHAR(50) NOT NULL,

                    changed_by VARCHAR(255),

                    reason TEXT,

                    timestamp TIMESTAMP NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT fk_case_history_case
                        FOREIGN KEY (case_id)
                        REFERENCES cases(case_id)
                        ON DELETE CASCADE
                )
                """
            )
        )

        # ====================================================
        # BACKFILL INVOICE TIMESTAMPS
        # ====================================================

        print("\nBackfilling invoice timestamps...")

        connection.execute(
            text(
                """
                UPDATE invoices
                SET created_at = CURRENT_TIMESTAMP
                WHERE created_at IS NULL
                """
            )
        )

        # ====================================================
        # BACKFILL PAYMENT TIMESTAMPS
        # ====================================================

        print("\nBackfilling payment timestamps...")

        connection.execute(
            text(
                """
                UPDATE payments
                SET created_at = CURRENT_TIMESTAMP
                WHERE created_at IS NULL
                """
            )
        )

        # ====================================================
        # BACKFILL CASE LIFECYCLE
        # ====================================================

        print("\nBackfilling case lifecycle fields...")

        connection.execute(
            text(
                """
                UPDATE cases
                SET status = 'PENDING_REVIEW'
                WHERE status IS NULL
                """
            )
        )

        # ====================================================
        # COPY RISK INFORMATION TO CASES
        # ====================================================

        print("\nBackfilling case risk information...")

        connection.execute(
            text(
                """
                UPDATE cases c
                SET
                    risk_level = r.risk_level,
                    priority_score = r.priority_score,
                    human_review_required =
                        r.human_review_required
                FROM risk_assessments r
                WHERE c.case_id = r.case_id
                  AND c.risk_level IS NULL
                """
            )
        )

        # ====================================================
        # BACKFILL CASE TIMESTAMPS
        # ====================================================

        print("\nBackfilling case timestamps...")

        connection.execute(
            text(
                """
                UPDATE cases
                SET
                    created_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE created_at IS NULL
                   OR updated_at IS NULL
                """
            )
        )

        # ====================================================
        # BACKFILL INVESTIGATION TIMESTAMPS
        # ====================================================

        print("\nBackfilling investigation timestamps...")

        connection.execute(
            text(
                """
                UPDATE investigations
                SET created_at = CURRENT_TIMESTAMP
                WHERE created_at IS NULL
                """
            )
        )

        # ====================================================
        # BACKFILL RISK TIMESTAMPS
        # ====================================================

        print("\nBackfilling risk assessment timestamps...")

        connection.execute(
            text(
                """
                UPDATE risk_assessments
                SET created_at = CURRENT_TIMESTAMP
                WHERE created_at IS NULL
                """
            )
        )

        # ====================================================
        # BACKFILL REVIEW TIMESTAMPS
        # ====================================================

        print("\nBackfilling review timestamps...")

        connection.execute(
            text(
                """
                UPDATE reviews
                SET created_at =
                    COALESCE(
                        reviewed_at,
                        CURRENT_TIMESTAMP
                    )
                WHERE created_at IS NULL
                """
            )
        )

        # ====================================================
        # BACKFILL BANK TRANSACTION TIMESTAMPS
        # ====================================================

        print("\nBackfilling bank transaction timestamps...")

        connection.execute(
            text(
                """
                UPDATE bank_transactions
                SET created_at = CURRENT_TIMESTAMP
                WHERE created_at IS NULL
                """
            )
        )

        # ====================================================
        # CASE HISTORY INITIAL SNAPSHOT
        # ====================================================

        print("\nCreating initial case history records...")

        connection.execute(
            text(
                """
                INSERT INTO case_history (
                    case_id,
                    previous_status,
                    new_status,
                    changed_by,
                    reason
                )
                SELECT
                    c.case_id,
                    NULL,
                    c.status,
                    'SYSTEM',
                    'Phase 2 migration - initial lifecycle snapshot'
                FROM cases c
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM case_history h
                    WHERE h.case_id = c.case_id
                )
                """
            )
        )

    print("\n" + "=" * 60)
    print("PHASE 2 DATABASE MIGRATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    migrate()