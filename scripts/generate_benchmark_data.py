
import psycopg

DB_CONFIG = {
    "dbname": "security_monitor_benchmark",
    "user": "mehmetkocak",
    "host": "localhost",
    "port": 5432,
}

TOTAL_LOGS = 10_000


INSERT_QUERY = """
INSERT INTO security_logs (
    timestamp,
    ip_address,
    username,
    event_type,
    status
)
SELECT
    TIMESTAMP '2026-11-23 10:00:00'
        - (n * INTERVAL '10 seconds'),
    '198.51.100.' || ((n %% 200) + 1),
    'benchmark_user_' || n,
    CASE
        WHEN n %% 4 = 0 THEN 'login_success'
        ELSE 'login_failed'
    END,
    CASE
        WHEN n %% 4 = 0 THEN 'success'
        ELSE 'failed'
    END
FROM generate_series(1, %s) AS n
WHERE NOT EXISTS (
    SELECT 1
    FROM security_logs
    WHERE username = 'benchmark_user_' || n
      AND ip_address = '198.51.100.' || ((n %% 200) + 1)
);
"""


def main():
    with psycopg.connect(**DB_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_QUERY, (TOTAL_LOGS,))
            inserted = cursor.rowcount

            cursor.execute("ANALYZE security_logs")

            cursor.execute(
                "SELECT COUNT(*) FROM security_logs"
            )
            total = cursor.fetchone()[0]

    print("Benchmark dataset generation")
    print("-" * 40)
    print(f"Inserted logs: {inserted}")
    print(f"Total logs: {total}")


if __name__ == "__main__":
    main()
