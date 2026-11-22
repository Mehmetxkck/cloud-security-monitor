
from app.database import get_connection
from app.log_parser import load_logs, validate_all_logs


def import_logs():
    logs = load_logs()

    valid_logs, invalid_logs = validate_all_logs(logs)

    print("Valid logs:", len(valid_logs))
    print("Invalid logs:", len(invalid_logs))

    inserted_count = 0

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for log in valid_logs:

                cursor.execute(
                    """
                    INSERT INTO security_logs
                    (timestamp, ip_address, username, event_type, status)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT ON CONSTRAINT unique_security_log
                    DO NOTHING
                    """,
                    (
                        log["timestamp"],
                        log["ip_address"],
                        log["username"],
                        log["event_type"],
                        log["status"]
                    )
                )

                if cursor.rowcount == 1:
                    inserted_count += 1

        connection.commit()

    print("Inserted logs:", inserted_count)


if __name__ == "__main__":
    import_logs()
