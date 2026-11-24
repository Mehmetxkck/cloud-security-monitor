
from fastapi.testclient import TestClient
from psycopg import OperationalError

from app.main import app


client = TestClient(app)


# 1. Health endpoint testi
def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


# 2. Logs endpoint testi
def test_logs_endpoint(monkeypatch):
    sample_logs = [
        {
            "id": 1,
            "timestamp": "2026-11-22T10:00:00",
            "ip_address": "203.0.113.25",
            "username": "admin",
            "event_type": "login_failed",
            "status": "failed"
        }
    ]

    monkeypatch.setattr(
        "app.main.fetch_all_logs",
        lambda **kwargs: sample_logs
    )

    response = client.get("/logs")

    assert response.status_code == 200

    data = response.json()

    assert data["total_returned"] == 1
    assert data["limit"] == 100
    assert data["offset"] == 0
    assert len(data["logs"]) == 1
    assert data["logs"][0]["ip_address"] == "203.0.113.25"


# 3. Boş log listesi testi
def test_empty_logs_endpoint(monkeypatch):
    monkeypatch.setattr(
        "app.main.fetch_all_logs",
        lambda **kwargs: []
    )

    response = client.get("/logs")

    assert response.status_code == 200
    assert response.json()["total_returned"] == 0
    assert response.json()["logs"] == []


# 4. Brute-force tespit testi
# POST /security/analyze endpoint'ini test eder
def test_security_alert_detected(monkeypatch):
    sample_logs = [
        {
            "id": i + 1,
            "timestamp": f"2026-11-22T10:00:{i:02d}",
            "ip_address": "203.0.113.25",
            "username": "admin",
            "event_type": "login_failed",
            "status": "failed"
        }
        for i in range(5)
    ]

    saved_alerts = []

    monkeypatch.setattr(
        "app.main.fetch_logs_for_detection",
        lambda: sample_logs
    )

    def fake_save_security_alert(alert):
        saved_alerts.append(alert)

    monkeypatch.setattr(
        "app.main.save_security_alert",
        fake_save_security_alert
    )

    response = client.post("/security/analyze")

    assert response.status_code == 200

    data = response.json()

    assert data["analyzed_logs"] == 5
    assert data["detected_ips"] == 1

    assert len(saved_alerts) == 1
    assert saved_alerts[0]["ip_address"] == "203.0.113.25"
    assert saved_alerts[0]["alert_type"] == "brute_force"
    assert saved_alerts[0]["severity"] == "high"


# 5. Brute-force oluşmaması testi
def test_no_security_alert(monkeypatch):
    sample_logs = [
        {
            "id": i + 1,
            "timestamp": f"2026-11-22T10:00:{i:02d}",
            "ip_address": "203.0.113.25",
            "username": "admin",
            "event_type": "login_failed",
            "status": "failed"
        }
        for i in range(3)
    ]

    saved_alerts = []

    monkeypatch.setattr(
        "app.main.fetch_logs_for_detection",
        lambda: sample_logs
    )

    monkeypatch.setattr(
        "app.main.save_security_alert",
        lambda alert: saved_alerts.append(alert)
    )

    response = client.post("/security/analyze")

    assert response.status_code == 200

    data = response.json()

    assert data["analyzed_logs"] == 3
    assert data["detected_ips"] == 0
    assert saved_alerts == []


# 6. Veritabanı bağlantı hatası testi
def test_logs_database_unavailable(monkeypatch):

    def fake_database_error(**kwargs):
        raise OperationalError(
            "Simulated database connection failure"
        )

    monkeypatch.setattr(
        "app.main.fetch_all_logs",
        fake_database_error
    )

    response = client.get("/logs")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Database service unavailable"
    )


# 7. Sayfalama testi
def test_logs_pagination(monkeypatch):

    def fake_fetch_all_logs(**kwargs):
        assert kwargs["limit"] == 5
        assert kwargs["offset"] == 10
        return []

    monkeypatch.setattr(
        "app.main.fetch_all_logs",
        fake_fetch_all_logs
    )

    response = client.get("/logs?limit=5&offset=10")

    assert response.status_code == 200

    data = response.json()

    assert data["limit"] == 5
    assert data["offset"] == 10
    assert data["total_returned"] == 0


# 8. Geçersiz limit testi
def test_invalid_limit():
    response = client.get("/logs?limit=-1")

    assert response.status_code == 422


# 9. GET /security/alerts analiz başlatmamalı
def test_get_alerts_does_not_trigger_detection(monkeypatch):
    sample_alert = {
        "id": 1,
        "ip_address": "203.0.113.25",
        "alert_type": "brute_force",
        "severity": "high",
        "message": "Multiple failed login attempts detected",
        "created_at": "2026-11-22T10:01:00"
    }

    def unexpected_detection():
        raise AssertionError(
            "GET endpoint must not trigger detection"
        )

    def unexpected_save(alert):
        raise AssertionError(
            "GET endpoint must not save alerts"
        )

    monkeypatch.setattr(
        "app.main.fetch_logs_for_detection",
        unexpected_detection
    )

    monkeypatch.setattr(
        "app.main.save_security_alert",
        unexpected_save
    )

    monkeypatch.setattr(
        "app.main.fetch_security_alerts",
        lambda: [sample_alert]
    )

    response = client.get("/security/alerts")

    assert response.status_code == 200

    data = response.json()

    assert data["total_alerts"] == 1
    assert len(data["alerts"]) == 1
    assert data["alerts"][0]["alert_type"] == "brute_force"


def test_analyze_more_than_100_logs(monkeypatch):
    sample_logs = [
        {
            "id": i + 1,
            "timestamp": f"2026-11-22T10:{i // 60:02d}:{i % 60:02d}",
            "ip_address": "203.0.113.25",
            "username": "admin",
            "event_type": "login_failed",
            "status": "failed"
        }
        for i in range(150)
    ]

    saved_alerts = []

    def fake_fetch_logs():
        return sample_logs

    monkeypatch.setattr(
        "app.main.fetch_logs_for_detection",
        fake_fetch_logs
    )

    monkeypatch.setattr(
        "app.main.save_security_alert",
        lambda alert: saved_alerts.append(alert)
    )

    response = client.post("/security/analyze")

    assert response.status_code == 200
    assert response.json()["analyzed_logs"] == 150
    assert response.json()["detected_ips"] == 1
    assert len(saved_alerts) == 1


def test_security_stats_endpoint(monkeypatch):
    sample_stats = {
        "total_logs": 20,
        "failed_logins": 12,
        "top_ips": [
            {
                "ip_address": "203.0.113.25",
                "failed_attempts": 8
            },
            {
                "ip_address": "198.51.100.10",
                "failed_attempts": 4
            }
        ]
    }

    monkeypatch.setattr(
        "app.main.fetch_security_stats",
        lambda hours=None: sample_stats
    )

    response = client.get("/security/stats")

    assert response.status_code == 200
    assert response.json() == sample_stats


def test_security_stats_hours_filter(monkeypatch):
    received_hours = []

    def fake_stats(hours=None):
        received_hours.append(hours)
        return {
            "total_logs": 5,
            "failed_logins": 3,
            "top_ips": []
        }

    monkeypatch.setattr(
        "app.main.fetch_security_stats",
        fake_stats
    )

    response = client.get("/security/stats?hours=24")

    assert response.status_code == 200
    assert received_hours == [24]
    assert response.json()["total_logs"] == 5


def test_security_stats_invalid_hours():
    response = client.get("/security/stats?hours=-5")
    assert response.status_code == 422

    response = client.get("/security/stats?hours=721")
    assert response.status_code == 422
