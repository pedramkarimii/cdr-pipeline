from apps.core import os_setting_elastic  # noqa
import json
from django.utils.dateparse import parse_datetime
from apps.cdr.models import Cdr
from django.utils import timezone
from apps.cdr.tasks.tasks_main import RabbitMQMain


class RabbitMQConsumer(RabbitMQMain):
    """
    This class is used for consuming messages from RabbitMQ queues, processing them into Call Detail Records (CDRs),
    and saving them to a database.
    """

    def connect(self):
        """Establish connection to RabbitMQ."""
        super().connect()
        for shard_id in range(self.shard_count):
            self.channel.basic_consume(queue=f"{self.queue_prefix}_{shard_id}",
                                       on_message_callback=self.process_message, auto_ack=False)

    def process_message(self, ch, method, properties, body):  # noqa
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

    def _parse_message(self, message):  # noqa
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

    def _save_cdr(self, cdr_data):  # noqa
        """
        Save the CDR data to the database.
        """
        Cdr.objects.create(**cdr_data)

    def start_consuming(self):
        """Start consuming messages."""
        try:
            self.channel.start_consuming()
            print("Consumer started consuming messages...")
        except KeyboardInterrupt:
            print("Consumer interrupted by user.")
        except Exception as e:
            print(f"Error while consuming: {e}")
        finally:
            self.close_connection()
