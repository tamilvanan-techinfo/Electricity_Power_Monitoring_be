#!/bin/sh

echo "Applying migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Creating superuser (if it doesn't exist)..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
email = "admin@example.com"
password = "Admin@123"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("Superuser created.")
else:
    print("Superuser already exists.")
EOF

echo "Starting Uvicorn..."
exec uvicorn electricity_monitoring_be.application:application \
    --lifespan=on \
    --host 0.0.0.0 \
    --port 8000