
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DB_NAME = os.getenv("DB_NAME", "security_monitor")

TEST_DB_NAME = os.getenv(
    "TEST_DB_NAME",
    "security_monitor_test"
)

BENCHMARK_DB_NAME = os.getenv(
    "BENCHMARK_DB_NAME",
    "security_monitor_benchmark"
)

APP_ENV = os.getenv("APP_ENV", "development")
