import pika
import json
import random
from datetime import datetime, timedelta
import time
import hashlib


class RabbitMQProducer:
    """RabbitMQProducer class handles the creation of a RabbitMQ connection, shard-based message routing,
     and message publishing."""

    def __init__(self, queue_prefix, shard_count, host='localhost', port=5672, username='guest', password='guest'):
        """
        Initialize the RabbitMQProducer with connection parameters and shard configuration.

        queue_prefix: The base name for the queues.
        shard_count: Number of shards (queues) to be created.
        host, port, username, password: RabbitMQ connection parameters.
        """
        self.queue_prefix = queue_prefix
        self.shard_count = shard_count
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish connection to RabbitMQ."""
        credentials = pika.PlainCredentials(self.username, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials)
        )
        self.channel = self.connection.channel()

        for shard_id in range(self.shard_count):
            queue_name = f"{self.queue_prefix}_{shard_id}"
            self.channel.queue_declare(queue=queue_name, durable=True)
        print(f"Connected to RabbitMQ at {self.host}:{self.port}")

    def _get_shard_id(self, src_number):
        """Calculate shard ID based on src_number."""
        hash_value = int(hashlib.md5(src_number.encode()).hexdigest(), 16)
        return hash_value % self.shard_count

    def publish_message(self, message):
        """Publish a message to the appropriate shard queue."""
        shard_id = self._get_shard_id(message['src_number'])
        queue_name = f"{self.queue_prefix}_{shard_id}"
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )
        print(f"Published message to {queue_name}: {message}")

    def close_connection(self):
        """Close the RabbitMQ connection."""
        if self.connection:
            self.connection.close()
            print("Connection closed.")


def generate_cdr():
    """Generate a random Call Detail Record (CDR)."""
    src_number = f"0912{random.randint(100000, 999999)}"
    dest_number = f"0912{random.randint(100000, 999999)}"
    call_duration = random.randint(1, 60000)
    call_successful = random.choice([True, False])
    start_time = (datetime.now() - timedelta(seconds=random.randint(0, 86400))).isoformat()
    end_time = (datetime.now() - timedelta(seconds=random.randint(0, 86400))).isoformat()
    timestamp = (datetime.now() - timedelta(seconds=random.randint(0, 86400))).isoformat()

    return {
        "src_number": src_number,
        "dest_number": dest_number,
        "call_duration": call_duration,
        "call_successful": call_successful,
        "start_time": start_time,
        "end_time": end_time,
        "timestamp": timestamp
    }


if __name__ == "__main__":
    """Initialize the producer with queue prefix 'cdr_queue' and 4 shards"""
    producer = RabbitMQProducer(queue_prefix='cdr_queue', shard_count=4)
    producer.connect()

    message_count = 0
    start_time = time.time()

    try:
        while True:
            for _ in range(500):
                cdr = generate_cdr()
                producer.publish_message(cdr)
                message_count += 1
                if message_count % 100 == 0:
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    print(f"Sent {message_count} messages. Time taken: {elapsed_time:.2f} seconds.")
                    time.sleep(0.22)
            break

    except KeyboardInterrupt:
        producer.close_connection()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Total messages sent: {message_count}, Time taken: {elapsed_time:.2f} seconds.")
