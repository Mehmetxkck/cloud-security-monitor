
import time
import statistics
import psycopg
from app.config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    BENCHMARK_DB_NAME,
)

DB_CONFIG = {
    "dbname": BENCHMARK_DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT,
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


def execute_query(cursor, use_index):
    if use_index:
        cursor.execute("SET enable_seqscan = off")
    else:
        cursor.execute("SET enable_seqscan = on")

    start = time.perf_counter()

    cursor.execute(QUERY)
    cursor.fetchall()

    return (time.perf_counter() - start) * 1000


def get_query_plan(cursor, use_index):
    if use_index:
        cursor.execute("SET enable_seqscan = off")
    else:
        cursor.execute("SET enable_seqscan = on")

    cursor.execute("EXPLAIN " + QUERY)
    return "\n".join(row[0] for row in cursor.fetchall())


def benchmark(connection, runs=100, warmup=20):
    normal_times = []
    indexed_times = []

    with connection.cursor() as cursor:
        # Warm up both configurations
        for _ in range(warmup):
            execute_query(cursor, False)
            execute_query(cursor, True)

        # Alternate measurement order
        for i in range(runs):
            if i % 2 == 0:
                normal_times.append(execute_query(cursor, False))
                indexed_times.append(execute_query(cursor, True))
            else:
                indexed_times.append(execute_query(cursor, True))
                normal_times.append(execute_query(cursor, False))

        normal_plan = get_query_plan(cursor, False)
        indexed_plan = get_query_plan(cursor, True)

    return normal_times, indexed_times, normal_plan, indexed_plan


def summarize(times):
    return {
        "mean_ms": round(statistics.mean(times), 6),
        "median_ms": round(statistics.median(times), 6),
        "min_ms": round(min(times), 6),
        "max_ms": round(max(times), 6)
    }


def main():
    with psycopg.connect(**DB_CONFIG) as connection:
        normal, indexed, normal_plan, indexed_plan = benchmark(connection)

    print("\nPostgreSQL Query Benchmark")
    print("-" * 45)

    print("\nNormal planner:")
    print(summarize(normal))

    print("\nSeq Scan disabled:")
    print(summarize(indexed))

    print("\nNormal query plan:")
    print(normal_plan)

    print("\nAlternative query plan:")
    print(indexed_plan)


if __name__ == "__main__":
    main()
