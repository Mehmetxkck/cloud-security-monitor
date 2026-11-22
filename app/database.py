
import psycopg


def get_connection():
    connection = psycopg.connect(
        dbname="security_monitor",
        user="mehmetkocak",
        host="localhost",
        port=5432
    )

    return connection


def fetch_all_logs():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, timestamp, ip_address,
                       username, event_type, status
                FROM security_logs
                ORDER BY id ASC
                """
            )

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


def save_security_alert(alert):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO security_alerts
                (ip_address, alert_type, severity, message)
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


def fetch_security_alerts():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, ip_address, alert_type,
                       severity, message, created_at
                FROM security_alerts
                ORDER BY id DESC
                """
            )

            rows = cursor.fetchall()

    alerts = []

    for row in rows:
        alerts.append({
            "id": row[0],
            "ip_address": row[1],
            "alert_type": row[2],
            "severity": row[3],
            "message": row[4],
            "created_at": row[5].isoformat()
        })

    return alerts
