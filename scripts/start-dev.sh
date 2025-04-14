#!/bin/sh

set -e

# flask db init
flask db migrate || true
flask db upgrade 

# Populate the database with some teset data
flask api populate --source_path /data/output
flask auth add-user --username admin --password admin --admin

exec "$@"
