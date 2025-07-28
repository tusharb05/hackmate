#!/bin/sh

if [ "$RUN_MIGRATIONS" != "false" ]; then
  echo "Applying database migrations..."
  # CORRECT
  python -u notification_service/manage.py makemigrations
  python -u notification_service/manage.py migrate
fi

exec "$@"