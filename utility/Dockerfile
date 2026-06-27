FROM python:3.13-slim AS builder

ENV PIP_NO_CACHE_DIR=1
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN python -m pip install --upgrade pip && python -m pip install "poetry==2.2.1"

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=builder /usr/local /usr/local
COPY . .

RUN chmod +x /app/utility/bin/entrypoint.sh && mkdir -p /app/logs /app/storage/static /app/storage/static_collected /app/storage/media && chown -R app:app /app

USER app

ENTRYPOINT ["/app/utility/bin/entrypoint.sh"]
