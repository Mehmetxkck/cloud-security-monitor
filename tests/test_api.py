
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


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
        lambda: sample_logs
    )

    response = client.get("/logs")

    assert response.status_code == 200
    assert response.json()["total_logs"] == 1
    assert response.json()["logs"] == sample_logs


def test_empty_logs_endpoint(monkeypatch):
    monkeypatch.setattr(
        "app.main.fetch_all_logs",
        lambda: []
    )

    response = client.get("/logs")

    assert response.status_code == 200
    assert response.json()["total_logs"] == 0
    assert response.json()["logs"] == []


def test_security_alert_detected(monkeypatch):
    logs = []

    for second in [0, 10, 20, 30, 40]:
        logs.append({
            "id": second + 1,
            "timestamp": f"2026-11-22T10:00:{second:02d}",
            "ip_address": "203.0.113.25",
            "username": "admin",
            "event_type": "login_failed",
            "status": "failed"
        })

    saved_alerts = []

    def fake_save_alert(alert):
        saved_alerts.append(alert)

    def fake_fetch_alerts():
        return saved_alerts

    monkeypatch.setattr("app.main.fetch_all_logs", lambda: logs)
    monkeypatch.setattr("app.main.save_security_alert", fake_save_alert)
    monkeypatch.setattr("app.main.fetch_security_alerts", fake_fetch_alerts)

    response = client.get("/security/alerts")

    assert response.status_code == 200
    assert response.json()["total_alerts"] == 1
    assert response.json()["alerts"][0]["ip_address"] == "203.0.113.25"


def test_no_security_alert(monkeypatch):
    logs = [
        {
            "id": 1,
            "timestamp": "2026-11-22T10:00:00",
            "ip_address": "192.0.2.50",
            "username": "test",
            "event_type": "login_failed",
            "status": "failed"
        }
    ]

    saved_alerts = []

    monkeypatch.setattr("app.main.fetch_all_logs", lambda: logs)
    monkeypatch.setattr(
        "app.main.save_security_alert",
        lambda alert: saved_alerts.append(alert)
    )
    monkeypatch.setattr(
        "app.main.fetch_security_alerts",
        lambda: saved_alerts
    )

    response = client.get("/security/alerts")

    assert response.status_code == 200
    assert response.json()["total_alerts"] == 0
    assert saved_alerts == []
