
import pytest
from pydantic import ValidationError

from app.schemas.log_schema import SecurityLog


def test_valid_security_log():
    log = {
        "timestamp": "2026-11-22T10:00:00",
        "ip_address": "203.0.113.25",
        "username": "admin",
        "event_type": "login_failed",
        "status": "failed"
    }

    result = SecurityLog.model_validate(log)

    assert result.username == "admin"


def test_invalid_ip_address():
    log = {
        "timestamp": "2026-11-22T10:00:00",
        "ip_address": "invalid-ip",
        "username": "admin",
        "event_type": "login_failed",
        "status": "failed"
    }

    with pytest.raises(ValidationError):
        SecurityLog.model_validate(log)


def test_invalid_timestamp():
    log = {
        "timestamp": "invalid-date",
        "ip_address": "203.0.113.25",
        "username": "admin",
        "event_type": "login_failed",
        "status": "failed"
    }

    with pytest.raises(ValidationError):
        SecurityLog.model_validate(log)
