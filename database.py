import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "database.db"


def _create_quarantined_transactions(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quarantined_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            raw_data TEXT,
            rejection_reason TEXT NOT NULL,
            rejected_at TEXT NOT NULL
        )
    """)


def _migrate_quarantine_table(conn):
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }

    if "quarantined_transactions" in tables:
        return

    _create_quarantined_transactions(conn)

    if "quarantine_transactions" not in tables:
        return

    columns = {
        row[1]
        for row in conn.execute(
            "PRAGMA table_info(quarantine_transactions)"
        )
    }
    if {"rejected_at", "rejection_at"} <= columns:
        timestamp_column = "COALESCE(rejected_at, rejection_at)"
    elif "rejected_at" in columns:
        timestamp_column = "rejected_at"
    elif "rejection_at" in columns:
        timestamp_column = "rejection_at"
    else:
        raise sqlite3.DatabaseError(
            "Legacy quarantine_transactions table has no rejection timestamp"
        )

    conn.execute(f"""
        INSERT INTO quarantined_transactions
            (id, transaction_id, raw_data, rejection_reason, rejected_at)
        SELECT id, transaction_id, raw_data, rejection_reason, {timestamp_column}
        FROM quarantine_transactions
    """)
    conn.execute("DROP TABLE quarantine_transactions")


def create_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                customer_id TEXT,
                amount REAL,
                merchant TEXT,
                city TEXT,
                device TEXT,
                timestamp TEXT
            )
        """)
        _migrate_quarantine_table(conn)

        feature_columns = conn.execute(
            "PRAGMA table_info(transaction_features)"
        ).fetchall()
        expected_columns = {
            "transaction_id",
            "customer_id",
            "amount",
            "txn_count_5m",
            "amount_sum_1h",
            "avg_prior_amount",
            "amount_ratio",
            "city_changed",
            "feature_timestamp",
        }
        existing_columns = {row[1] for row in feature_columns}

        if feature_columns and existing_columns != expected_columns:
            conn.execute("DROP TABLE transaction_features")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS transaction_features (
                transaction_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                amount REAL NOT NULL,
                txn_count_5m INTEGER NOT NULL,
                amount_sum_1h REAL NOT NULL,
                avg_prior_amount REAL,
                amount_ratio REAL,
                city_changed INTEGER NOT NULL,
                feature_timestamp TEXT NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS fraud_predictions (
                transaction_id TEXT PRIMARY KEY,
                fraud_score REAL NOT NULL,
                is_suspicious INTEGER NOT NULL,
                model_version TEXT NOT NULL,
                predicted_at TEXT NOT NULL,
                FOREIGN KEY (transaction_id)
                    REFERENCES transactions(transaction_id)
            )
        """)


    print("Database and quarantine tables are ready at:", DB_PATH)


if __name__ == "__main__":
    create_database()