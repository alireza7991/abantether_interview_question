#!/bin/bash

# Wait for the database to be ready
echo "Waiting for PostgreSQL to be ready..."
until nc -z -v -w30 "$DJANGO_DB_HOST" 5432; do
  echo "Waiting for PostgreSQL to start..."
  sleep 1
done
echo "PostgreSQL is up and running!"

echo "Running migrations..."
python manage.py migrate --noinput
if [ $? -ne 0 ]; then
    echo "Migration failed." >&2
    exit 1
fi
echo "Migrations done"

# If we have any args (e.g. running tests), run args,
# otherwise start the server

if [[ $# -gt 0 ]]; then
    INPUT=$@
    sh -c "$INPUT"
else
    echo "Starting application..."
    cd src
    exec gunicorn --bind 0.0.0.0:80 aban.asgi -k uvicorn.workers.UvicornWorker
fi