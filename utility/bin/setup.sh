#! /usr/bin/env bash

# Remove any existing PostgreSQL container named cdr forcefully.
docker rm -f cdr

# Example: configure PostgreSQL container
# Run a new PostgreSQL container with the specified environment variables and settings.
docker run --name cdr -e POSTGRES_PASSWORD=1234 -d --rm -p "5432:5432" -e PGDATA=/var/lib/postgresqlcdr/data/pgdata -v /docker/db:/var/lib/postgresqlcoffeeshoptandis/data postgres:alpine

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
RETRIES=10
until docker exec -i cdr pg_isready -U postgres || [ $RETRIES -eq 0 ]; do
  echo "Waiting for PostgreSQL server, $((RETRIES--)) remaining attempts..."
  sleep 2
done

# Exit if PostgreSQL did not start in time.
if [ $RETRIES -eq 0 ]; then
  echo "PostgreSQL did not start in time."
  exit 1
fi

echo "Creating the 'cdr' database..."
docker exec -i cdr psql -U postgres -c "CREATE DATABASE cdr;"
sleep 2
# Create new migrations for Django apps.
python manage.py makemigrations
echo "Setup complete: Created migrations."
sleep 2

# Apply the migrations to the database.
python manage.py migrate
echo "Setup complete: Applied migrations."
sleep 2

# Start the Django development server.
echo "Starting Django development server..."
python manage.py runserver