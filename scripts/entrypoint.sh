#!/bin/sh
echo "Running entrypoint.sh..."
set -e

# Adjust the path if necessary
if [ -f "/app/manage.py" ]; then
    MANAGE_PY_PATH="/app/manage.py"
else
    echo "Error: manage.py not found in /app"
    exit 1
fi

# Run custom management commands
echo "Running setup_test_keyspace..."
python $MANAGE_PY_PATH setup_test_keyspace
echo "Finished running setup_test_keyspace."

echo "Running sync_cassandra_models..."
python $MANAGE_PY_PATH sync_cassandra_models
echo "Finished running sync_cassandra_models."




# # Start Celery worker and beat scheduler
# echo "Starting Celery worker..."
# celery -A celery worker --loglevel=info &

# echo "Starting Celery beat..."
# celery -A celery beat --loglevel=info &


# Start uWSGI server (proxy)
# uwsgi --socket :8001 --master --enable-threads --module app.wsgi:application --pythonpath /app/app
python $MANAGE_PY_PATH runserver 0.0.0.0:8001