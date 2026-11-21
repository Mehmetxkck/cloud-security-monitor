
from datetime import datetime, timedelta

from app.services.detection_engine import detect_brute_force


def create_timestamps(seconds):
    """Verilen saniyelere göre test zamanları oluşturur."""

    start = datetime(2026, 11, 21, 10, 0, 0)

    timestamps = []

    for second in seconds:
        timestamp = start + timedelta(seconds=second)
        timestamps.append(timestamp)

    return timestamps


def test_brute_force_detected():
    timestamps = create_timestamps([0, 10, 20, 30, 40])

    result = detect_brute_force(timestamps)

    assert result is True


def test_brute_force_not_detected():
    timestamps = create_timestamps([0, 10, 20])

    result = detect_brute_force(timestamps)

    assert result is False


def test_attempts_outside_window():
    timestamps = create_timestamps([0, 70, 140, 210, 280])

    result = detect_brute_force(timestamps)

    assert result is False


def test_unsorted_timestamps():
    timestamps = create_timestamps([40, 0, 30, 10, 20])

    result = detect_brute_force(timestamps)

    assert result is True


def test_exact_window_boundary():
    timestamps = create_timestamps([0, 15, 30, 45, 60])

    result = detect_brute_force(timestamps)

    assert result is True
