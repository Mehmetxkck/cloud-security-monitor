import json
from pathlib import Path


REQUIRED_FIELDS = [
    "timestamp",
    "ip_address",
    "username",
    "event_type",
    "status"
]


def load_logs():
    """JSON dosyasından log kayıtlarını okur."""

    project_root = Path(__file__).resolve().parent.parent
    file_path = project_root / "data" / "sample_logs.json"

    with open(file_path, "r", encoding="utf-8") as file:
        logs = json.load(file)

    return logs


def validate_log(log):
    """Log kaydında gerekli alanların bulunup bulunmadığını kontrol eder."""

    for field in REQUIRED_FIELDS:
        if field not in log:
            return False

    return True


def find_missing_fields(log):
    missing_fields = []

    for field in REQUIRED_FIELDS:
        if field not in log:
            missing_fields.append(field)

    return missing_fields


def validate_all_logs(logs):
    valid_logs = []
    invalid_logs = []

    for log in logs:
        if validate_log(log):
            valid_logs.append(log)
        else:
            invalid_logs.append(log)

    return valid_logs, invalid_logs


def count_failed_logins(logs):
    """Başarısız giriş denemelerini IP adreslerine göre sayar."""

    failed_attempts = {}

    for log in logs:
        if log["event_type"] == "login_failed":
            ip = log["ip_address"]

            if ip in failed_attempts:
                failed_attempts[ip] += 1
            else:
                failed_attempts[ip] = 1

    return failed_attempts


valid_log = {
    "timestamp": "2026-11-21T10:00:00",
    "ip_address": "203.0.113.25",
    "username": "admin",
    "event_type": "login_failed",
    "status": "failed"
}

invalid_log = {
    "username": "admin",
    "status": "failed"
}

test_logs = [valid_log, invalid_log, valid_log]

valid_results, invalid_results = validate_all_logs(test_logs)


if __name__ == "__main__":
    with open("data/sample_logs.json", "r") as file:
        logs = json.load(file)

    valid_results, invalid_results = validate_all_logs(logs)

    print("Total logs:", len(logs))
    print("Valid logs:", len(valid_results))
    print("Invalid logs:", len(invalid_results))
