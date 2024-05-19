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



# # Start Celery worker and beat scheduler
# echo "Starting Celery worker..."
# celery -A celery worker --loglevel=info &

# echo "Starting Celery beat..."
# celery -A celery beat --loglevel=info &


# Start uWSGI server (proxy)
# uwsgi --socket :8001 --master --enable-threads --module app.wsgi:application --pythonpath /app/app
python app/manage.py runserver 0.0.0.0:8001