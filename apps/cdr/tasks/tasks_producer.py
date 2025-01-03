from apps.core import os_setting_elastic  # noqa
from apps.cdr.tasks.tasks_main import RabbitMQMain
import pika
import json
import time
import hashlib


class RabbitMQProducer(RabbitMQMain):
    """
    This class is responsible for producing and publishing messages to RabbitMQ queues.
     It calculates the shard (queue) to which the message will be published based on the source number (src_number).
    The class also includes retry logic that allows
     the producer to retry message publishing if it fails due to temporary issues.
    """

    def _get_shard_id(self, src_number):
        """Calculate shard ID based on src_number."""
        hash_value = int(hashlib.md5(src_number.encode()).hexdigest(), 16)
        return hash_value % self.shard_count

    def publish_message(self, message):
        """Publish a message to the appropriate shard queue with retry logic."""
        shard_id = self._get_shard_id(message['src_number'])
        queue_name = f"{self.queue_prefix}_{shard_id}"

        retries = 0
        while retries < self.max_retries:
            try:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2
                    )
                )
                print(f"Published message to {queue_name}: {message}")
                return

            except (pika.exceptions.AMQPConnectionError, pika.exceptions.AMQPChannelError) as e:
                print(f"Error publishing message to {queue_name}: {e}")
                retries += 1
                print(f"Retrying ({retries}/{self.max_retries}) after {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                self.retry_delay *= 2

        print(f"Failed to publish message after {self.max_retries} retries. Sending to DLX (if configured).")
