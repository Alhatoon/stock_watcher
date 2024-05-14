#!/bin/sh

set -e

# Function to check if the Cassandra database is ready
wait_for_database() {
  echo "Waiting for Cassandra..."

  while ! cqlsh -e 'describe keyspaces;' > /dev/null 2>&1; do
    sleep 3
  done

  echo "Cassandra is ready."
}
# Wait for the Cassandra database to be ready
wait_for_database

# Run custom management commands
python manage.py setup_test_keyspace
python manage.py sync_cassandra_models

python manage.py collectstatic --noinput


# Start uWSGI server
uwsgi --socket :8000 --master --enable-threads --module app.wsgi 
