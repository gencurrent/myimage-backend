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


USE_GUNICORN=true

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        -d | --debug)
            USE_GUNICORN=false
            ;;
        --environment)
            ENVIRONMENT=$VALUE
            ;;
        --db-path)
            DB_PATH=$VALUE
            ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done

echo "Running migration"
./manage.py migrate --noinput


echo "Starting MyImage"
if [ $USE_GUNICORN = true ]; then
    gunicorn 
    echo "Using gunicorn"
else
    echo "Not using gunicorn"
    ./manage.py runserver 0.0.0.0:8000
fi
