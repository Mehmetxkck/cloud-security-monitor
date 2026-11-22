
from fastapi import FastAPI
from app.database import (
    fetch_all_logs,
    save_security_alert,
    fetch_security_alerts
)
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
    logs = fetch_all_logs()

    return {
        "total_logs": len(logs),
        "logs": logs
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
    logs = fetch_all_logs()

    grouped_logs = group_failed_logins(logs)

    for ip, timestamps in grouped_logs.items():
        if detect_brute_force(timestamps):
            alert = {
                "ip_address": ip,
                "alert_type": "brute_force",
                "severity": "high",
                "message": "Multiple failed login attempts detected"
            }

            save_security_alert(alert)

    alerts = fetch_security_alerts()

    return {
        "total_alerts": len(alerts),
        "alerts": alerts
    }
