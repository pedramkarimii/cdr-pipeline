from apps.core import os_setting_elastic
import pika
import json
from django.utils.dateparse import parse_datetime
from apps.cdr.models import Cdr
from django.utils import timezone


class RabbitMQConsumer:
    def __init__(self, queue_prefix, shard_count, host='localhost', port=5672, username='guest', password='guest'):
        """
        Initialize the RabbitMQConsumer with connection parameters and shard configuration.
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
            self.channel.basic_consume(queue=queue_name, on_message_callback=self.process_message, auto_ack=False)
        print(f"Connected to RabbitMQ at {self.host}:{self.port} and consuming messages...")

    def process_message(self, ch, method, properties, body):
        """
        This method will be called for each message consumed from the RabbitMQ queue.
        """
        try:
            message = json.loads(body)
            print(f"Received message: {message}")
            cdr_data = self._parse_message(message)
            self._save_cdr(cdr_data)

            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"Processed message: {cdr_data}")
        except Exception as e:
            print(f"Error processing message: {e}. Skipping message: {body}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def _parse_message(self, message):
        """
        This method parses the message and converts it into the CDR format.
        """
        timestamp = parse_datetime(message['timestamp'])
        timestamp = timezone.make_aware(timestamp, timezone.get_current_timezone())

        start_time = parse_datetime(message.get('start_time', message['timestamp']))
        start_time = timezone.make_aware(start_time, timezone.get_current_timezone())

        end_time = parse_datetime(message.get('end_time', message['timestamp']))
        end_time = timezone.make_aware(end_time, timezone.get_current_timezone())

        cdr_data = {
            'src_number': message['src_number'],
            'dest_number': message['dest_number'],
            'call_duration': message['call_duration'],
            'call_successful': message['call_successful'],
            'timestamp': timestamp,
            'start_time': start_time,
            'end_time': end_time,
        }
        return cdr_data

    def _save_cdr(self, cdr_data):
        """
        Save the CDR data to the database.
        """
        Cdr.objects.create(
            src_number=cdr_data['src_number'],
            dest_number=cdr_data['dest_number'],
            call_duration=cdr_data['call_duration'],
            call_successful=cdr_data['call_successful'],
            start_time=cdr_data['start_time'],
            end_time=cdr_data['end_time'],
            timestamp=cdr_data['timestamp']
        )

    def start_consuming(self):
        """Start consuming messages."""
        self.channel.start_consuming()

    def close_connection(self):
        """Close the RabbitMQ connection."""
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    consumer = RabbitMQConsumer(queue_prefix='cdr_queue', shard_count=4)
    consumer.connect()

    try:
        consumer.start_consuming()
    except KeyboardInterrupt:
        consumer.close_connection()
