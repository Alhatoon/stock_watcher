#!/bin/sh
echo "Running entrypoint.sh..."
set -e

# Function to check if the Cassandra database is ready
# wait_for_database() {
#   echo "Waiting for Cassandra..."

#   while ! cqlsh -e 'describe keyspaces;' > /dev/null 2>&1; do
#     sleep 3
#   done

#   echo "Cassandra is ready."
# }
# # Wait for the Cassandra database to be ready
# wait_for_database

# Run custom management commands
echo "Running setup_test_keyspace..."
python app/manage.py setup_test_keyspace
echo "Finished running setup_test_keyspace."

echo "Running sync_cassandra_models..."
python app/manage.py sync_cassandra_models
echo "Finished running sync_cassandra_models."

#python app/manage.py collectstatic --noinput


# Start uWSGI server
uwsgi --socket :8001 --master --enable-threads --module app.wsgi:application --pythonpath /app/app
# uwsgi --module app.app.wsgi:application --socket :8001 --master --enable-threads
# uwsgi --module app.app.app.wsgi:application --socket :8001 --master --enable-threads --pythonpath /app/app
