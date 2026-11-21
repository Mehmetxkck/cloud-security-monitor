
import json


def load_logs(file_path):
    """JSON dosyasındaki log kayıtlarını okur."""
    with open(file_path, "r") as file:
        logs = json.load(file)

    return logs


def filter_failed_logs(logs):
    """Başarısız işlemleri filtreler."""
    failed_logs = []

    for log in logs:
        if log["status"] == "failed":
            failed_logs.append(log)

    return failed_logs


def count_failed_attempts(failed_logs):
    """IP adreslerine göre başarısız işlem sayılarını hesaplar."""
    failed_attempts = {}

    for log in failed_logs:
        ip = log["ip_address"]

        if ip in failed_attempts:
            failed_attempts[ip] += 1
        else:
            failed_attempts[ip] = 1

    return failed_attempts


# Programın başlangıç noktası
if __name__ == "__main__":
    logs = load_logs("data/sample_logs.json")

    failed_logs = filter_failed_logs(logs)

    results = count_failed_attempts(failed_logs)

    print("Failed attempts by IP:")

    for ip, count in results.items():
        print(ip, ":", count)
