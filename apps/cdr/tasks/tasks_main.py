import logging
import random
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import pika
from decouple import config


logger = logging.getLogger(__name__)


class RabbitMQMain:
    def __init__(
        self,
        queue_prefix: str,
        shard_count: int,
        url: str | None = None,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        virtual_host: str | None = None,
        max_retries: int = 5,
        retry_delay: float = 2,
    ) -> None:
        self.queue_prefix = queue_prefix
        self.shard_count = shard_count
        self.url = url
        self.host = host or config("RABBITMQ_HOST", default="rabbitmq")
        self.port = port or config("RABBITMQ_PORT", cast=int, default=5672)
        self.username = username or config("RABBITMQ_USER", default="guest")
        self.password = password or config("RABBITMQ_PASSWORD", default="guest")
        self.virtual_host = (
            virtual_host
            if virtual_host is not None
            else config("RABBITMQ_VHOST", default="/")
        )
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection = None
        self.channel = None

    def _connection_parameters(self) -> pika.ConnectionParameters:
        if self.url:
            return pika.URLParameters(self.url)

        credentials = pika.PlainCredentials(self.username, self.password)
        return pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=credentials,
            heartbeat=60,
            blocked_connection_timeout=30,
        )

    def connect(self) -> bool:
        for attempt in range(1, self.max_retries + 1):
            try:
                self.connection = pika.BlockingConnection(self._connection_parameters())
                self.channel = self.connection.channel()
                self.channel.basic_qos(prefetch_count=1)

                for shard_id in range(self.shard_count):
                    self.channel.queue_declare(
                        queue=f"{self.queue_prefix}_{shard_id}",
                        durable=True,
                    )

                logger.info(
                    "Connected to RabbitMQ at %s:%s",
                    self.host,
                    self.port,
                )
                return True
            except pika.exceptions.AMQPConnectionError as exc:
                logger.warning(
                    "RabbitMQ connection attempt %s/%s failed: %s",
                    attempt,
                    self.max_retries,
                    exc,
                )
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)

        self.connection = None
        self.channel = None
        return False

    def close_connection(self) -> None:
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("RabbitMQ connection closed.")


def generate_cdr() -> dict[str, Any]:
    call_duration = random.randint(1, 3600)
    start_time = datetime.now(timezone.utc) - timedelta(
        seconds=random.randint(0, 30 * 24 * 60 * 60)
    )
    end_time = start_time + timedelta(seconds=call_duration)

    return {
        "src_number": f"0912{random.randint(1000000, 9999999)}",
        "dest_number": f"0912{random.randint(1000000, 9999999)}",
        "call_duration": call_duration,
        "call_successful": random.choice([True, False]),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "timestamp": end_time.isoformat(),
    }
