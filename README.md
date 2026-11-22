
# Cloud Security Monitoring Platform

A Python-based security monitoring platform that analyzes
authentication logs, detects brute-force attempts, and stores
security events in PostgreSQL.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- Psycopg 3
- Pytest
- Git & GitHub

## Features

- JSON log ingestion
- Log validation
- PostgreSQL log storage
- Failed login analysis
- IP-based grouping
- Brute-force detection
- Persistent security alerts
- REST API
- Automated testing

## Detection Rule

Detects 5 or more failed login attempts from the same IP
address within a 60-second window.

## Project Structure

```text
cloud-security-monitor/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── log_parser.py
│   ├── import_logs.py
│   └── services/
│       └── detection_engine.py
├── data/
│   └── sample_logs.json
├── tests/
│   ├── test_api.py
│   ├── test_detection.py
│   └── test_parser.py
├── requirements.txt
└── README.md
```

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Database

Requires a running PostgreSQL server.

Create the database:

```bash
createdb security_monitor
```

The `security_logs` and `security_alerts` tables must be
created before running the application.

## Run

```bash
python -m uvicorn app.main:app --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | API status |
| GET | /health | Health check |
| GET | /logs | Retrieve logs from PostgreSQL |
| GET | /logs/failed | Failed login statistics |
| GET | /security/alerts | Detect and retrieve security alerts |

## Tests

```bash
python -m pytest -v
```

Current verified test results:

- 10 passed
- 0 failed

## Roadmap

- Stronger log validation
- Duplicate log prevention
- Database integration tests
- Pagination and filtering
- Background security detection
- Docker deployment
- Cloud deployment
