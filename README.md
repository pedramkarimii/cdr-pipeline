# CDR Pipeline

Dockerized backend pipeline for ingesting, processing, storing, and querying Call Detail Records (CDRs).

The project combines Django, PostgreSQL, RabbitMQ, Redis, Elasticsearch, and Nginx in a reproducible Compose stack. Generated CDR messages are routed through durable RabbitMQ queues, validated by a consumer, stored in PostgreSQL, and made available through a JWT-protected API.

## Architecture

```text
CDR producer
    |
    v
RabbitMQ durable queues
    |
    v
CDR consumer ---> PostgreSQL ---> Elasticsearch
                                 ^
                                |
Client ---> Nginx ---> Django API
                    |
                    +--> Redis cache
```

## Highlights

- Durable RabbitMQ publishing with deterministic queue sharding.
- CDR validation and indexed PostgreSQL persistence.
- Elasticsearch-backed search, statistics, and synchronization checks.
- JWT authentication for API endpoints.
- Health checks for PostgreSQL, Redis, RabbitMQ, Elasticsearch, Django, and Nginx.
- Non-root Django container with environment-based configuration.
- GitHub Actions integration CI.

## Stack

- Python 3.12+
- Django and Django REST Framework
- PostgreSQL
- RabbitMQ and Pika
- Redis
- Elasticsearch
- Docker Compose and Nginx

## Quick start

```bash
git clone https://github.com/pedramkarimii/cdr-pipeline.git
cd cdr-pipeline

cp .env.example .env
docker compose up -d --build --wait

curl http://127.0.0.1:8082/health/
```

Expected response:

```json
{"status": "ok"}
```

Stop the stack:

```bash
docker compose down
```

Remove the stack and local service data:

```bash
docker compose down -v
```

## Configuration

Create a local environment file from the template:

```bash
cp .env.example .env
```

The example values are for local development only. Use strong, unique secrets and credentials in every other environment.

## API authentication

Create an administrative user:

```bash
docker compose exec application python manage.py createsuperuser
```

Obtain access and refresh tokens:

```bash
curl -X POST http://127.0.0.1:8082/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'
```

Use the access token with protected endpoints:

```bash
curl http://127.0.0.1:8082/api/cdr/stats/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health/` | Public service health check |
| `POST` | `/api/auth/token/` | Obtain JWT access and refresh tokens |
| `POST` | `/api/auth/token/refresh/` | Refresh an access token |
| `GET` | `/api/cdr/search/` | Search indexed CDRs |
| `GET` | `/api/cdr/stats/` | Retrieve CDR statistics |
| `GET` | `/api/cdr/sync-status/` | Compare PostgreSQL and Elasticsearch state |

## Producing and consuming CDRs

Publish generated records:

```bash
docker compose exec application \
  python manage.py create_producer --num-messages 100
```

Run a consumer for two shards:

```bash
docker compose exec application \
  python manage.py create_consumer --shard-count 2
```

The consumer runs until interrupted with `Ctrl+C`.

## Validation

Run the test suite:

```bash
docker compose exec application python manage.py test -v 0
```

Check for migration drift:

```bash
docker compose exec application \
  python manage.py makemigrations --check --dry-run
```

Validate the Compose configuration:

```bash
docker compose config --quiet
```

## CI

GitHub Actions runs for pull requests targeting `develop` and pushes to `develop`. It validates Compose, starts the full stack, runs Django checks and migration validation, executes tests, verifies the health endpoint, and always removes services and volumes.

## License

Licensed under the MIT License. See [LICENSE](LICENSE).
