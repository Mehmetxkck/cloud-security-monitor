
from pydantic import ValidationError
from app.schemas.log_schema import SecurityLog


valid_log = {
    "timestamp": "2026-11-22T10:00:00",
    "ip_address": "203.0.113.25",
    "username": "admin",
    "event_type": "login_failed",
    "status": "failed"
}

invalid_log = {
    "timestamp": "yanlis-tarih",
    "ip_address": "merhaba",
    "username": "",
    "event_type": "unknown",
    "status": "error"
}


print("=== VALID LOG ===")

log = SecurityLog.model_validate(valid_log)
print(log.model_dump(mode="json"))


print("\n=== INVALID LOG ===")

try:
    SecurityLog.model_validate(invalid_log)

except ValidationError as error:
    print(error)
