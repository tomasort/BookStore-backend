#!/bin/sh

set -e

echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# flask db init
flask db migrate || true
flask db upgrade 

# Populate the database with some teset data
flask api populate --source_path /data/output
flask auth add-user --username admin --password admin --admin

exec "$@"
