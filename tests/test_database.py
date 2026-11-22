
import pytest
import uuid
import psycopg

from app import database


TEST_DB_NAME = "security_monitor_test"


def test_fetch_logs_from_postgresql(monkeypatch):

    # Test veritabanına bağlantı
    def test_connection():
        return psycopg.connect(
            dbname=TEST_DB_NAME,
            user="mehmetkocak",
            host="localhost",
            port=5432
        )

    # Gerçek veritabanı yerine test DB kullan
    monkeypatch.setattr(
        database,
        "get_connection",
        test_connection
    )

    # Test DB bağlantısını doğrula
    with test_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database()"
            )
            current_db = cursor.fetchone()[0]

            assert current_db == TEST_DB_NAME

            # Yalnızca test veritabanındaki
            # belirli test kaydını temizle
            cursor.execute(
                """
                DELETE FROM security_logs
                WHERE ip_address = %s
                  AND username = %s
                """,
                ("198.51.100.42", "integration_test")
            )

            # Örnek güvenlik logu ekle
            cursor.execute(
                """
                INSERT INTO security_logs
                (
                    timestamp,
                    ip_address,
                    username,
                    event_type,
                    status
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    "2026-11-22 10:00:00",
                    "198.51.100.42",
                    "integration_test",
                    "login_failed",
                    "failed"
                )
            )

        connection.commit()

    try:
        # Gerçek PostgreSQL sorgusunu çalıştır
        logs = database.fetch_all_logs(
            ip_address="198.51.100.42",
            limit=10,
            offset=0
        )

        # Sonuçları doğrula
        assert len(logs) == 1
        assert logs[0]["ip_address"] == "198.51.100.42"
        assert logs[0]["username"] == "integration_test"
        assert logs[0]["status"] == "failed"

    finally:
        # Test verisini temizle
        with test_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM security_logs
                    WHERE ip_address = %s
                      AND username = %s
                    """,
                    ("198.51.100.42", "integration_test")
                )

            connection.commit()


@pytest.fixture
def sample_database_logs(monkeypatch):
    # Test veritabanı bağlantısı
    def test_connection():
        return psycopg.connect(
            dbname="security_monitor_test",
            user="mehmetkocak",
            host="localhost",
            port=5432
        )

    monkeypatch.setattr(
        database,
        "get_connection",
        test_connection
    )

    # Yanlış veritabanında işlem yapılmasını önle
    with test_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            assert cursor.fetchone()[0] == "security_monitor_test"

    # Her test için benzersiz kullanıcı adı
    username = f"test_{uuid.uuid4().hex[:12]}"
    inserted_ids = []

    try:
        with test_connection() as connection:
            with connection.cursor() as cursor:
                for second, ip in enumerate([
                    "198.51.100.71",
                    "198.51.100.71",
                    "198.51.100.72"
                ]):
                    cursor.execute(
                        """
                        INSERT INTO security_logs
                        (timestamp, ip_address, username,
                         event_type, status)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            f"2026-11-22 12:00:{second:02d}",
                            ip,
                            username,
                            "login_failed",
                            "failed"
                        )
                    )
                    inserted_ids.append(cursor.fetchone()[0])

            connection.commit()

        yield username, inserted_ids

    finally:
        # Sadece bu testin eklediği kayıtları temizle
        if inserted_ids:
            with test_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM security_logs WHERE id = ANY(%s)",
                        (inserted_ids,)
                    )
                connection.commit()


# 2. Gerçek IP filtreleme testi
def test_postgresql_ip_filter(sample_database_logs):
    username, ids = sample_database_logs

    logs = database.fetch_all_logs(
        ip_address="198.51.100.71",
        limit=1000,
        offset=0
    )

    matching = [
        log for log in logs
        if log["username"] == username
    ]

    assert len(matching) == 2
    assert all(
        log["ip_address"] == "198.51.100.71"
        for log in matching
    )


# 3. Gerçek LIMIT testi
def test_postgresql_limit(sample_database_logs):
    username, ids = sample_database_logs

    logs = database.fetch_all_logs(
        limit=2,
        offset=0
    )

    assert len(logs) == 2


# 4. Gerçek OFFSET testi
def test_postgresql_offset(sample_database_logs):
    username, ids = sample_database_logs

    first_page = database.fetch_all_logs(
        limit=1,
        offset=0
    )

    second_page = database.fetch_all_logs(
        limit=1,
        offset=1
    )

    assert len(first_page) == 1
    assert len(second_page) == 1
    assert first_page[0]["id"] != second_page[0]["id"]


def test_detection_fetches_more_than_100_logs(monkeypatch):
    import uuid

    test_db = "security_monitor_test"
    test_ip = "198.51.100.99"
    test_username = f"bulk_{uuid.uuid4().hex[:12]}"
    inserted_ids = []

    def test_connection():
        return psycopg.connect(
            dbname=test_db,
            user="mehmetkocak",
            host="localhost",
            port=5432
        )

    monkeypatch.setattr(
        database,
        "get_connection",
        test_connection
    )

    try:
        with test_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database()")
                assert cursor.fetchone()[0] == test_db

                for i in range(105):
                    cursor.execute(
                        """
                        INSERT INTO security_logs
                        (
                            timestamp,
                            ip_address,
                            username,
                            event_type,
                            status
                        )
                        VALUES (
                            TIMESTAMP '2026-11-22 10:00:00'
                            + (%s * INTERVAL '1 second'),
                            %s, %s, %s, %s
                        )
                        RETURNING id
                        """,
                        (
                            i,
                            test_ip,
                            test_username,
                            "login_failed",
                            "failed"
                        )
                    )

                    inserted_ids.append(cursor.fetchone()[0])

        # Gerçek PostgreSQL sorgusu
        logs = database.fetch_logs_for_detection()

        # Yalnızca bu testin eklediği logları say
        matching_logs = [
            log for log in logs
            if log["username"] == test_username
        ]

        assert len(matching_logs) == 105

    finally:
        # Test kayıtlarını temizle
        if inserted_ids:
            with test_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM security_logs
                        WHERE id = ANY(%s)
                        """,
                        (inserted_ids,)
                    )
