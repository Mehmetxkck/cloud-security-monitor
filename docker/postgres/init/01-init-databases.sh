#!/usr/bin/env bash

set -euo pipefail

APP_DB="${POSTGRES_DB}"
TEST_DB="${TEST_DB_NAME:-security_monitor_test}"
BENCHMARK_DB="${BENCHMARK_DB_NAME:-security_monitor_benchmark}"

SCHEMA_DIR="/docker-entrypoint-initdb.d/schemas"

if [[ -z "$APP_DB" || -z "$TEST_DB" || -z "$BENCHMARK_DB" ||
      "$APP_DB" == "$TEST_DB" ||
      "$APP_DB" == "$BENCHMARK_DB" ||
      "$TEST_DB" == "$BENCHMARK_DB" ]]; then
    echo "ERROR: Database names must be distinct and non-empty."
    exit 1
fi

echo "Initializing Cloud Security Monitor databases..."

createdb -U "$POSTGRES_USER" "$TEST_DB"
createdb -U "$POSTGRES_USER" "$BENCHMARK_DB"

echo "Applying application schema..."

psql -X -v ON_ERROR_STOP=1 --single-transaction \
    -U "$POSTGRES_USER" \
    -d "$APP_DB" \
    -f "$SCHEMA_DIR/app-schema.sql"

echo "Applying test schema..."

psql -X -v ON_ERROR_STOP=1 --single-transaction \
    -U "$POSTGRES_USER" \
    -d "$TEST_DB" \
    -f "$SCHEMA_DIR/test-schema.sql"

echo "Applying benchmark schema..."

psql -X -v ON_ERROR_STOP=1 --single-transaction \
    -U "$POSTGRES_USER" \
    -d "$BENCHMARK_DB" \
    -f "$SCHEMA_DIR/benchmark-schema.sql"

echo "Database initialization completed successfully."
