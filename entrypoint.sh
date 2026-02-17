#!/bin/sh

# Entrypoint Script für Django Container

set -e

echo "Starting da-coder backend..."

# Führe Datenbankmigrationen aus
echo "Running database migrations..."
python manage.py migrate --noinput

# Sammle static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Erstelle Superuser falls nicht vorhanden
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser if not exists..."
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser(
        username='$DJANGO_SUPERUSER_USERNAME',
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print("Superuser created successfully.")
else:
    print("Superuser already exists.")
EOF
else
    echo "Skipping superuser creation (environment variables not set)."
fi

echo "Starting application..."
exec "$@"