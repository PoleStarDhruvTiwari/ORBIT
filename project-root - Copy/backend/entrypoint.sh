#!/bin/sh

echo "Waiting for postgres..."

sleep 5

echo "Running schema.sql..."

psql $DATABASE_URL -f sql/schema.sql

echo "Running alter.sql..."

psql $DATABASE_URL -f sql/alter.sql

echo "Running seed.sql..."

psql $DATABASE_URL -f sql/seed.sql

echo "Starting FastAPI..."

uvicorn app.main:app --host 0.0.0.0 --port 8000