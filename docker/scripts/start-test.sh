#!/bin/sh

set -e

# flask db migrate || true
# flask db upgrade 

exec "$@"
