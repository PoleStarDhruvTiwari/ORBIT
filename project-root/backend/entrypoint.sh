#!/bin/sh
set -e

echo "Waiting for postgres..."
sleep 5

# psql cannot parse the SQLAlchemy-style "+asyncpg" driver suffix.
PSQL_URL=$(echo "$DATABASE_URL" | sed 's#+asyncpg##')

# Order matters:
#   1) schema.sql -> creates tables (no FKs)
#   2) seed.sql   -> populates rows (no FKs to fight)
#   3) alter.sql  -> adds all FKs + indexes
echo "Running schema.sql..."
psql "$PSQL_URL" -v ON_ERROR_STOP=1 -f sql/schema.sql

echo "Running seed.sql..."
psql "$PSQL_URL" -v ON_ERROR_STOP=1 -f sql/seed.sql

echo "Running alter.sql..."
psql "$PSQL_URL" -v ON_ERROR_STOP=1 -f sql/alter.sql

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
