
from datetime import datetime, timedelta, timezone
import psycopg
from app.config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
)


# PostgreSQL bağlantısı
def get_connection():
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )

# PostgreSQL'den güvenlik loglarını getir


def fetch_all_logs(
    ip_address=None,
    limit=100,
    offset=0
):
    query = """
        SELECT
            id,
            timestamp,
            ip_address,
            username,
            event_type,
            status
        FROM security_logs
    """

    params = []

    # IP adresine göre filtreleme
    if ip_address:
        query += " WHERE ip_address = %s"
        params.append(ip_address)

    # Sayfalama
    query += " ORDER BY id ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

    logs = []

    for row in rows:
        log = {
            "id": row[0],
            "timestamp": row[1].isoformat(),
            "ip_address": row[2],
            "username": row[3],
            "event_type": row[4],
            "status": row[5]
        }

        logs.append(log)

    return logs


# Güvenlik uyarısını PostgreSQL'e kaydet
def save_security_alert(alert):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO security_alerts
                (
                    ip_address,
                    alert_type,
                    severity,
                    message
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (ip_address, alert_type)
                DO NOTHING
                """,
                (
                    alert["ip_address"],
                    alert["alert_type"],
                    alert["severity"],
                    alert["message"]
                )
            )

        connection.commit()


# PostgreSQL'den güvenlik uyarılarını getir
def fetch_security_alerts():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    ip_address,
                    alert_type,
                    severity,
                    message,
                    created_at
                FROM security_alerts
                ORDER BY id DESC
                """
            )

            rows = cursor.fetchall()

    alerts = []

    for row in rows:
        alert = {
            "id": row[0],
            "ip_address": row[1],
            "alert_type": row[2],
            "severity": row[3],
            "message": row[4],
            "created_at": row[5].isoformat()
        }

        alerts.append(alert)

    return alerts


def fetch_logs_for_detection():
    """
    Brute-force analizi için tüm başarısız
    giriş kayıtlarını getirir.
    """

    query = """
        SELECT
            id,
            timestamp,
            ip_address,
            username,
            event_type,
            status
        FROM security_logs
        WHERE event_type = %s
        ORDER BY timestamp ASC
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                ("login_failed",)
            )
            rows = cursor.fetchall()

    logs = []

    for row in rows:
        logs.append({
            "id": row[0],
            "timestamp": row[1].isoformat(),
            "ip_address": row[2],
            "username": row[3],
            "event_type": row[4],
            "status": row[5]
        })

    return logs


def fetch_security_stats(hours=None):
    start_time = None

    if hours is not None:
        start_time = (
            datetime.now(timezone.utc).replace(tzinfo=None)
            - timedelta(hours=hours)
        )

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM security_logs
                WHERE (%s::timestamp IS NULL
                       OR timestamp >= %s::timestamp)
                """,
                (start_time, start_time)
            )
            total_logs = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM security_logs
                WHERE event_type = %s
                  AND (%s::timestamp IS NULL
                       OR timestamp >= %s::timestamp)
                """,
                ("login_failed", start_time, start_time)
            )
            failed_logins = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT ip_address, COUNT(*) AS attempts
                FROM security_logs
                WHERE event_type = %s
                  AND (%s::timestamp IS NULL
                       OR timestamp >= %s::timestamp)
                GROUP BY ip_address
                ORDER BY attempts DESC, ip_address ASC
                LIMIT 5
                """,
                ("login_failed", start_time, start_time)
            )
            rows = cursor.fetchall()

    return {
        "total_logs": total_logs,
        "failed_logins": failed_logins,
        "top_ips": [
            {
                "ip_address": row[0],
                "failed_attempts": row[1]
            }
            for row in rows
        ]
    }


def fetch_failed_logins_by_ip():
    """
    PostgreSQL'deki başarısız girişleri
    IP adresine göre gruplandırır.
    """

    query = """
        SELECT ip_address, COUNT(*) AS failed_attempts
        FROM security_logs
        WHERE event_type = %s
        GROUP BY ip_address
        ORDER BY failed_attempts DESC, ip_address ASC
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                ("login_failed",)
            )

            rows = cursor.fetchall()

    return {
        row[0]: row[1]
        for row in rows
    }
