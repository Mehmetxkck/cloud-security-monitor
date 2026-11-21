
from fastapi import FastAPI
from app.log_parser import (
    load_logs,
    validate_all_logs,
    count_failed_logins
)
from app.services.detection_engine import (
    group_failed_logins,
    detect_brute_force
)

app = FastAPI(
    title="Cloud Security Monitoring Platform",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "message": "Cloud Security Monitoring API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/logs")
def get_logs():
    logs = load_logs()

    valid_logs, invalid_logs = validate_all_logs(logs)

    return {
        "total_logs": len(logs),
        "valid_logs": len(valid_logs),
        "invalid_logs": len(invalid_logs),
        "logs": valid_logs
    }


@app.get("/logs/failed")
def get_failed_logins():
    logs = load_logs()

    valid_logs, invalid_logs = validate_all_logs(logs)

    failed_attempts = count_failed_logins(valid_logs)

    return {
        "failed_login_count": sum(failed_attempts.values()),
        "failed_attempts_by_ip": failed_attempts
    }


@app.get("/security/alerts")
def get_security_alerts():
    logs = load_logs()

    valid_logs, invalid_logs = validate_all_logs(logs)

    grouped_logs = group_failed_logins(valid_logs)

    alerts = []

    for ip, timestamps in grouped_logs.items():
        if detect_brute_force(timestamps):
            alert = {
                "ip_address": ip,
                "alert_type": "brute_force",
                "severity": "high",
                "message": "Multiple failed login attempts detected"
            }

            alerts.append(alert)

    return {
        "total_alerts": len(alerts),
        "alerts": alerts
    }
