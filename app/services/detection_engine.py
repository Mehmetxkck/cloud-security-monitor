
from datetime import datetime


def group_failed_logins(logs):
    """Başarısız girişleri IP adreslerine göre gruplar."""

    grouped_logs = {}

    for log in logs:
        if log["event_type"] == "login_failed":
            ip = log["ip_address"]
            timestamp = datetime.fromisoformat(log["timestamp"])

            if ip not in grouped_logs:
                grouped_logs[ip] = []

            grouped_logs[ip].append(timestamp)

    return grouped_logs


def detect_brute_force(timestamps, threshold=5, window_seconds=60):
    """Belirli sürede çok sayıda başarısız giriş olup olmadığını kontrol eder."""

    timestamps = sorted(timestamps)

    for i in range(len(timestamps)):
        start_time = timestamps[i]
        count = 0

        for j in range(i, len(timestamps)):
            difference = timestamps[j] - start_time

            if difference.total_seconds() <= window_seconds:
                count += 1
            else:
                break

            if count >= threshold:
                return True

    return False


if __name__ == "__main__":
    test_logs = [
        {
            "ip_address": "203.0.113.25",
            "event_type": "login_failed",
            "timestamp": "2026-11-21T10:00:00"
        },
        {
            "ip_address": "203.0.113.25",
            "event_type": "login_failed",
            "timestamp": "2026-11-21T10:00:10"
        },
        {
            "ip_address": "192.0.2.50",
            "event_type": "login_failed",
            "timestamp": "2026-11-21T10:00:20"
        },
        {
            "ip_address": "203.0.113.25",
            "event_type": "login_failed",
            "timestamp": "2026-11-21T10:00:20"
        },
        {
            "ip_address": "203.0.113.25",
            "event_type": "login_failed",
            "timestamp": "2026-11-21T10:00:30"
        },
        {
            "ip_address": "203.0.113.25",
            "event_type": "login_failed",
            "timestamp": "2026-11-21T10:00:40"
        }
    ]

    grouped = group_failed_logins(test_logs)

    print("\nBrute-force detection results:")

    for ip, timestamps in grouped.items():
        detected = detect_brute_force(timestamps)

        print(ip, ":", detected)
