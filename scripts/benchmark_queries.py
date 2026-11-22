
import time
import statistics
import psycopg

DB_CONFIG = {
    "dbname": "security_monitor",
    "user": "mehmetkocak",
    "host": "localhost",
    "port": 5432
}

QUERY = """
SELECT ip_address, COUNT(*) AS attempts
FROM security_logs
WHERE event_type = 'login_failed'
  AND timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY ip_address
ORDER BY attempts DESC
LIMIT 5;
"""


def benchmark_query(connection, use_index, runs=100):
    times = []

    with connection.cursor() as cursor:
        if use_index:
            cursor.execute("SET enable_seqscan = off")
        else:
            cursor.execute("SET enable_seqscan = on")

        for _ in range(runs):
            start = time.perf_counter()

            cursor.execute(QUERY)
            cursor.fetchall()

            elapsed = (
                time.perf_counter() - start
            ) * 1000

            times.append(elapsed)

    return {
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "min_ms": min(times),
        "max_ms": max(times)
    }


def main():
    with psycopg.connect(**DB_CONFIG) as connection:
        normal = benchmark_query(
            connection,
            use_index=False
        )

        indexed = benchmark_query(
            connection,
            use_index=True
        )

    print("\nPostgreSQL Query Benchmark")
    print("-" * 40)

    print("Normal planner:", normal)
    print("Seq Scan disabled:", indexed)


if __name__ == "__main__":
    main()
