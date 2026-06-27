import hashlib
import json
import logging
import time

import pika

from apps.cdr.tasks.tasks_main import RabbitMQMain


logger = logging.getLogger(__name__)


class RabbitMQProducer(RabbitMQMain):
    def _get_shard_id(self, src_number: str) -> int:
        digest = hashlib.md5(src_number.encode("utf-8")).hexdigest()
        return int(digest, 16) % self.shard_count

    def publish_message(self, message: dict) -> bool:
        if self.channel is None:
            raise RuntimeError("RabbitMQ channel is not connected.")

        shard_id = self._get_shard_id(message["src_number"])
        queue_name = f"{self.queue_prefix}_{shard_id}"

        for attempt in range(1, self.max_retries + 1):
            try:
                self.channel.basic_publish(
                    exchange="",
                    routing_key=queue_name,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                logger.info("Published CDR to %s", queue_name)
                return True
            except (
                pika.exceptions.AMQPConnectionError,
                pika.exceptions.AMQPChannelError,
            ) as exc:
                logger.warning(
                    "Publish attempt %s/%s to %s failed: %s",
                    attempt,
                    self.max_retries,
                    queue_name,
                    exc,
                )
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)

        return False
