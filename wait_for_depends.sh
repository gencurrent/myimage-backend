#!/bin/sh

# Awaiting for the DataBase
while ! nc -z $DB_HOST $DB_PORT; do
    echo "Waiting for the DataBase to launch on $DB_HOST:$DB_PORT ..."
    sleep 0.5 # wait for 1/10 of the second before check again
done
echo "Postgres is launched"

# Awaiting for the Redis
while ! nc -z $REDIS_HOST $REDIS_PORT; do
    echo "Waiting for the Redis to launch on $REDIS_HOST:$REDIS_PORT ..."
    sleep 0.5 # wait for 1/10 of the second before check again
done
echo "Redis is launched"

echo "Running migration"
./manage.py migrate --noinput

echo "Running MyImage"
./manage.py runserver 0.0.0.0:8000