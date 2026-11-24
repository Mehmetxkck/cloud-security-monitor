
import logging

from fastapi import FastAPI, HTTPException, Query
from psycopg import OperationalError

from app.database import (
    fetch_all_logs,
    save_security_alert,
    fetch_security_alerts,
    fetch_logs_for_detection,
    fetch_security_stats,
    fetch_failed_logins_by_ip
)

from app.services.detection_engine import (
    group_failed_logins,
    detect_brute_force
)


# Logging
logger = logging.getLogger(__name__)


# FastAPI uygulaması
app = FastAPI(
    title="Cloud Security Monitoring Platform",
    description="Security log monitoring and brute-force detection API",
    version="0.2.0"
)


# Ana endpoint
@app.get("/")
def root():
    return {
        "message": "Cloud Security Monitoring Platform API"
    }


# Sağlık kontrolü
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# PostgreSQL'den logları getir
# IP filtreleme ve sayfalama desteklenir
@app.get("/logs")
def get_logs(
    ip_address: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    try:
        logs = fetch_all_logs(
            ip_address=ip_address,
            limit=limit,
            offset=offset
        )

        return {
            "total_returned": len(logs),
            "limit": limit,
            "offset": offset,
            "logs": logs
        }

    except OperationalError:
        logger.exception("Database connection failed")

        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )


# PostgreSQL'den başarısız giriş istatistiklerini getir
@app.get("/logs/failed")
def get_failed_logs():
    try:
        failed_logins = fetch_failed_logins_by_ip()

        return {
            "failed_logins_by_ip": failed_logins
        }

    except OperationalError:
        logger.exception("Database connection failed")

        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )


@app.post("/security/analyze")
def analyze_security_logs():
    try:
        logs = fetch_logs_for_detection()
        grouped_logs = group_failed_logins(logs)

        detected_count = 0

        for ip, timestamps in grouped_logs.items():
            if detect_brute_force(timestamps):
                alert = {
                    "ip_address": ip,
                    "alert_type": "brute_force",
                    "severity": "high",
                    "message": "Multiple failed login attempts detected"
                }

                save_security_alert(alert)
                detected_count += 1

        return {
            "analyzed_logs": len(logs),
            "detected_ips": detected_count
        }

    except OperationalError:
        logger.exception("Database connection failed")
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )


@app.get("/security/alerts")
def get_security_alerts():
    try:
        alerts = fetch_security_alerts()

        return {
            "total_alerts": len(alerts),
            "alerts": alerts
        }

    except OperationalError:
        logger.exception("Database connection failed")
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )


@app.get("/security/stats")
def get_security_stats(
    hours: int | None = Query(
        default=None,
        ge=1,
        le=720
    )
):
    try:
        return fetch_security_stats(hours=hours)

    except OperationalError:
        logger.exception("Database connection failed")

        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )
