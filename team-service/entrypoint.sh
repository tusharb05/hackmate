#!/bin/sh

#!/bin/sh

# Only run migrations if RUN_MIGRATIONS is not set to "false"
if [ "$RUN_MIGRATIONS" != "false" ]; then
  echo "Applying database migrations..."
  python -u ./team_service/manage.py makemigrations
  python -u ./team_service/manage.py migrate
fi

# Execute the command passed to the container (e.g., runserver or a consumer script)
exec "$@"

# python -u ./team_service/manage.py makemigrations

# python -u ./team_service/manage.py migrate

# python -u ./team_service/manage.py runserver 0.0.0.0:8000