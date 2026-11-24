
import statistics
import time
from app.config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    BENCHMARK_DB_NAME,
)
import psycopg

DB_CONFIG = {
    "dbname": "security_monitor_benchmark",
    "user": "mehmetkocak",
    "host": "localhost",
    "port": 5432,
}

QUERY = """
SELECT ip_address, COUNT(*) AS attempts
FROM security_logs
WHERE event_type = 'login_failed'
  AND timestamp >= TIMESTAMP '2026-11-23 09:00:00'
GROUP BY ip_address
ORDER BY attempts DESC
LIMIT 5;
"""


def run_query(cursor, use_index):
    cursor.execute(
        "SET enable_indexscan = "
        + ("on" if use_index else "off")
    )
    cursor.execute(
        "SET enable_bitmapscan = "
        + ("on" if use_index else "off")
    )
    cursor.execute(
        "SET enable_indexonlyscan = "
        + ("on" if use_index else "off")
    )

    start = time.perf_counter()
    cursor.execute(QUERY)
    cursor.fetchall()

    return (time.perf_counter() - start) * 1000


def benchmark(cursor, runs=100, warmup=20):
    results = {"index": [], "seq_scan": []}

    for _ in range(warmup):
        run_query(cursor, True)
        run_query(cursor, False)

    for i in range(runs):
        order = [True, False] if i % 2 == 0 else [False, True]

        for use_index in order:
            elapsed = run_query(cursor, use_index)
            key = "index" if use_index else "seq_scan"
            results[key].append(elapsed)

    return results


def summarize(values):
    return {
        "mean_ms": round(statistics.mean(values), 4),
        "median_ms": round(statistics.median(values), 4),
        "min_ms": round(min(values), 4),
        "max_ms": round(max(values), 4),
    }


def main():
    with psycopg.connect(**DB_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM security_logs")
            count = cursor.fetchone()[0]

            if count < 10000:
                raise RuntimeError(
                    "Benchmark için en az 10000 kayıt gerekiyor."
                )

            results = benchmark(cursor)

    print(f"Dataset size: {count}")
    print("Index enabled:", summarize(results["index"]))
    print("Index disabled:", summarize(results["seq_scan"]))


if __name__ == "__main__":
    main()
