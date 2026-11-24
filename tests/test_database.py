
import uuid
from datetime import datetime, timedelta, timezone

import pytest
import psycopg

from app import database
from app.config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    TEST_DB_NAME,
    BENCHMARK_DB_NAME,
)


# Merkezi ve güvenli test veritabanı bağlantısı
def _test_db_connection():
    if not TEST_DB_NAME or TEST_DB_NAME in {
        DB_NAME,
        BENCHMARK_DB_NAME,
    }:
        raise RuntimeError(
            "Test database must be isolated."
        )

    return psycopg.connect(
        dbname=TEST_DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


# 1. Gerçek PostgreSQL bağlantı testi
def test_fetch_logs_from_postgresql(monkeypatch):

    monkeypatch.setattr(
        database,
        "get_connection",
        _test_db_connection
    )

    with _test_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            current_db = cursor.fetchone()[0]

            assert current_db == TEST_DB_NAME

            # Önceki test kaydını temizle
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
        logs = database.fetch_all_logs(
            ip_address="198.51.100.42",
            limit=10,
            offset=0
        )

        assert len(logs) == 1
        assert logs[0]["ip_address"] == "198.51.100.42"
        assert logs[0]["username"] == "integration_test"
        assert logs[0]["status"] == "failed"

    finally:
        # Test verisini temizle
        with _test_db_connection() as connection:
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


# Ortak test verisi fixture
@pytest.fixture
def sample_database_logs(monkeypatch):

    monkeypatch.setattr(
        database,
        "get_connection",
        _test_db_connection
    )

    # Yanlış veritabanında işlem yapılmasını önle
    with _test_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database()")

            assert cursor.fetchone()[0] == TEST_DB_NAME

    # Her test için benzersiz kullanıcı adı
    username = f"test_{uuid.uuid4().hex[:12]}"
    inserted_ids = []

    try:
        with _test_db_connection() as connection:
            with connection.cursor() as cursor:

                for second, ip in enumerate([
                    "198.51.100.71",
                    "198.51.100.71",
                    "198.51.100.72"
                ]):
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

                    inserted_ids.append(
                        cursor.fetchone()[0]
                    )

            connection.commit()

        yield username, inserted_ids

    finally:
        # Sadece bu testin eklediği kayıtları temizle
        if inserted_ids:
            with _test_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM security_logs
                        WHERE id = ANY(%s)
                        """,
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


# 5. Detection fonksiyonunun 100'den fazla log okuma testi
def test_detection_fetches_more_than_100_logs(monkeypatch):

    test_ip = "198.51.100.99"
    test_username = f"bulk_{uuid.uuid4().hex[:12]}"
    inserted_ids = []

    monkeypatch.setattr(
        database,
        "get_connection",
        _test_db_connection
    )

    try:
        with _test_db_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute("SELECT current_database()")

                assert cursor.fetchone()[0] == TEST_DB_NAME

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

                    inserted_ids.append(
                        cursor.fetchone()[0]
                    )

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
            with _test_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM security_logs
                        WHERE id = ANY(%s)
                        """,
                        (inserted_ids,)
                    )


# 6. Güvenlik istatistikleri zaman filtreleme testi
def test_security_stats_time_filter(monkeypatch):

    test_ip = "198.51.100.88"
    test_username = f"time_{uuid.uuid4().hex[:12]}"
    inserted_ids = []

    monkeypatch.setattr(
        database,
        "get_connection",
        _test_db_connection
    )

    now = datetime.now(timezone.utc).replace(
        tzinfo=None
    )

    try:
        with _test_db_connection() as connection:
            with connection.cursor() as cursor:

                for timestamp in [
                    now - timedelta(hours=2),
                    now - timedelta(hours=48)
                ]:
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
                        RETURNING id
                        """,
                        (
                            timestamp,
                            test_ip,
                            test_username,
                            "login_failed",
                            "failed"
                        )
                    )

                    inserted_ids.append(
                        cursor.fetchone()[0]
                    )

        stats_24h = database.fetch_security_stats(
            hours=24
        )

        stats_72h = database.fetch_security_stats(
            hours=72
        )

        def attempts_for_ip(stats):
            return next(
                (
                    item["failed_attempts"]
                    for item in stats["top_ips"]
                    if item["ip_address"] == test_ip
                ),
                0
            )

        assert attempts_for_ip(stats_24h) == 1
        assert attempts_for_ip(stats_72h) == 2

    finally:
        if inserted_ids:
            with _test_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM security_logs
                        WHERE id = ANY(%s)
                        """,
                        (inserted_ids,)
                    )
