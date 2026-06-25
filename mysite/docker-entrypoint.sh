#!/bin/sh

echo "Очікування PostgreSQL..."
while ! python -c "
import psycopg2, os
psycopg2.connect(
    host=os.environ['POSTGRES_HOST'],
    port=os.environ['POSTGRES_PORT'],
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
)
" 2>/dev/null; do
    sleep 2
done
echo "PostgreSQL готовий!"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "Запуск сервера..."
exec python manage.py runserver 0.0.0.0:8000